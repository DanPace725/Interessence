#pragma once

#include "Types.h"
#include <optional>
#include <string>
#include <vector>

namespace interessence {

struct LoadResult {
    bool ok{false};
    std::vector<std::string> errors;
    std::optional<RuntimeBundle> bundle;
};

// Parse and normalize packs provided as JSON strings.
LoadResult LoadPacksFromStrings(const std::string& worldJson,
                                const std::string& heuristicsJson,
                                const std::string& signalJson);

// Convenience: load from file paths (implemented only if JSON parsing is enabled).
LoadResult LoadPacksFromFiles(const std::string& worldPath,
                              const std::string& heuristicsPath,
                              const std::string& signalPath);

} // namespace interessence
