"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { AgentStudy } from "./agent-study";
import {
  MAX_BEATS,
  WORLD_HEIGHT,
  WORLD_WIDTH,
  actionLabel,
  applyIntervention,
  canReach,
  createWorld,
  distance,
  moodLabel,
  moveObserver,
  nudgeObserver,
  relationLabel,
  speciesLabel,
  stepWorld,
  summarizeWorld,
  type Intervention,
  type SignalOverlay,
  type WorldState,
} from "./simulation";
import { agentAtPoint, canvasPoint, drawWorld } from "./world-art";
import { interpolateWorld, SIMULATION_TICK_MS, snapshotWorld } from "./visual-interpolation";

const INITIAL_SEED = 7319;

function Meter({ label, value, tone }: { label: string; value: number; tone: "gold" | "coral" | "mint" }) {
  return (
    <div className="meter-row">
      <span>{label}</span>
      <div className="meter-track" aria-label={`${label}: ${Math.round(value * 100)} percent`}>
        <span className={`meter-fill meter-${tone}`} style={{ width: `${Math.max(3, value * 100)}%` }} />
      </div>
    </div>
  );
}

function SpeciesMark({ species }: { species: "brambleback" | "wickwing" | "mirehorn" }) {
  return (
    <span className={`species-mark species-${species}`} aria-hidden="true">
      <i />
      <b />
      <em />
    </span>
  );
}

function FieldJournal({
  world,
  selectedId,
  overlay,
  notice,
  onIntervene,
}: {
  world: WorldState;
  selectedId: string | null;
  overlay: SignalOverlay;
  notice: string;
  onIntervene: (kind: Intervention) => void;
}) {
  const selected = world.agents.find((agent) => agent.id === selectedId) ?? null;
  const reachable = selected ? canReach(world, selected) : false;
  const labOpen = overlay !== "none";

  return (
    <aside className="journal" aria-label="Field journal">
      <div className="journal-heading">
        <div>
          <p className="eyebrow">Field journal</p>
          <h2>{selected ? selected.name : "Unwritten page"}</h2>
        </div>
        <span className={`range-status ${reachable ? "range-near" : ""}`}>
          {selected ? (reachable ? "within lantern" : "distant") : "no subject"}
        </span>
      </div>

      {!selected ? (
        <div className="empty-journal">
          <div className="empty-rings" aria-hidden="true"><span /><span /><span /></div>
          <p>Select a creature in the clearing. Move close enough to attend, nourish, or ward it.</p>
        </div>
      ) : (
        <>
          <div className="creature-intro">
            <SpeciesMark species={selected.species} />
            <div>
              <span>{speciesLabel(selected.species)}</span>
              <strong>{selected.epithet}</strong>
            </div>
          </div>
          <p className="creature-description">{selected.description}</p>

          <div className="reading-block">
            <span className="reading-label">Visible reading</span>
            <strong>{moodLabel(selected)}</strong>
            <p>Currently {actionLabel(selected.action)}.</p>
          </div>

          {selected.attended || labOpen ? (
            <div className="meters">
              <Meter label="Vitality" value={selected.energy} tone="gold" />
              <Meter label="Strain" value={selected.stress} tone="coral" />
              <Meter label="Familiarity" value={(selected.trustObserver + 1) / 2} tone="mint" />
            </div>
          ) : (
            <p className="unread-note">Attend quietly to make these conditions legible.</p>
          )}

          <div className="relationship-note">
            <span className="knot" aria-hidden="true">⌁</span>
            <p>{relationLabel(selected)}</p>
          </div>

          <div className="interventions" aria-label="Interventions">
            <button disabled={!reachable || world.focus < 1 || world.complete} onClick={() => onIntervene("attend")}>
              <span>Attend</span><small>1 focus</small>
            </button>
            <button disabled={!reachable || world.focus < 2 || world.complete} onClick={() => onIntervene("nourish")}>
              <span>Nourish</span><small>2 focus</small>
            </button>
            <button className="ward-button" disabled={!reachable || world.focus < 1 || world.complete} onClick={() => onIntervene("ward")}>
              <span>Ward</span><small>1 focus</small>
            </button>
          </div>
          {!reachable && <p className="proximity-hint">Click nearby ground to carry your lantern closer.</p>}

          <div className="memory-section">
            <div className="section-title"><span>Relational memory</span><small>{selected.memories.length || "none yet"}</small></div>
            {selected.memories.length ? (
              <ul className="memory-list">
                {selected.memories.slice(0, 3).map((memory) => (
                  <li key={`${memory.beat}-${memory.kind}`}><span>{memory.beat}</span>{memory.text}</li>
                ))}
              </ul>
            ) : <p className="quiet-copy">No direct history between you—only first impressions.</p>}
          </div>

          {labOpen && (
            <div className="causal-section">
              <div className="section-title"><span>Why this action?</span><small>lab trace</small></div>
              <ol>
                {selected.lastReasons.map((reason) => <li key={reason}>{reason}</li>)}
              </ol>
            </div>
          )}
        </>
      )}
      <p className="notice" aria-live="polite">{notice || "The clearing offers no score—only consequences."}</p>
    </aside>
  );
}

function CompletionPanel({ world, onSameSeed, onNewSeed, onExport }: { world: WorldState; onSameSeed: () => void; onNewSeed: () => void; onExport: () => void }) {
  const summary = summarizeWorld(world);
  return (
    <div className="modal-scrim" role="dialog" aria-modal="true" aria-labelledby="closing-title">
      <section className="closing-card">
        <p className="eyebrow">Field visit complete · seed {world.seed}</p>
        <h2 id="closing-title">The clearing keeps what happened.</h2>
        <p className="closing-lede">This is not a score. It is the shape left by your attention, absence, and pressure.</p>
        <div className="summary-grid">
          <div><span>Closest presence</span><strong>{summary.mostTrusting.name}</strong><p>{relationLabel(summary.mostTrusting)}</p></div>
          <div><span>Most wary</span><strong>{summary.mostWary.name}</strong><p>{relationLabel(summary.mostWary)}</p></div>
          <div><span>Strongest creature bond</span><strong>{summary.strongest ? `${summary.strongest.a.name} + ${summary.strongest.b.name}` : "None"}</strong><p>A relationship formed without your direction.</p></div>
          <div><span>Material trace</span><strong>{summary.depleted ? `${summary.depleted} food sites thinned` : "Food sites remain viable"}</strong><p>You spent {summary.attentionSpent} of 12 focus.</p></div>
        </div>
        <div className="closing-actions">
          <button className="primary-button" onClick={onSameSeed}>Replay same seed</button>
          <button onClick={onNewSeed}>Enter a changed clearing</button>
          <button onClick={onExport}>Save field notes</button>
        </div>
      </section>
    </div>
  );
}

export default function Home() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const worldRef = useRef<WorldState>(createWorld(INITIAL_SEED));
  const previousWorldRef = useRef<WorldState>(snapshotWorld(worldRef.current));
  const visualWorldRef = useRef<WorldState>(snapshotWorld(worldRef.current));
  const lastBeatAtRef = useRef(0);
  const [revision, setRevision] = useState(0);
  const [selectedId, setSelectedId] = useState<string | null>("bracken");
  const [hoveredId, setHoveredId] = useState<string | null>(null);
  const [overlay, setOverlay] = useState<SignalOverlay>("none");
  const [introOpen, setIntroOpen] = useState(true);
  const [notice, setNotice] = useState("");
  const [studyOpen, setStudyOpen] = useState(false);
  const world = worldRef.current;

  useEffect(() => {
    let frame = 0;
    const render = (now: number) => {
      const canvas = canvasRef.current;
      const ctx = canvas?.getContext("2d");
      if (canvas && ctx) {
        const elapsed = lastBeatAtRef.current ? now - lastBeatAtRef.current : SIMULATION_TICK_MS;
        const visualWorld = interpolateWorld(previousWorldRef.current, worldRef.current, elapsed / (SIMULATION_TICK_MS * 0.94));
        visualWorldRef.current = visualWorld;
        drawWorld(ctx, visualWorld, selectedId, hoveredId, overlay);
      }
      frame = window.requestAnimationFrame(render);
    };
    frame = window.requestAnimationFrame(render);
    return () => window.cancelAnimationFrame(frame);
  }, [hoveredId, overlay, selectedId]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      const current = worldRef.current;
      if (!current.running || current.complete) return;
      previousWorldRef.current = snapshotWorld(current);
      stepWorld(current);
      lastBeatAtRef.current = performance.now();
      setRevision((value) => value + 1);
    }, SIMULATION_TICK_MS);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      const key = event.key.toLowerCase();
      const direction: Record<string, [number, number]> = {
        arrowup: [0, -24], w: [0, -24], arrowdown: [0, 24], s: [0, 24],
        arrowleft: [-24, 0], a: [-24, 0], arrowright: [24, 0], d: [24, 0],
      };
      if (direction[key]) {
        event.preventDefault();
        previousWorldRef.current = snapshotWorld(worldRef.current);
        nudgeObserver(worldRef.current, ...direction[key]);
        lastBeatAtRef.current = performance.now();
        setRevision((value) => value + 1);
      }
      if (key === " " && !introOpen) {
        event.preventDefault();
        worldRef.current.running = !worldRef.current.running;
        setRevision((value) => value + 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [introOpen]);

  const selected = world.agents.find((agent) => agent.id === selectedId) ?? null;
  const phase = world.beat < 48 ? "Late afternoon" : world.beat < 100 ? "Blue dusk" : "First night";
  const progress = Math.min(100, (world.beat / MAX_BEATS) * 100);

  const handleCanvasClick = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const point = canvasPoint(event.currentTarget, event.clientX, event.clientY);
    const agent = agentAtPoint(visualWorldRef.current, point);
    if (agent) {
      setSelectedId(agent.id);
      setNotice(`${agent.name} is ${Math.round(distance(visualWorldRef.current.observer, agent))} paces from your light.`);
    } else {
      moveObserver(worldRef.current, point);
      setNotice("You carry the lantern toward the chosen ground.");
    }
    setRevision((value) => value + 1);
  };

  const handlePointerMove = (event: React.PointerEvent<HTMLCanvasElement>) => {
    const point = canvasPoint(event.currentTarget, event.clientX, event.clientY);
    const agent = agentAtPoint(visualWorldRef.current, point);
    setHoveredId(agent?.id ?? null);
  };

  const intervene = (kind: Intervention) => {
    if (!selectedId) return;
    const result = applyIntervention(worldRef.current, selectedId, kind);
    setNotice(result.message);
    setRevision((value) => value + 1);
  };

  const begin = () => {
    setIntroOpen(false);
    worldRef.current.running = true;
    setNotice("The visit begins. Nothing here is waiting to be solved.");
    setRevision((value) => value + 1);
  };

  const reset = (seed: number) => {
    worldRef.current = createWorld(seed);
    worldRef.current.running = true;
    previousWorldRef.current = snapshotWorld(worldRef.current);
    visualWorldRef.current = snapshotWorld(worldRef.current);
    lastBeatAtRef.current = performance.now();
    setSelectedId("bracken");
    setOverlay("none");
    setNotice("The same initial conditions return; your choices need not.");
    setRevision((value) => value + 1);
  };

  const exportNotes = () => {
    const current = worldRef.current;
    const payload = {
      prototype: "The Relational Clearing v0.1",
      seed: current.seed,
      beat: current.beat,
      focusRemaining: current.focus,
      events: [...current.events].reverse(),
      creatures: current.agents.map(({ id, name, species, energy, stress, trustObserver, fearObserver, action, memories }) => ({ id, name, species, energy, stress, trustObserver, fearObserver, action, memories })),
      bonds: current.bonds,
      resources: current.resources,
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `relational-clearing-${current.seed}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const eventItems = useMemo(() => world.events.slice(0, 5), [revision, world.events]);

  return (
    <main className="app-shell">
      <header className="site-header">
        <div className="brand-block">
          <span className="brand-knot" aria-hidden="true"><i /><b /><em /></span>
          <div>
            <p>Interessence field study 01</p>
            <h1>The Relational Clearing</h1>
          </div>
        </div>
        <div className="header-study">
          <p className="header-thesis">A small ecology of memory, partial knowledge, and consequence.</p>
          <button onClick={() => setStudyOpen(true)}><span>New</span> Open agent study</button>
        </div>
        <div className="session-stats">
          <div><span>Phase</span><strong>{phase}</strong></div>
          <div><span>Focus</span><strong>{world.focus} / 12</strong></div>
          <div><span>Seed</span><strong>{world.seed}</strong></div>
        </div>
      </header>

      <section className="workbench">
        <div className="field-column">
          <div className="canvas-frame">
            <canvas
              ref={canvasRef}
              width={WORLD_WIDTH}
              height={WORLD_HEIGHT}
              aria-label="A living dusk clearing with five creatures. Click ground to move your lantern and click creatures to inspect them."
              tabIndex={0}
              onClick={handleCanvasClick}
              onPointerMove={handlePointerMove}
              onPointerLeave={() => setHoveredId(null)}
            />
            {introOpen && (
              <div className="intro-card">
                <p className="eyebrow">A ten-minute thought experiment</p>
                <h2>Enter without knowing what needs you.</h2>
                <p>Five creatures share this clearing. They perceive only what is near, remember how you treat them, and choose among competing needs.</p>
                <ul>
                  <li><span>Move</span>Click the ground or use WASD / arrow keys.</li>
                  <li><span>Read</span>Select a creature. Exact conditions require attention.</li>
                  <li><span>Intervene</span>Your twelve focus cannot cover every need.</li>
                </ul>
                <button className="primary-button" onClick={begin}>Light the field lantern</button>
              </div>
            )}
          </div>

          <div className="field-controls">
            <div className="play-controls">
              <button
                className="round-control"
                aria-label={world.running ? "Pause simulation" : "Resume simulation"}
                onClick={() => { world.running = !world.running; setRevision((value) => value + 1); }}
                disabled={introOpen || world.complete}
              >{world.running ? "Ⅱ" : "▶"}</button>
              <div className="timeline">
                <div><span>Field time</span><strong>Beat {world.beat} of {MAX_BEATS}</strong></div>
                <div className="timeline-track"><span style={{ width: `${progress}%` }} /></div>
              </div>
            </div>
            <div className="overlay-controls" aria-label="Signal overlays">
              <span>Laboratory lens</span>
              {(["none", "resource", "distress", "bond"] as SignalOverlay[]).map((channel) => (
                <button key={channel} className={overlay === channel ? "active" : ""} onClick={() => setOverlay(channel)}>
                  {channel === "none" ? "Hidden" : channel}
                </button>
              ))}
            </div>
          </div>

          <div className="lower-panels">
            <section className="event-panel">
              <div className="section-title"><span>What the clearing revealed</span><small>latest first</small></div>
              <ul>
                {eventItems.map((event) => (
                  <li key={`${event.beat}-${event.text}`} className={`event-${event.tone}`}>
                    <span>{String(event.beat).padStart(3, "0")}</span><p>{event.text}</p>
                  </li>
                ))}
              </ul>
            </section>
            <section className="legend-panel">
              <div className="section-title"><span>Field marks</span><small>not values</small></div>
              <div className="legend-items">
                <span><i className="mark-resource" />nourishment</span>
                <span><i className="mark-hazard" />strained ground</span>
                <span><i className="mark-lantern" />your local view</span>
              </div>
              <p>Signal overlays are a laboratory instrument. Creatures never receive the whole map.</p>
            </section>
          </div>
        </div>

        <FieldJournal world={world} selectedId={selected?.id ?? null} overlay={overlay} notice={notice} onIntervene={intervene} />
      </section>

      <footer>
        <p>Deterministic prototype · same seed, same unattended history</p>
        <button onClick={exportNotes}>Export field notes</button>
      </footer>

      {world.complete && <CompletionPanel world={world} onSameSeed={() => reset(world.seed)} onNewSeed={() => reset(world.seed + 7919)} onExport={exportNotes} />}
      <AgentStudy open={studyOpen} onClose={() => setStudyOpen(false)} />
    </main>
  );
}
