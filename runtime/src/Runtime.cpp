#include "runtime/Runtime.h"
#include <algorithm>
#include <cmath>
#include <optional>
#include <string_view>
#include <unordered_set>
#include <random>
#include <limits>

namespace interessence {

namespace {
double GetNumber(const std::unordered_map<std::string, Value>& state, std::string_view key, double fallback = 0.0) {
    auto it = state.find(std::string(key));
    if (it == state.end()) return fallback;
    if (auto p = std::get_if<double>(&it->second)) return *p;
    if (auto b = std::get_if<bool>(&it->second)) return *b ? 1.0 : 0.0;
    return fallback;
}

void SetNumber(std::unordered_map<std::string, Value>& state, const std::string& key, double v) {
    state[key] = v;
}

double distance2(const Vec3& a, const Vec3& b) {
    const double dx = a.x - b.x;
    const double dy = a.y - b.y;
    const double dz = a.z - b.z;
    return dx * dx + dy * dy + dz * dz;
}

bool GetBool(const std::unordered_map<std::string, Value>& state, std::string_view key, bool fallback = false) {
    auto it = state.find(std::string(key));
    if (it == state.end()) return fallback;
    if (auto b = std::get_if<bool>(&it->second)) return *b;
    if (auto d = std::get_if<double>(&it->second)) return *d != 0.0;
    return fallback;
}
double SampleMetric(const Entity& e, std::string_view metric) {
    if (metric == "visibleResources") return GetNumber(e.state, "visibleResources", 0.0);
    if (metric == "nearestResourceDist2") {
        double d2 = GetNumber(e.state, "nearestResourceDist2", std::numeric_limits<double>::infinity());
        if (std::isinf(d2)) return 0.0;
        return 1.0 / (1.0 + d2); // convert distance to a [0,1) proximity score
    }
    // fallback: direct state lookup
    return GetNumber(e.state, std::string(metric), 0.0);
}

static std::mt19937& rng() {
    static thread_local std::mt19937 gen(1234567u);
    return gen;
}
double rand01() {
    static thread_local std::uniform_real_distribution<double> dist(0.0, 1.0);
    return dist(rng());
}
double randRange(double a, double b) {
    return a + (b - a) * rand01();
}
} // namespace

Runtime::Runtime(RuntimeBundle bundle)
    : m_entities(std::move(bundle.entities)),
      m_relations(std::move(bundle.relations)),
      m_config(std::move(bundle.config)),
      m_heuristics(std::move(bundle.heuristics)),
      m_signal(std::move(bundle.signal)) {
    ApplyRuleBiases();
}

void Runtime::Tick() {
    PhaseGeometry();
    PhaseConstraint();
    PhaseEpistemic();
    PhaseDynamics();
    PhaseMeta();
    PhaseGCO();
}

void Runtime::PhaseGeometry() {
    // Simple proximity: count neighbors within wallAvoidMargin (if present)
    const double neighborR2 = [&]() {
        auto it = m_config.geometry.find("wallAvoidMargin");
        return (it != m_config.geometry.end()) ? it->second * it->second : 100.0 * 100.0;
    }();
    for (auto& e : m_entities) {
        int count = 0;
        for (const auto& other : m_entities) {
            if (e.id == other.id) continue;
            if (distance2(e.position, other.position) <= neighborR2) count++;
        }
        SetNumber(e.state, "neighbors", static_cast<double>(count));

        // Cache nearest resource distance^2
        double nearestResource = std::numeric_limits<double>::infinity();
        for (const auto& other : m_entities) {
            if (other.kind != "resource") continue;
            const double d2 = distance2(e.position, other.position);
            if (d2 < nearestResource) nearestResource = d2;
        }
        if (nearestResource < std::numeric_limits<double>::infinity()) {
            SetNumber(e.state, "nearestResourceDist2", nearestResource);
        }
    }
}

void Runtime::PhaseConstraint() {
    // Enforce max agents if specified
    auto it = m_config.constraints.find("maxAgents");
    if (it != m_config.constraints.end()) {
        double maxVal = 0.0;
        if (auto p = std::get_if<double>(&it->second)) maxVal = *p;
        else if (auto b = std::get_if<bool>(&it->second)) maxVal = *b ? 1.0 : 0.0;
        const std::size_t maxAgents = static_cast<std::size_t>(std::max(0.0, maxVal));
        if (m_entities.size() > maxAgents) {
            m_entities.resize(maxAgents);
        }
    }
}

void Runtime::PhaseEpistemic() {
    // Visibility based on sensing radius and chi scaling
    const double senseBase = GetNumber(m_heuristics.parameters, "aiSensoryRangeBase", 0.0);
    const double senseMax = GetNumber(m_heuristics.parameters, "aiSensoryRangeMax", senseBase);
    const double sensePerChi = GetNumber(m_heuristics.parameters, "aiSenseRangePerChi", 0.0);
    for (auto& e : m_entities) {
        int visible = 0;
        double chi = GetNumber(e.state, "chi", GetNumber(e.state, "Chi", 0.0));
        double radius = std::min(senseMax, senseBase + chi * sensePerChi);
        double r2 = radius * radius;
        for (const auto& other : m_entities) {
            if (other.id == e.id) continue;
            if (other.kind != "resource") continue;
            if (distance2(e.position, other.position) <= r2) visible++;
        }
        SetNumber(e.state, "visibleResources", static_cast<double>(visible));
    }
}

void Runtime::PhaseDynamics() {
    const double chiLeak = GetNumber(m_heuristics.parameters, "chiLeakPerSec", 0.0);
    const double chiMoveCost = GetNumber(m_heuristics.parameters, "chiMoveCostPerSec", 0.0);
    const double energyLeak = GetNumber(m_heuristics.parameters, "energyLeakPerSec", 0.0);
    const double energyGainPerFood = GetNumber(m_heuristics.parameters, "energyGainPerFood", 0.0);
    const double chiRegenRate = GetNumber(m_heuristics.parameters, "chiRegenRateFromEnergy", 0.0);
    const double chiRegenThreshold = GetNumber(m_heuristics.parameters, "chiRegenThresholdEnergy", 0.0);
    const double steeringWeightScale = 1.0; // placeholder
    const double maxSpeed = GetNumber(m_heuristics.parameters, "maxSpeed", 0.0);
    const double resourceRadius = m_config.geometry.count("resourceRadius") ? m_config.geometry["resourceRadius"] : 10.0;
    const double worldHalf = m_config.geometry.count("worldHalfSize") ? m_config.geometry["worldHalfSize"] : 500.0;
    const double mitosisThreshold = GetNumber(m_heuristics.parameters, "mitosisThreshold", 1e9);
    const double mitosisCost = GetNumber(m_heuristics.parameters, "mitosisCost", 0.0);
    const double childStartChi = GetNumber(m_heuristics.parameters, "childStartChi", 0.0);
    const double mitosisCooldown = GetNumber(m_heuristics.parameters, "mitosisCooldown", 0.0);
    const double spawnOffset = GetNumber(m_heuristics.parameters, "spawnOffset", 10.0);
    const bool inheritHeading = GetBool(m_heuristics.parameters, "inheritHeading", false);
    std::size_t maxAgents = static_cast<std::size_t>(GetNumber(m_config.constraints, "maxAgents", static_cast<double>(m_entities.size() + 1000)));

    // Track resources for carrying capacity
    std::size_t resourceCount = std::count_if(m_entities.begin(), m_entities.end(), [](const Entity& e) { return e.kind == "resource"; });

    for (auto& e : m_entities) {
        double chi = GetNumber(e.state, "chi", GetNumber(e.state, "Chi", 0.0));
        double energy = GetNumber(e.state, "energy", GetNumber(e.state, "Energy", 0.0));

        // Leak
        chi -= chiLeak + chiMoveCost;
        energy -= energyLeak;

        // Simple resource gain if any visible resources (from PhaseEpistemic marker)
        const double vis = GetNumber(e.state, "visibleResources", 0.0);
        if (vis > 0 && energyGainPerFood > 0.0) {
            energy += energyGainPerFood * std::min(vis, 1.0);
        }

        // Regen chi from energy if above threshold
        if (energy > chiRegenThreshold && chiRegenRate > 0.0) {
            const double delta = std::min(chiRegenRate, energy - chiRegenThreshold);
            chi += delta;
            energy -= delta;
        }

        // Apply simple steering feeds: accumulate metric * weight
        double steerBias = 0.0;
        for (const auto& sf : m_signal.steeringFeeds) {
            steerBias += SampleMetric(e, sf.metric) * sf.weight;
        }
        // Crude rule bias mapping: use rule names to bias steering if present
        auto rb = m_ruleBiasMap.find("seek_resource");
        if (rb != m_ruleBiasMap.end()) steerBias += rb->second;
        rb = m_ruleBiasMap.find("avoid_distress");
        if (rb != m_ruleBiasMap.end()) steerBias -= rb->second;
        SetNumber(e.state, "steeringBias", steerBias * steeringWeightScale);

        // Clamp at zero
        if (chi < 0.0) chi = 0.0;
        if (energy < 0.0) energy = 0.0;

        SetNumber(e.state, "chi", chi);
        SetNumber(e.state, "energy", energy);

        // Agent observation feeds: stash metric values under keys
        for (const auto& feed : m_signal.agentObservations) {
            if (feed.scope != "agent") continue;
            const double val = SampleMetric(e, feed.metric);
            SetNumber(e.state, feed.key, val);
        }

        // Simple movement: drift with steering bias toward nearest resource direction if available
        Vec3 delta{0, 0, 0};
        if (maxSpeed > 0.0) {
            // random wander
            delta.x += randRange(-1.0, 1.0);
            delta.y += randRange(-1.0, 1.0);
            // steering bias as magnitude
            const double bias = GetNumber(e.state, "steeringBias", 0.0);
            if (bias != 0.0) {
                // nudge toward decreasing nearestResourceDist2 if known
                // crude: move toward origin if no better info
                double dirX = 0.0;
                double dirY = 0.0;
                if (GetNumber(e.state, "nearestResourceDist2", std::numeric_limits<double>::infinity()) < std::numeric_limits<double>::infinity()) {
                    // find closest resource
                    const Entity* nearestRes = nullptr;
                    double best = std::numeric_limits<double>::infinity();
                    for (const auto& r : m_entities) {
                        if (r.kind != "resource") continue;
                        const double d2 = distance2(e.position, r.position);
                        if (d2 < best) {
                            best = d2;
                            nearestRes = &r;
                        }
                    }
                    if (nearestRes) {
                        dirX = nearestRes->position.x - e.position.x;
                        dirY = nearestRes->position.y - e.position.y;
                    }
                }
                const double len = std::sqrt(dirX * dirX + dirY * dirY);
                if (len > 1e-6) {
                    dirX /= len;
                    dirY /= len;
                }
                delta.x += dirX * bias;
                delta.y += dirY * bias;
            }
            // clamp step
            const double stepLen = std::sqrt(delta.x * delta.x + delta.y * delta.y);
            if (stepLen > 1e-6) {
                const double scale = std::min(maxSpeed, stepLen);
                delta.x = delta.x / stepLen * scale;
                delta.y = delta.y / stepLen * scale;
            }
            e.position.x += delta.x;
            e.position.y += delta.y;

            // bounds
            e.position.x = std::clamp(e.position.x, -worldHalf, worldHalf);
            e.position.y = std::clamp(e.position.y, -worldHalf, worldHalf);
        }

        // Consume resource if within radius
        for (auto& res : m_entities) {
            if (res.kind != "resource") continue;
            const double d2 = distance2(e.position, res.position);
            if (d2 <= resourceRadius * resourceRadius) {
                energy += energyGainPerFood;
                res.state["consumed"] = true;
                break;
            }
        }

        // Simple reproduction gate
        double cooldown = GetNumber(e.state, "mitosisCooldown", 0.0);
        if (cooldown > 0.0) {
            cooldown -= 1.0;
            SetNumber(e.state, "mitosisCooldown", cooldown);
        }
        bool respectCapacity = GetBool(m_config.constraints, "respectCarryingCapacity", false);
        double capMult = GetNumber(m_config.constraints, "carryingCapacityMultiplier", 1.0);
        std::size_t carryingCap = respectCapacity ? static_cast<std::size_t>(resourceCount * capMult) : maxAgents;
        if (chi > mitosisThreshold && cooldown <= 0.0 && m_entities.size() < maxAgents && m_entities.size() < carryingCap) {
            chi -= mitosisCost;
            Entity child = e;
            child.id = e.id + "_child_" + std::to_string(static_cast<int>(randRange(0, 1e6)));
            child.label = "child";
            child.position.x += randRange(-spawnOffset, spawnOffset);
            child.position.y += randRange(-spawnOffset, spawnOffset);
            if (!inheritHeading) {
                child.state.erase("steeringBias");
            }
            SetNumber(child.state, "chi", childStartChi);
            SetNumber(child.state, "energy", energy * 0.5);
            SetNumber(e.state, "mitosisCooldown", mitosisCooldown);
            m_entities.push_back(std::move(child));
        }
    }

    // Remove consumed resources
    m_entities.erase(std::remove_if(m_entities.begin(), m_entities.end(), [](const Entity& e) {
        return e.kind == "resource" && GetBool(e.state, "consumed", false);
    }), m_entities.end());
}

void Runtime::PhaseMeta() {
    // Remove entities with chi == 0 (simple decay)
    m_entities.erase(std::remove_if(m_entities.begin(), m_entities.end(), [](const Entity& e) {
        return GetNumber(e.state, "chi", 0.0) <= 0.0;
    }), m_entities.end());
}

void Runtime::PhaseGCO() {
    // Deduplicate relations by (primitive, source, target)
    std::unordered_set<std::string> seen;
    std::vector<Relation> deduped;
    deduped.reserve(m_relations.size());
    for (const auto& r : m_relations) {
        const std::string key = std::to_string(static_cast<int>(r.primitive)) + ":" + r.source + ":" + r.target;
        if (seen.insert(key).second) {
            deduped.push_back(r);
        }
    }
    m_relations.swap(deduped);

    // Apply optional GCO thresholds (placeholder: if metric < threshold, drop relation)
    ApplyGcoThresholds();
}

void Runtime::ApplyRuleBiases() {
    m_ruleBiasMap.clear();
    for (const auto& rb : m_signal.ruleBiases) {
        m_ruleBiasMap[rb.rule] += rb.weight;
    }
}

void Runtime::ApplyGcoThresholds() {
    if (m_signal.gcoThresholds.empty()) return;
    // simple metric sampling per relation target
    m_relations.erase(std::remove_if(m_relations.begin(), m_relations.end(), [&](const Relation& r) {
        // find entity
        auto it = std::find_if(m_entities.begin(), m_entities.end(), [&](const Entity& e) { return e.id == r.target; });
        if (it == m_entities.end()) return false;
        for (const auto& th : m_signal.gcoThresholds) {
            if (th.target == r.target || th.target.empty()) {
                double val = SampleMetric(*it, th.metric);
                if (val < th.threshold) return true; // drop relation
            }
        }
        return false;
    }), m_relations.end());
}

} // namespace interessence
