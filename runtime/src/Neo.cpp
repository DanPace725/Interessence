#include "runtime/Neo.h"
#include <algorithm>
#include <cmath>
#include <iostream>

namespace interessence {

// Internal constants matching Python implementation
static const float INTERACTION_MATRIX[5][5] = {
    // Right(0), Left(1), Cross(2), Diagonal(3), Backslash(4)

    // Right (0)
    {2.0f, -1.5f, 0.5f, 0.5f, 0.5f},
    // Left (1)
    {-1.5f, 2.0f, 0.5f, 0.5f, 0.5f},
    // Cross (2)
    {0.5f, 0.5f, 3.0f, 4.0f, 5.0f},
    // Diagonal (3)
    {0.5f, 0.5f, 4.0f, 1.5f, 3.5f},
    // Backslash (4)
    {0.5f, 0.5f, 5.0f, 3.5f, 6.0f}};

// Note: Python dict had tuples like ('left', 'right'): -1.5.
// And ('right', 'left'): -1.5.
// My matrix above assumes indices:
// Right=0, Left=1, Cross=2, Diagonal=3, Backslash=4.
// Let's verify:
// (Left, Right) -> (1, 0) = -1.5. Correct.
// (Cross, Cross) -> (2, 2) = 3.0. Correct.
// (Cross, Diagonal) -> (2, 3) = 4.0. Correct.
// (Cross, Backslash) -> (2, 4) = 5.0. Correct.
// (Diagonal, Diagonal) -> (3, 3) = 1.5. Correct.
// (Diagonal, Backslash) -> (3, 4) = 3.5. Correct.
// (Backslash, Backslash) -> (4, 4) = 6.0. Correct.
// All others 0.5 default.

NeoGlyphProps Neo::GetGlyphProps(uint32_t inscriptionSeed, int x, int y) {
  // Python arithmetic emulation
  // Python: h = (x * 374761393 ^ y * 668265263 ^ inscription_seed)
  // We use int64_t to accommodate negative x/y and larger results, matching
  // Python's signed behavior for small ranges.

  int64_t h = (int64_t(x) * 374761393LL) ^ (int64_t(y) * 668265263LL) ^
              int64_t(inscriptionSeed);

  // Python: type = h % 5
  // C++ % can return negative. Python % always returns positive [0, 4].
  int typeIndex = (int)(h % 5);
  if (typeIndex < 0)
    typeIndex += 5;

  NeoGlyphType type;
  switch (typeIndex) {
  case 0:
    type = NeoGlyphType::Left;
    break;
  case 1:
    type = NeoGlyphType::Right;
    break;
  case 2:
    type = NeoGlyphType::Cross;
    break;
  case 3:
    type = NeoGlyphType::Diagonal;
    break;
  case 4:
    type = NeoGlyphType::Backslash;
    break;
  default:
    type = NeoGlyphType::Unknown;
    break; // Should not happen
  }

  // Python: mag = ((h >> 8) % 5) + 1
  // Python >> 8 on negative numbers: -1 >> 8 = -1. -256 >> 8 = -1.
  // C++: Implementation defined for signed right shift, but usually arithmetic
  // (preserves sign). Let's assume arithmetic shift.
  int64_t shifted = h >> 8;
  int magIndex = (int)(shifted % 5);
  if (magIndex < 0)
    magIndex += 5;

  int mag = magIndex + 1;

  return {type, mag};
}

float Neo::CalculateLocalIntensity(uint32_t seed, int x, int y) {
  std::vector<NeoGlyphProps> neighbors;
  neighbors.reserve(9);

  for (int dy = -1; dy <= 1; ++dy) {
    for (int dx = -1; dx <= 1; ++dx) {
      neighbors.push_back(GetGlyphProps(seed, x + dx, y + dy));
    }
  }

  float score = 0.0f;
  int count = 0;

  for (size_t i = 0; i < neighbors.size(); ++i) {
    for (size_t j = i + 1; j < neighbors.size(); ++j) {
      NeoGlyphProps p1 = neighbors[i];
      NeoGlyphProps p2 = neighbors[j];

      // Base interaction
      // Map Enum to Matrix Index
      // Matrix: Right(0), Left(1), Cross(2), Diagonal(3), Backslash(4)

      auto TypeToIndex = [](NeoGlyphType t) -> int {
        switch (t) {
        case NeoGlyphType::Right:
          return 0;
        case NeoGlyphType::Left:
          return 1;
        case NeoGlyphType::Cross:
          return 2;
        case NeoGlyphType::Diagonal:
          return 3;
        case NeoGlyphType::Backslash:
          return 4;
        default:
          return 0;
        }
      };

      int idx1 = TypeToIndex(p1.type);
      int idx2 = TypeToIndex(p2.type);

      // Interaction is symmetric in our matrix?
      // (Right, Left) -> (0, 1) -> -1.5
      // (Left, Right) -> (1, 0) -> -1.5.
      // Yes.
      float base = INTERACTION_MATRIX[idx1][idx2];

      // Magnitude Modulation
      float delta = std::abs((float)p1.magnitude - (float)p2.magnitude);

      score += base + (delta * 0.25f);
      count++;
    }
  }

  if (count == 0)
    return 0.0f;
  return score / (float)count;
}

std::vector<float> Neo::GenerateField(uint32_t seed, int width, int height,
                                      bool normalize) {
  std::vector<float> field(width * height);

  for (int y = 0; y < height; ++y) {
    for (int x = 0; x < width; ++x) {
      field[y * width + x] = CalculateLocalIntensity(seed, x, y);
    }
  }

  if (normalize) {
    float minVal = -1.5f;
    float maxVal = 7.5f;

    for (float &val : field) {
      val = (val - minVal) / (maxVal - minVal);
      // Clamp
      if (val < 0.0f)
        val = 0.0f;
      if (val > 1.0f)
        val = 1.0f;
    }
  }

  return field;
}

uint32_t Neo::HashString(const std::string &input) {
  // DJB2 Hash
  uint32_t hash = 5381;
  for (char c : input) {
    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
  }
  return hash;
}

} // namespace interessence
