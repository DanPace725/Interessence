#pragma once

#include <optional>
#include <string>
#include <unordered_map>
#include <variant>
#include <vector>

namespace interessence {

enum class Primitive {
    ONTOLOGY,
    GEOMETRY,
    CONSTRAINT,
    EPISTEMIC,
    DYNAMICS,
    META
};

struct Vec3 {
    double x{0.0};
    double y{0.0};
    double z{0.0};
};

struct RPFingerprint {
    double P1_identity{0.5};
    double P2_dynamics{0.5};
    double P3_geometry{0.5};
    double P4_constraints{0.5};
    double P5_epistemic{0.5};
    double P6_meta{0.5};
};

using Value = std::variant<double, bool, std::string>;
using StateMap = std::unordered_map<std::string, Value>;

struct Entity {
    std::string id;
    std::string kind;
    std::string label;
    Vec3 position{};
    RPFingerprint rp{};
    StateMap state;
};

struct Relation {
    std::string id;
    Primitive primitive{Primitive::ONTOLOGY};
    std::string source;
    std::string target;
    double weight{1.0};
    std::optional<std::string> payloadRaw; // payload as raw JSON string for now
};

struct RuntimeConfig {
    std::unordered_map<std::string, bool> toggles;
    std::unordered_map<std::string, double> geometry;
    std::unordered_map<std::string, Value> constraints;
    std::unordered_map<std::string, double> ecology;
    std::unordered_map<std::string, double> reproduction;
};

struct HeuristicsConfig {
    std::unordered_map<std::string, Value> parameters;
};

struct SignalConfig {
    std::unordered_map<std::string, Value> field;
    std::vector<std::unordered_map<std::string, Value>> compute;

    struct RuleBias {
        std::string rule;
        std::string metric;
        double weight{0.0};
    };
    struct GcoThreshold {
        std::string target;
        std::string metric;
        double threshold{0.0};
    };
    struct AgentObservationFeed {
        std::string scope; // agent|faction|global (currently only agent used)
        std::string metric;
        std::string key;
    };
    struct SteeringFeed {
        std::string metric;
        double weight{0.0};
    };

    std::vector<RuleBias> ruleBiases;
    std::vector<GcoThreshold> gcoThresholds;
    std::vector<AgentObservationFeed> agentObservations;
    std::vector<SteeringFeed> steeringFeeds;

    std::unordered_map<std::string, Value> participation;
};

struct RuntimeBundle {
    std::vector<Entity> entities;
    std::vector<Relation> relations;
    RuntimeConfig config;
    HeuristicsConfig heuristics;
    SignalConfig signal;
};

} // namespace interessence
