#include "runtime/Loader.h"
#include <fstream>

#ifdef INTERESSENCE_ENABLE_JSON
#include <nlohmann/json.hpp>
#endif

namespace interessence {

namespace {

Primitive ParsePrimitive(const std::string& s) {
    const std::string up = s;
    if (up == "GEOMETRY") return Primitive::GEOMETRY;
    if (up == "CONSTRAINT") return Primitive::CONSTRAINT;
    if (up == "EPISTEMIC") return Primitive::EPISTEMIC;
    if (up == "DYNAMICS") return Primitive::DYNAMICS;
    if (up == "META") return Primitive::META;
    return Primitive::ONTOLOGY;
}

#ifdef INTERESSENCE_ENABLE_JSON
RPFingerprint ParseRP(const nlohmann::json& rp) {
    RPFingerprint out{};
    out.P1_identity = rp.value("P1_identity", out.P1_identity);
    out.P2_dynamics = rp.value("P2_dynamics", out.P2_dynamics);
    out.P3_geometry = rp.value("P3_geometry", out.P3_geometry);
    out.P4_constraints = rp.value("P4_constraints", out.P4_constraints);
    out.P5_epistemic = rp.value("P5_epistemic", out.P5_epistemic);
    out.P6_meta = rp.value("P6_meta", out.P6_meta);
    return out;
}
#endif

} // namespace

LoadResult LoadPacksFromStrings(const std::string& worldJson,
                                const std::string& heuristicsJson,
                                const std::string& signalJson) {
#ifndef INTERESSENCE_ENABLE_JSON
    return {false, {"JSON parsing disabled; rebuild with INTERESSENCE_ENABLE_JSON=ON"}, std::nullopt};
#else
    LoadResult result;
    try {
        nlohmann::json w = nlohmann::json::parse(worldJson);
        nlohmann::json h = nlohmann::json::parse(heuristicsJson);
        nlohmann::json s = nlohmann::json::parse(signalJson);

        RuntimeBundle bundle;

        // Entities
        if (w.contains("entities") && w["entities"].is_array()) {
            for (const auto& e : w["entities"]) {
                Entity ent;
                ent.id = e.value("id", "");
                ent.kind = e.value("kind", e.value("type", "entity"));
                ent.label = e.value("label", "");
                if (e.contains("position")) {
                    ent.position.x = e["position"].value("x", 0.0);
                    ent.position.y = e["position"].value("y", 0.0);
                    ent.position.z = e["position"].value("z", 0.0);
                }
                if (e.contains("state") && e["state"].is_object()) {
                    for (auto it = e["state"].begin(); it != e["state"].end(); ++it) {
                        if (it->is_boolean()) ent.state[it.key()] = it->get<bool>();
                        else if (it->is_number()) ent.state[it.key()] = it->get<double>();
                        else if (it->is_string()) ent.state[it.key()] = it->get<std::string>();
                    }
                }
                if (e.contains("rp")) {
                    ent.rp = ParseRP(e["rp"]);
                }
                bundle.entities.push_back(std::move(ent));
            }
        }

        // Relations
        if (w.contains("relations") && w["relations"].is_array()) {
            for (const auto& r : w["relations"]) {
                if (!r.contains("source") || !r.contains("target")) continue;
                Relation rel;
                rel.id = r.value("id", "");
                rel.source = r.value("source", "");
                rel.target = r.value("target", "");
                rel.weight = r.value("weight", 1.0);
                rel.primitive = ParsePrimitive(r.value("primitive", "ONTOLOGY"));
                if (r.contains("payload")) {
                    rel.payloadRaw = r["payload"].dump();
                }
                bundle.relations.push_back(std::move(rel));
            }
        }

        // Config
        if (w.contains("toggles") && w["toggles"].is_object()) {
            for (auto it = w["toggles"].begin(); it != w["toggles"].end(); ++it) {
                if (it->is_boolean()) bundle.config.toggles[it.key()] = it->get<bool>();
            }
        }
        auto copyNumberMap = [](const nlohmann::json& obj, std::unordered_map<std::string, double>& out) {
            for (auto it = obj.begin(); it != obj.end(); ++it) {
                if (it->is_number()) out[it.key()] = it->get<double>();
                else if (it->is_boolean()) out[it.key()] = it->get<bool>() ? 1.0 : 0.0;
            }
        };
        auto copyValueMap = [](const nlohmann::json& obj, std::unordered_map<std::string, Value>& out) {
            for (auto it = obj.begin(); it != obj.end(); ++it) {
                if (it->is_boolean()) out[it.key()] = it->get<bool>();
                else if (it->is_number()) out[it.key()] = it->get<double>();
                else if (it->is_string()) out[it.key()] = it->get<std::string>();
            }
        };
        if (w.contains("geometry") && w["geometry"].is_object()) copyNumberMap(w["geometry"], bundle.config.geometry);
        if (w.contains("constraints") && w["constraints"].is_object()) copyValueMap(w["constraints"], bundle.config.constraints);
        if (w.contains("ecology") && w["ecology"].is_object()) copyNumberMap(w["ecology"], bundle.config.ecology);
        if (w.contains("reproduction") && w["reproduction"].is_object()) copyNumberMap(w["reproduction"], bundle.config.reproduction);

        // Heuristics
        if (h.contains("parameters") && h["parameters"].is_object()) {
            for (auto it = h["parameters"].begin(); it != h["parameters"].end(); ++it) {
                        if (it->is_boolean()) bundle.heuristics.parameters[it.key()] = it->get<bool>();
                        else if (it->is_number()) bundle.heuristics.parameters[it.key()] = it->get<double>();
                        else if (it->is_string()) bundle.heuristics.parameters[it.key()] = it->get<std::string>();
                    }
                }

        // Signal
        if (s.contains("field") && s["field"].is_object()) {
            for (auto it = s["field"].begin(); it != s["field"].end(); ++it) {
                if (it->is_boolean()) bundle.signal.field[it.key()] = it->get<bool>();
                else if (it->is_number()) bundle.signal.field[it.key()] = it->get<double>();
                else if (it->is_string()) bundle.signal.field[it.key()] = it->get<std::string>();
            }
        }
        if (s.contains("compute") && s["compute"].is_array()) {
            for (const auto& c : s["compute"]) {
                std::unordered_map<std::string, Value> entry;
                if (c.is_object()) {
                    for (auto it = c.begin(); it != c.end(); ++it) {
                        if (it->is_boolean()) entry[it.key()] = it->get<bool>();
                        else if (it->is_number()) entry[it.key()] = it->get<double>();
                        else if (it->is_string()) entry[it.key()] = it->get<std::string>();
                    }
                }
                bundle.signal.compute.push_back(std::move(entry));
            }
        }
        if (s.contains("feeds") && s["feeds"].is_object()) {
            const auto& f = s["feeds"];
            if (f.contains("ruleBiases") && f["ruleBiases"].is_array()) {
                for (const auto& rb : f["ruleBiases"]) {
                    if (!rb.is_object()) continue;
                    SignalConfig::RuleBias bias;
                    bias.rule = rb.value("rule", "");
                    bias.metric = rb.value("metric", "");
                    bias.weight = rb.value("weight", 0.0);
                    bundle.signal.ruleBiases.push_back(std::move(bias));
                }
            }
            if (f.contains("gcoThresholds") && f["gcoThresholds"].is_array()) {
                for (const auto& gt : f["gcoThresholds"]) {
                    if (!gt.is_object()) continue;
                    SignalConfig::GcoThreshold th;
                    th.target = gt.value("target", "");
                    th.metric = gt.value("metric", "");
                    th.threshold = gt.value("threshold", 0.0);
                    bundle.signal.gcoThresholds.push_back(std::move(th));
                }
            }
            if (f.contains("agentObservation") && f["agentObservation"].is_array()) {
                for (const auto& ao : f["agentObservation"]) {
                    if (!ao.is_object()) continue;
                    SignalConfig::AgentObservationFeed feed;
                    feed.scope = ao.value("scope", "agent");
                    feed.metric = ao.value("metric", "");
                    feed.key = ao.value("key", "");
                    bundle.signal.agentObservations.push_back(std::move(feed));
                }
            }
            if (f.contains("steering") && f["steering"].is_array()) {
                for (const auto& st : f["steering"]) {
                    if (!st.is_object()) continue;
                    SignalConfig::SteeringFeed feed;
                    feed.metric = st.value("metric", "");
                    feed.weight = st.value("weight", 0.0);
                    bundle.signal.steeringFeeds.push_back(std::move(feed));
                }
            }
        }
        if (s.contains("participation") && s["participation"].is_object()) {
            for (auto it = s["participation"].begin(); it != s["participation"].end(); ++it) {
                if (it->is_boolean()) bundle.signal.participation[it.key()] = it->get<bool>();
                else if (it->is_number()) bundle.signal.participation[it.key()] = it->get<double>();
                else if (it->is_string()) bundle.signal.participation[it.key()] = it->get<std::string>();
            }
        }

        result.ok = true;
        result.bundle = std::move(bundle);
        return result;
    } catch (const std::exception& ex) {
        result.ok = false;
        result.errors.push_back(ex.what());
        return result;
    }
#endif
}

LoadResult LoadPacksFromFiles(const std::string& worldPath,
                              const std::string& heuristicsPath,
                              const std::string& signalPath) {
#ifndef INTERESSENCE_ENABLE_JSON
    return {false, {"JSON parsing disabled; rebuild with INTERESSENCE_ENABLE_JSON=ON"}, std::nullopt};
#else
    auto slurp = [](const std::string& path) -> std::string {
        std::ifstream ifs(path);
        if (!ifs) throw std::runtime_error("Failed to open file: " + path);
        return std::string((std::istreambuf_iterator<char>(ifs)), std::istreambuf_iterator<char>());
    };
    try {
        const std::string w = slurp(worldPath);
        const std::string h = slurp(heuristicsPath);
        const std::string s = slurp(signalPath);
        return LoadPacksFromStrings(w, h, s);
    } catch (const std::exception& ex) {
        return {false, {ex.what()}, std::nullopt};
    }
#endif
}

} // namespace interessence
