#include "runtime/Loader.h"
#include "runtime/Neo.h"
#include "runtime/Runtime.h"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>

using namespace interessence;

static std::string Slurp(const std::string &path) {
  std::ifstream ifs(path);
  if (!ifs)
    throw std::runtime_error("Failed to open file: " + path);
  std::stringstream buffer;
  buffer << ifs.rdbuf();
  return buffer.str();
}

int main(int argc, char **argv) {
  // Neo Verification Mode
  // If no arguments or strict flag, run verification
  bool runVerification = (argc < 2);

  if (runVerification) {
    std::cout << "Running Neo Verification..." << std::endl;
    uint32_t seed = 42069;
    int width = 5;
    int height = 5;

    std::cout << "Generating Neo Field with Int Seed: " << seed << "\n";
    std::cout << "Dimensions: " << width << "x" << height << "\n";

    // Generate normalized
    std::vector<float> field = Neo::GenerateField(seed, width, height, true);

    std::cout << "\n--- Generated Values (Row Major) ---\n";
    std::cout << std::fixed << std::setprecision(6);

    for (int y = 0; y < height; ++y) {
      for (int x = 0; x < width; ++x) {
        std::cout << field[y * width + x] << " ";
      }
      std::cout << "\n";
    }

    std::cout << "\n--- Verification Instructions ---\n";
    std::cout << "Compare the above block with Python output from "
                 "`neo_verification_gen.py`.\n";
    std::cout << "Expected first row: 0.496914 0.408951 ...\n";

    return 0;
  }

  // Original Demo Logic
  try {
    if (argc < 4) {
      std::cout << "Usage: demo <world-pack.json> <heuristics-pack.json> "
                   "<signal-pack.json>\n";
      return 0;
    }
    const std::string world = Slurp(argv[1]);
    const std::string heur = Slurp(argv[2]);
    const std::string sig = Slurp(argv[3]);

    auto res = LoadPacksFromStrings(world, heur, sig);
    if (!res.ok || !res.bundle.has_value()) {
      std::cerr << "Failed to load packs:\n";
      for (const auto &e : res.errors)
        std::cerr << "  - " << e << "\n";
      return 1;
    }

    Runtime runtime(std::move(res.bundle.value()));
    std::cout << "Loaded entities: " << runtime.GetEntities().size() << "\n";
    std::cout << "Loaded relations: " << runtime.GetRelations().size() << "\n";

    for (int i = 0; i < 5; ++i) {
      runtime.Tick();
      std::cout << "Tick " << i + 1 << " complete.\n";
    }

    return 0;
  } catch (const std::exception &ex) {
    std::cerr << "Exception: " << ex.what() << "\n";
    return 1;
  }
}
