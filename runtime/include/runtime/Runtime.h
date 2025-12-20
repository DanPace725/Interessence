#pragma once

#include "Types.h"
#include <functional>
#include <string>
#include <vector>

namespace interessence {

// Simple tick interface; expand as systems are implemented.
class Runtime {
public:
    explicit Runtime(RuntimeBundle bundle);

    // Execute one tick of the RPE pipeline.
    void Tick();

    // Accessors for inspection / integration
    const std::vector<Entity>& GetEntities() const { return m_entities; }
    const std::vector<Relation>& GetRelations() const { return m_relations; }
    const RuntimeConfig& GetConfig() const { return m_config; }
    const HeuristicsConfig& GetHeuristics() const { return m_heuristics; }
    const SignalConfig& GetSignal() const { return m_signal; }

private:
    std::vector<Entity> m_entities;
    std::vector<Relation> m_relations;
    RuntimeConfig m_config;
    HeuristicsConfig m_heuristics;
    SignalConfig m_signal;

    // Rule biases cached into a map rule->weight
    std::unordered_map<std::string, double> m_ruleBiasMap;

    // Phase stubs
    void PhaseGeometry();
    void PhaseConstraint();
    void PhaseEpistemic();
    void PhaseDynamics();
    void PhaseMeta();
    void PhaseGCO();

    void ApplyRuleBiases();
    void ApplyGcoThresholds();

    // Utility: spawn child entity (defined in PhaseDynamics logic)
};

} // namespace interessence
