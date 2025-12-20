#pragma once

#include <cstdint>
#include <map>
#include <string>
#include <vector>


namespace interessence {

// Enum matching the Python keys
enum class NeoGlyphType {
  Right,     // B-Group
  Left,      // H-Group
  Cross,     // M-Group
  Diagonal,  // A-Group
  Backslash, // Forfeda
  Unknown
};

struct NeoGlyphProps {
  NeoGlyphType type;
  int magnitude;
};

// Core Noise / Neo Logic
class Neo {
public:
  // Core functions matching neo_noise_core.py
  static NeoGlyphProps GetGlyphProps(uint32_t inscriptionSeed, int x, int y);
  static float CalculateLocalIntensity(uint32_t seed, int x, int y);

  // Generate a 2D field.
  // Returns a flat vector (row-major) of floats [0.0, 1.0]
  static std::vector<float> GenerateField(uint32_t seed, int width, int height,
                                          bool normalize = true);

  // Helper to hash string to seed
  static uint32_t HashString(const std::string &input);

  // Data structures matching Python dictionaries
  static const std::map<NeoGlyphType, std::string> TypeNames;
};

} // namespace interessence
