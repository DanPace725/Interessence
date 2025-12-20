# Understanding Relational Primitives

## What Are Relational Primitives?

Traditional game AI uses **state machines** and **behavior trees**. These work, but they're:
- Brittle (hard to modify without breaking)
- Opaque (hard to debug)
- Non-emergent (behavior is scripted, not derived)

**Relational Primitives** offer a different approach: describe *relationships* between entities, and let behavior *emerge* from those relationships.

## The Six Primitives

### 1. ONTOLOGY - "What Is It?"

Defines **identity, structure, and composition** of entities.

**Examples:**
- "This entity is a wolf"
- "Wolves are composed of: body, hunger, pack-affiliation"
- "This berry bush is a resource node"

**In Code:**
```cpp
Entity* wolf = world.createEntity("wolf_1", "predator");
wolf->setState("predator_type", "wolf");
wolf->setState("pack_id", "pack_alpha");
```

**Why It Matters:**
- Entities need identity before they can interact
- Composition defines emergent properties
- Categories enable pattern-matching rules

---

### 2. GEOMETRY - "Where and When?"

Defines **spatial, temporal, and causal structure**.

**Examples:**
- "Wolf is at position (100, 200)"
- "Sheep is within 80 units of wolf"
- "Event A must happen before event B"

**In Code:**
```cpp
// Spatial
entity->setState("x", 100.0f);
entity->setState("y", 200.0f);

// Query spatial relationships
auto nearby = spatialIndex->queryRadius(Vec2(x, y), visionRange);

// Temporal/Causal
// (implicit in tick ordering and rule dependencies)
```

**Why It Matters:**
- Space determines what *can* interact
- Causality determines what *order* things happen
- Proximity creates opportunities for emergence

---

### 3. CONSTRAINT - "What Are the Rules?"

Defines **bounds, limits, conservation laws, and forbidden states**.

**Examples:**
- "Health cannot exceed 100"
- "Energy cannot be negative"
- "Wolf cannot exist in water tiles"
- "Total resources in system are conserved"

**In Code:**
```cpp
// Clamp health
float health = entity->getState<float>("health");
float maxHealth = entity->getState<float>("max_health");
entity->setState("health", std::clamp(health, 0.0f, maxHealth));

// Boundary enforcement
if (x < worldMinX) x = worldMinX;
if (x > worldMaxX) x = worldMaxX;
```

**Why It Matters:**
- Prevents invalid states
- Enforces physical laws
- Creates scarcity (drives emergent behavior)
- Enables conservation laws (energy, matter)

---

### 4. EPISTEMIC - "What Can Be Known?"

Defines **visibility, memory, inference, and accessible information**.

**Examples:**
- "Wolf can see sheep within 100 units"
- "Sheep knows it saw a wolf 10 ticks ago"
- "Player faction has incomplete knowledge of enemy positions"
- "This entity is occluded by terrain"

**In Code:**
```cpp
// Visibility check
float visionRange = predator->getState<float>("vision_range");
auto visible = spatialIndex->queryRadius(predatorPos, visionRange);

// Memory
entity->setState("last_seen_predator", tick);
entity->setState("last_known_food_pos", Vec2(x, y));

// Inference (future)
// entity->setState("believes_food_nearby", true);
```

**Why It Matters:**
- Entities act on **perceived** reality, not ground truth
- Enables stealth, misinformation, rumors
- Creates fog-of-war
- Grounds AI in realistic limitations

---

### 5. DYNAMICS - "How Does It Change?"

Defines **movement, interaction, transformation, and evolution**.

**Examples:**
- "Wolf moves toward sheep at 1.5 units/tick"
- "Sheep flees from wolf"
- "Berry bush regrows 0.1 resources/tick"
- "Energy decreases by 0.5/tick (metabolism)"

**In Code:**
```cpp
// Movement
float vx = entity->getState<float>("vel_x");
float vy = entity->getState<float>("vel_y");
entity->setState("x", x + vx);
entity->setState("y", y + vy);

// Interaction
if (distance < consumeRange) {
    float consumed = std::min(resourceAmount, 10.0f);
    resource->setState("amount", resourceAmount - consumed);
    agent->setState("energy", energy + consumed);
}

// Evolution
float energy = entity->getState<float>("energy");
entity->setState("energy", energy - metabolismRate);
```

**Why It Matters:**
- This is where most "game logic" lives
- Dynamics create change → change creates story
- Grounded in geometry, epistemic, and constraints

---

### 6. META - "Rules About Rules"

Defines **spawning, despawning, structural changes, and rule mutations**.

**Examples:**
- "Spawn new wolf when pack size < 3"
- "Remove entity when health <= 0"
- "Faction splits when internal tension > threshold"
- "Add new rule: 'wolves fear fire'"

**In Code:**
```cpp
// Spawning
if (packSize < minPackSize && foodAbundant) {
    EntityTemplates::createPredator(world, "wolf_new", x, y);
}

// Despawning
if (health <= 0.0f) {
    world.removeEntity(entityId);
}

// Rule injection (advanced)
if (playerBuiltFirePit) {
    engine.registerDynamicsRule("AvoidFire", avoidFireBehavior);
}
```

**Why It Matters:**
- Enables population dynamics
- Allows world to evolve its own rules
- Supports player creations that change gameplay
- Drives faction evolution and cultural drift

---

## The Global Closure Operator (GCO)

After all six primitives are applied, the **GCO** ensures the world state is:
- **Consistent** (no contradictions)
- **Minimal** (no redundant relations)
- **Stable** (ready for next tick)

Think of it as a "sanity check" that:
- Removes duplicate relations
- Resolves conflicts (e.g., two entities claiming same space)
- Enforces schema invariants
- Produces debug logs for inspection

**In Code:**
```cpp
void RPEngine::executeGCO() {
    // Deduplicate relations
    // Resolve spatial conflicts
    // Enforce invariants
    // Log closure events for debugging
}
```

---

## How They Work Together: An Example

Let's trace a simple scenario: **Wolf hunts sheep**

### Phase 1: GEOMETRY
```
- Wolf at (100, 100)
- Sheep at (120, 110)
- Distance = 22.36 units
- Wolf vision range = 100 units
- Sheep is within wolf's vision
```

### Phase 2: CONSTRAINT
```
- Wolf health clamped to [0, 150]
- Sheep cannot move through rocks
- Wolf energy must be > 0 to hunt
```

### Phase 3: EPISTEMIC
```
- Wolf KNOWS sheep is at (120, 110)
- Sheep DOES NOT know wolf is nearby (wolf is downwind)
- Wolf remembers sheep's position
```

### Phase 4: DYNAMICS
```
- Wolf calculates direction to sheep
- Wolf moves toward sheep at 1.5 units/tick
- Wolf energy -= 0.5 (metabolism)
- Sheep wanders randomly (unaware)
```

### Phase 5: META
```
- (Nothing to spawn/despawn this tick)
- (No rule changes)
```

### Phase 6: GCO
```
- No conflicts detected
- All entities in valid state
- Ready for next tick
```

**Next tick:**
- Wolf is closer
- Sheep still unaware
- Eventually wolf enters attack range
- Dynamics triggers attack
- Sheep health decreases
- Sheep's epistemic updates (now knows about wolf!)
- Sheep dynamics change (flee behavior)

**This entire sequence emerged from rules, not scripts.**

---

## Design Patterns

### Pattern 1: Reactive Behavior

**Don't write:** "If see predator, then flee"

**Do write:**
```cpp
// EPISTEMIC: Check what entity knows
auto visible = getVisibleEntities(entity);
for (auto* other : visible) {
    if (other->getKind() == "predator") {
        // DYNAMICS: React based on knowledge
        Vec2 fleeDirection = calculateFleeVector(entity, other);
        entity->setState("vel_x", fleeDirection.x);
        entity->setState("vel_y", fleeDirection.y);
    }
}
```

### Pattern 2: Emergent Flocking

**Don't write:** "Move toward flock center"

**Do write:**
```cpp
// GEOMETRY: Find nearby same-type entities
auto neighbors = spatialIndex->queryRadius(pos, flockRadius);

// DYNAMICS: Average positions and velocities
Vec2 avgPos = computeAverage(neighbors, "position");
Vec2 avgVel = computeAverage(neighbors, "velocity");

// Apply slight attraction (emergence happens naturally)
Vec2 steering = (avgPos - myPos) * 0.1f + avgVel * 0.2f;
```

### Pattern 3: Resource Scarcity

**Don't write:** "If food < threshold, spawn more"

**Do write:**
```cpp
// CONSTRAINT: Conservation law
float totalFood = sumResourceAmounts(world);

// DYNAMICS: Natural regrowth
for (auto* resource : resources) {
    float amount = resource->getState<float>("amount");
    float regrowth = resource->getState<float>("regrowth_rate");
    resource->setState("amount", amount + regrowth);
}

// Scarcity emerges from:
// - Consumption (dynamics)
// - Regrowth rate (dynamics)
// - No artificial spawning
```

---

## Common Mistakes

### ❌ Mixing Primitives

**Bad:**
```cpp
// Constraint phase doing dynamics work
void executeConstraint() {
    entity->setState("x", x + vx);  // This is DYNAMICS!
}
```

**Good:**
```cpp
// Constraint phase enforcing bounds
void executeConstraint() {
    float x = entity->getState<float>("x");
    if (x < minX) entity->setState("x", minX);
}

// Dynamics phase doing movement
void executeDynamics() {
    float x = entity->getState<float>("x");
    float vx = entity->getState<float>("vel_x");
    entity->setState("x", x + vx);
}
```

### ❌ Acting on Unknown Information

**Bad:**
```cpp
// Entity magically knows enemy position
Vec2 enemyPos = getEnemyPosition();  // How did we know?
moveToward(enemyPos);
```

**Good:**
```cpp
// EPISTEMIC: Check if entity can see enemy
auto visible = getVisibleEntities(entity);
for (auto* other : visible) {
    if (other->isEnemy()) {
        // DYNAMICS: Now we can act on known information
        Vec2 enemyPos = other->getPosition();
        moveToward(enemyPos);
    }
}
```

### ❌ Hardcoding Emergence

**Bad:**
```cpp
// Scripted "predator avoidance"
if (entity->getKind() == "sheep" && nearPredator) {
    runAway();  // Hardcoded behavior
}
```

**Good:**
```cpp
// Let behavior emerge from energy trade-offs
float fear = entity->getState<float>("fear_level");
float energy = entity->getState<float>("energy");

if (fear > threshold && energy > costToFlee) {
    // Fleeing is expensive but necessary
    flee();
    entity->setState("energy", energy - fleeCost);
}
```

---

## Debugging Relational Systems

### Enable Verbose Logging
```cpp
engine.setVerbose(true);
```

### Add Debug Prints
```cpp
std::cout << "Entity " << id << " at (" << x << "," << y << ")" << std::endl;
std::cout << "  Energy: " << energy << "/" << maxEnergy << std::endl;
std::cout << "  Visible entities: " << visible.size() << std::endl;
```

### Visualize Relations
```cpp
// Print all relations for an entity
auto relations = world.getRelationsForEntity("wolf_1");
for (auto* rel : relations) {
    std::cout << rel->toString() << std::endl;
}
```

### Check Invariants
```cpp
// After each tick, verify world state
assert(totalEnergy <= maxTotalEnergy);  // Conservation
assert(entity->getState<float>("health") >= 0.0f);  // Constraint
```

---

## Further Reading

- **rpe.md** - Technical specification of the RPE
- **rpgsimoverview.md** - High-level game design
- **Relational Primitives/** - Theoretical foundations
- **examples/ecosystem_demo.cpp** - Working example

---

**Remember:** The goal is not to *script* behavior, but to create conditions where behavior *emerges naturally* from relational structure.
