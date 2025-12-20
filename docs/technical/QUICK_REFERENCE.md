# RPE Quick Reference Card

## Six Relational Primitives

| Primitive | Purpose | Examples |
|-----------|---------|----------|
| **ONTOLOGY** | What is it? | Identity, kind, composition |
| **GEOMETRY** | Where/when? | Position, distance, causality |
| **CONSTRAINT** | What rules? | Bounds, limits, conservation |
| **EPISTEMIC** | What knows? | Visibility, memory, inference |
| **DYNAMICS** | How change? | Movement, interaction, growth |
| **META** | Rules² | Spawn/despawn, rule changes |

## Common Code Patterns

### Creating an Entity
```cpp
Entity* e = world.createEntity("unique_id", "kind");
e->setState("property", value);
```

### Accessing State
```cpp
float x = entity->getState<float>("x", defaultValue);
entity->setState("x", newValue);
bool hasIt = entity->hasState("x");
```

### Querying Spatial
```cpp
// By radius
auto nearby = spatialIndex->queryRadius(Vec2(x, y), radius);

// By bounding box
auto inBox = spatialIndex->queryAABB(AABB(min, max));

// Nearest N
auto nearest = spatialIndex->queryNearest(Vec2(x, y), count);
```

### Registering Rules
```cpp
engine.registerGeometryRule("Name", ruleFunction);
engine.registerConstraintRule("Name", ruleFunction);
engine.registerEpistemicRule("Name", ruleFunction);
engine.registerDynamicsRule("Name", ruleFunction);
engine.registerMetaRule("Name", ruleFunction);
```

### Rule Function Signature
```cpp
void myRule(World& world) {
    for (const auto& [id, entity] : world.getEntities()) {
        // ... do something ...
        world.markEntityDirty(id);
    }
}
```

## The 6-Phase Tick

```
┌─────────────────────────────────────┐
│  1. GEOMETRY                        │
│     - Update spatial index          │
│     - Compute proximity             │
│     - Calculate fields              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  2. CONSTRAINT                      │
│     - Clamp health/energy           │
│     - Enforce bounds                │
│     - Apply conservation            │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  3. EPISTEMIC                       │
│     - Update visibility             │
│     - Process memory                │
│     - Update knowledge graphs       │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  4. DYNAMICS                        │
│     - Apply movement                │
│     - Process interactions          │
│     - Update metabolism             │
│     - Execute behavior              │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  5. META                            │
│     - Spawn new entities            │
│     - Remove dead entities          │
│     - Inject new rules              │
│     - Faction reorganization        │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  6. GCO (Global Closure)            │
│     - Deduplicate relations         │
│     - Resolve contradictions        │
│     - Enforce invariants            │
│     - Produce closure report        │
└─────────────────────────────────────┘
```

## Entity Template Examples

### Agent (Creature)
```cpp
Entity* agent = world.createEntity(id, "agent");
agent->setState("x", x);
agent->setState("y", y);
agent->setState("health", 100.0f);
agent->setState("energy", 100.0f);
agent->setState("speed", 1.0f);
agent->setState("vision_range", 80.0f);
```

### Resource (Food)
```cpp
Entity* resource = world.createEntity(id, "resource");
resource->setState("x", x);
resource->setState("y", y);
resource->setState("amount", 50.0f);
resource->setState("regrowth_rate", 0.1f);
resource->setState("active", true);
```

### Predator
```cpp
Entity* pred = world.createEntity(id, "predator");
pred->setState("x", x);
pred->setState("y", y);
pred->setState("health", 150.0f);
pred->setState("speed", 1.5f);
pred->setState("attack_damage", 25.0f);
pred->setState("vision_range", 100.0f);
```

## Useful Math

### Distance
```cpp
float dx = x2 - x1;
float dy = y2 - y1;
float dist = std::sqrt(dx * dx + dy * dy);
float distSq = dx * dx + dy * dy;  // Faster, use when comparing
```

### Normalize Vector
```cpp
float len = std::sqrt(dx * dx + dy * dy);
if (len > 0.0f) {
    dx /= len;
    dy /= len;
}
```

### Move Toward
```cpp
float dx = targetX - x;
float dy = targetY - y;
float dist = std::sqrt(dx * dx + dy * dy);
if (dist > 0.01f) {
    entity->setState("vel_x", (dx / dist) * speed);
    entity->setState("vel_y", (dy / dist) * speed);
}
```

### Flee From
```cpp
float dx = x - threatX;  // Note: reversed
float dy = y - threatY;
float dist = std::sqrt(dx * dx + dy * dy);
if (dist > 0.01f) {
    entity->setState("vel_x", (dx / dist) * fleeSpeed);
    entity->setState("vel_y", (dy / dist) * fleeSpeed);
}
```

## Common Gotchas

### ❌ Wrong: Acting without checking epistemic
```cpp
auto* enemy = world.getEntity("enemy_1");
moveToward(enemy->getState<float>("x"));  // How did we know?
```

### ✅ Right: Check visibility first
```cpp
auto visible = spatialIndex->queryRadius(myPos, visionRange);
for (const auto& id : visible) {
    if (id.starts_with("enemy")) {
        auto* enemy = world.getEntity(id);
        moveToward(enemy->getState<float>("x"));
    }
}
```

### ❌ Wrong: Modifying state in wrong phase
```cpp
void executeGeometry() {
    entity->setState("health", health - 10);  // Dynamics work!
}
```

### ✅ Right: Correct phase for operation
```cpp
void executeDynamics() {
    entity->setState("health", health - 10);  // Correct
}
```

### ❌ Wrong: Forgetting to mark dirty
```cpp
entity->setState("x", newX);
// Entity won't be processed efficiently next tick
```

### ✅ Right: Mark when changing
```cpp
entity->setState("x", newX);
world.markEntityDirty(id);
```

## Debug Checklist

- [ ] Enable verbose: `engine.setVerbose(true)`
- [ ] Print entity state each tick
- [ ] Verify rules are registered
- [ ] Check tick is being called
- [ ] Ensure entities are created
- [ ] Verify spatial index updates
- [ ] Check for NaN/inf values
- [ ] Confirm phase order

## Performance Tips

### Use Spatial Queries
```cpp
// ❌ Slow: O(n²)
for (auto& e1 : entities) {
    for (auto& e2 : entities) {
        if (distance(e1, e2) < range) { ... }
    }
}

// ✅ Fast: O(n log n) or O(n) with good index
for (auto& e : entities) {
    auto nearby = spatialIndex->queryRadius(e.pos, range);
    for (auto& id : nearby) { ... }
}
```

### Cache Expensive Calculations
```cpp
// ❌ Recalculate every time
float dist = sqrt(dx*dx + dy*dy);
float dist2 = sqrt(dx*dx + dy*dy);  // Duplicate work

// ✅ Calculate once
float distSq = dx*dx + dy*dy;
if (distSq < rangeSq) {  // Use squared comparison
    float dist = sqrt(distSq);  // Only when needed
}
```

### Use Dirty Flags
```cpp
// Only process entities that changed
for (const auto& id : world.getDirtyEntities()) {
    auto* entity = world.getEntity(id);
    // ... expensive processing ...
}
```

## Build Commands

```bash
# Configure
cmake -B build -DCMAKE_BUILD_TYPE=Release

# Build
cmake --build build

# Run
./build/ecosystem_demo
```

## Project Layout

```
game/
├── include/          # Headers
│   ├── core/         # Core engine
│   ├── spatial/      # Spatial indexing
│   └── primitives/   # Entity templates
├── src/              # Implementations
├── examples/         # Example programs
├── docs/             # Documentation
└── CMakeLists.txt    # Build config
```

## Key Files

| File | Purpose |
|------|---------|
| `include/core/Entity.h` | Entity data structure |
| `include/core/Relation.h` | Relational primitives |
| `include/core/World.h` | World container |
| `include/core/RPEngine.h` | 6-phase tick engine |
| `include/spatial/SpatialIndex.h` | Spatial queries |
| `examples/ecosystem_demo.cpp` | Working example |

## Next Actions

1. Read `GETTING_STARTED.md`
2. Build the project
3. Run `ecosystem_demo`
4. Modify a rule
5. Create a new entity type
6. Experiment!

---

**Keep this reference handy while coding!**
