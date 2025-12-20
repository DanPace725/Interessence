#include "runtime/Loader.h"
#include "runtime/Neo.h"
#include "runtime/Runtime.h"
#include <algorithm>
#include <filesystem>
#include <iostream>
#include <raylib.h>
#include <raymath.h>
#include <string>
#include <vector>

using namespace interessence;

// Helper to resolve asset paths
static std::string ResolveSample(const std::string &name) {
  std::filesystem::path base = std::filesystem::current_path();
  std::filesystem::path rel =
      base / "tools" / "authoring" / "public" / "samples" / name;
  if (std::filesystem::exists(rel))
    return rel.string();
  if (std::filesystem::exists(name))
    return name;
  return name;
}

// Helper to create a Raylib Image from Neo Noise
static Image GenerateNeoImage(uint32_t seed, int width, int height) {
  std::vector<float> field = Neo::GenerateField(seed, width, height, true);

  // Convert to RGBA pixels (Grayscale)
  // Raylib expects array of Color (struct {r,g,b,a}) for simpler handling,
  // or we can just alloc raw bytes. Let's use raw bytes for LoadImageEx:
  // R8G8B8A8
  int dataSize = width * height * 4;
  unsigned char *pixels = (unsigned char *)RL_MALLOC(dataSize);

  for (int i = 0; i < width * height; ++i) {
    float val = field[i];
    unsigned char byteVal = static_cast<unsigned char>(val * 255.0f);

    pixels[i * 4 + 0] = byteVal; // R
    pixels[i * 4 + 1] = byteVal; // G
    pixels[i * 4 + 2] = byteVal; // B
    pixels[i * 4 + 3] = 255;     // A
  }

  Image image;
  image.data = pixels;
  image.width = width;
  image.height = height;
  image.mipmaps = 1;
  image.format = PIXELFORMAT_UNCOMPRESSED_R8G8B8A8;

  return image;
}

int main(int argc, char **argv) {
  // 1. Load Runtime
  std::string worldPath, heurPath, sigPath;
  if (argc >= 4) {
    worldPath = argv[1];
    heurPath = argv[2];
    sigPath = argv[3];
  } else {
    worldPath = ResolveSample("forest-world-pack.json");
    heurPath = ResolveSample("forest-heuristics-pack.json");
    sigPath = ResolveSample("forest-signal-pack.json");
  }

  auto res = LoadPacksFromFiles(worldPath, heurPath, sigPath);
  if (!res.ok || !res.bundle.has_value()) {
    std::cerr << "Failed to load packs:\n";
    for (const auto &e : res.errors)
      std::cerr << "  - " << e << "\n";
    return 1;
  }

  Runtime runtime(std::move(res.bundle.value()));

  // 2. Initialize Window and 3D Camera
  const int screenWidth = 1200;
  const int screenHeight = 800;
  InitWindow(screenWidth, screenHeight, "Interessence 3D Neo Prototype");

  // Define the camera to look into our 3D world
  Camera3D camera = {0};
  camera.position = Vector3{0.0f, 150.0f, 150.0f}; // Camera position
  camera.target = Vector3{0.0f, 0.0f, 0.0f};       // Camera looking at point
  camera.up =
      Vector3{0.0f, 1.0f, 0.0f}; // Camera up vector (rotation towards target)
  camera.fovy = 45.0f;           // Camera field-of-view Y
  camera.projection = CAMERA_PERSPECTIVE; // Camera projection type

  SetTargetFPS(60);

  // 3. Generate Neo Terrain
  // We create a heightmap model.
  // World size is roughly -500 to 500.
  // Let's generate a 128x128 grid and scale it up.
  int neoW = 128;
  int neoH = 128;
  Image heightMapImage = GenerateNeoImage(42069, neoW, neoH);

  // Generate mesh from heightmap
  Mesh mesh =
      GenMeshHeightmap(heightMapImage, Vector3{1000.0f, 50.0f, 1000.0f});
  // Size: 1000x1000 units, 50 units high

  Model model = LoadModelFromMesh(mesh);

  // Texture for the terrain
  // Just white for now so lights work, or use the noise image itself
  Image textureImage = ImageCopy(heightMapImage);
  // Maybe colorize it?
  ImageColorTint(&textureImage, GREEN);
  Texture2D texture = LoadTextureFromImage(textureImage);
  model.materials[0].maps[MATERIAL_MAP_DIFFUSE].texture = texture;

  UnloadImage(heightMapImage);
  UnloadImage(textureImage);

  // Position the ground so (0,0,0) is center.
  // GenMeshHeightmap creates mesh starting at (0,0,0) extending to (size.x,
  // size.y, size.z). We need to shift it by -size/2. Actually, Raylib meshes
  // usually pivot at center? No, usually corner. Let's verify by drawing axis.
  // Assuming corner (0,0) to (1000, 1000). So we translate by (-500, 0, -500).
  Vector3 mapPosition = {-500.0f, 0.0f, -500.0f};

  bool running = true;

  // Neo Height Sampling Function
  // We need the raw data again if we want to snap entities to ground accurately
  // without GPU readback. Or we can just regen it.
  std::vector<float> neoField = Neo::GenerateField(42069, neoW, neoH, true);
  auto GetTerrainHeight = [&](float worldX, float worldZ) -> float {
    // Transform world coord to [0,1]
    // World: -500 to 500
    float u = (worldX + 500.0f) / 1000.0f;
    float v = (worldZ + 500.0f) / 1000.0f;

    // Clamp
    if (u < 0)
      u = 0;
    if (u > 1)
      u = 1;
    if (v < 0)
      v = 0;
    if (v > 1)
      v = 1;

    // Map to grid
    int x = (int)(u * (neoW - 1));
    int y = (int)(v * (neoH - 1)); // Z corresponds to image Y usually

    float val = neoField[y * neoW + x];
    return val * 50.0f; // Scale by height factor
  };

  while (!WindowShouldClose()) {
    // Input
    if (IsKeyPressed(KEY_SPACE))
      running = !running;

    // Camera Free Control (WASD + Mouse)
    UpdateCamera(&camera, CAMERA_FREE);

    // Sim Step
    if (running) {
      runtime.Tick();
    }

    BeginDrawing();
    ClearBackground(Color{20, 20, 30, 255});

    BeginMode3D(camera);

    // Draw Ground
    DrawModel(model, mapPosition, 1.0f, WHITE);

    // Draw Grid Helper
    DrawGrid(20, 50.0f); // 20 slices, spacing 50

    // Draw Entities
    for (const auto &e : runtime.GetEntities()) {
      // Sim is 2D: X, Y.
      // 3D: X -> X, Y -> Z.
      float wx = static_cast<float>(e.position.x);
      float wz = static_cast<float>(e.position.y); // Sim Y is 3D Z

      float wy = GetTerrainHeight(wx, wz);

      Vector3 pos = {wx, wy + 2.0f, wz}; // Slightly above ground

      Color c = BLUE;
      if (e.kind == "resource") {
        c = GREEN;
        DrawCube(pos, 2.0f, 2.0f, 2.0f, c);
      } else {
        c = RED;
        DrawSphere(pos, 3.0f, c);

        // Optional: Draw stats as floating bar?
        // Too complex for now, just spheres.
      }
    }

    EndMode3D();

    // UI
    DrawFPS(10, 10);
    DrawText("Interessence 3D Proto", 10, 30, 20, WHITE);
    DrawText("Controls: WASD=Move, Mouse=Look, Space=Pause", 10, 50, 16, GRAY);

    char buf[64];
    snprintf(buf, sizeof(buf), "Entities: %zu", runtime.GetEntities().size());
    DrawText(buf, 10, 70, 16, GRAY);

    EndDrawing();
  }

  // Cleanup
  UnloadTexture(texture);
  UnloadModel(model);
  CloseWindow();

  return 0;
}
