"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { AgentReplay } from "./agent-interface";
import type { MultiSeedStudy } from "./multi-seed-study";
import { WORLD_HEIGHT, WORLD_WIDTH } from "./simulation";
import { drawWorld } from "./world-art";

const replaySources = [
  "/runs/passive-7319.json",
  "/runs/caretaker-7319.json",
  "/runs/codex-7319.json",
] as const;

function controllerLabel(controller: AgentReplay["controller"]) {
  return ({ passive: "No-action baseline", scripted: "Fixed local policy", llm: "LLM structured play" } as const)[controller];
}

function percent(value: number) {
  return `${Math.round(value * 100)}%`;
}

function ActionDescription({ action }: { action: AgentReplay["turns"][number]["action"] }) {
  const target = "target" in action ? action.target : "target_zone" in action ? action.target_zone.replaceAll("_", " ") : null;
  return (
    <div className="study-action">
      <span className={`action-token action-${action.action}`}>{action.action}</span>
      {target && <strong>{target}</strong>}
      <p>{action.public_reason}</p>
      {action.belief_updates?.map((belief) => (
        <div className="belief-chip" key={`${belief.subject}-${belief.belief}`}>
          <span>{belief.confidence}</span>
          <p><b>{belief.subject}:</b> {belief.belief}</p>
        </div>
      ))}
    </div>
  );
}

export function AgentStudy({ open, onClose }: { open: boolean; onClose: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const [replays, setReplays] = useState<AgentReplay[]>([]);
  const [multiSeed, setMultiSeed] = useState<MultiSeedStudy | null>(null);
  const [runIndex, setRunIndex] = useState(2);
  const [turnIndex, setTurnIndex] = useState(0);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!open || replays.length) return;
    Promise.all([
      Promise.all(replaySources.map((source) => fetch(source).then((response) => {
        if (!response.ok) throw new Error(`Could not load ${source}`);
        return response.json() as Promise<AgentReplay>;
      }))),
      fetch("/runs/multiseed-v02.json").then((response) => {
        if (!response.ok) throw new Error("Could not load the multi-seed study");
        return response.json() as Promise<MultiSeedStudy>;
      }),
    ])
      .then(([loadedReplays, study]) => { setReplays(loadedReplays); setMultiSeed(study); })
      .catch((reason: Error) => setError(reason.message));
  }, [open, replays.length]);

  const replay = replays[runIndex] ?? null;
  const turn = replay?.turns[Math.min(turnIndex, replay.turns.length - 1)] ?? null;
  const world = turn?.world ?? replay?.initial_world ?? null;
  const turnStartBeat = turn?.observation.beat ?? -1;
  const turnCauses = (world?.causalEvents ?? []).filter((event) => event.beat > turnStartBeat).slice(-4).reverse();
  const firstIntervention = replay?.turns.find((item) => item.world.causalEvents.some((event) => event.kind === "intervention")) ?? null;

  useEffect(() => {
    if (!open || !world || !canvasRef.current) return;
    const context = canvasRef.current.getContext("2d");
    if (!context) return;
    const selected = turn?.action && "target" in turn.action ? turn.action.target : null;
    drawWorld(context, world, selected, null, "none");
  }, [open, turn, world]);

  useEffect(() => {
    if (!open) return;
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose, open]);

  const maxTurns = useMemo(() => replays.reduce((maximum, item) => Math.max(maximum, item.turns.length), 0), [replays]);
  if (!open) return null;

  return (
    <div className="study-scrim" role="dialog" aria-modal="true" aria-labelledby="study-title">
      <section className="study-shell">
        <header className="study-header">
          <div>
            <p className="eyebrow">Agent compatibility study · mechanics v0.2 · seed 7319</p>
            <h2 id="study-title">Same clearing. Three kinds of attention.</h2>
            <p>Each controller receives twelve decision windows. The LLM sees qualitative local observations—not coordinates, hidden relationships, signal values, or action scores.</p>
          </div>
          <button className="study-close" onClick={onClose} aria-label="Close agent study">×</button>
        </header>

        {error ? <p className="study-error">{error}</p> : !replay ? <p className="study-loading">Loading recorded field histories…</p> : (
          <>
            <nav className="run-tabs" aria-label="Recorded runs">
              {replays.map((item, index) => (
                <button key={item.id} className={runIndex === index ? "active" : ""} onClick={() => { setRunIndex(index); setTurnIndex(0); }}>
                  <span>{String(index + 1).padStart(2, "0")}</span>
                  <strong>{item.label}</strong>
                  <small>{controllerLabel(item.controller)}</small>
                </button>
              ))}
            </nav>

            <div className="study-stage">
              <div className="replay-visual">
                <canvas ref={canvasRef} width={WORLD_WIDTH} height={WORLD_HEIGHT} aria-label={`Recorded clearing at turn ${turnIndex + 1}`} />
                <div className="replay-stamp"><span>Recorded state</span><strong>Turn {turnIndex + 1} · beat {turn?.after.beat ?? 0}</strong></div>
              </div>

              <aside className="decision-inspector">
                <div className="inspector-heading">
                  <div><span>Decision record</span><strong>{turn ? `Turn ${turn.turn}` : "Initial state"}</strong></div>
                  <small>{turn?.observation.focus ?? replay.initial_world.focus} focus available</small>
                </div>
                {turn && (
                  <>
                    <div className="agent-observation">
                      <span className="inspector-label">Local observation</span>
                      <p className="observation-meta">{turn.observation.phase.replaceAll("_", " ")} · {turn.observation.observer_zone.replaceAll("_", " ")}</p>
                      {turn.observation.visible_creatures.length ? (
                        <ul>
                          {turn.observation.visible_creatures.map((creature) => (
                            <li key={creature.id}>
                              <div><strong>{creature.name}</strong><span>{creature.species} · {creature.distance.replace("_", " ")}</span></div>
                              <p>{creature.condition}; {creature.behavior}. {creature.notable_cue}</p>
                            </li>
                          ))}
                        </ul>
                      ) : <p className="no-observation">No creature was locally visible.</p>}
                    </div>
                    <div className="agent-decision">
                      <span className="inspector-label">Chosen action</span>
                      <ActionDescription action={turn.action} />
                      <p className="action-outcome"><span>Outcome</span>{turn.outcome}</p>
                    </div>
                    <div className="causal-ledger">
                      <span className="inspector-label">Causal ledger</span>
                      {turnCauses.length ? turnCauses.map((event) => (
                        <div className="cause-entry" key={event.id}>
                          <span>{event.kind.replace("-", " ")} · beat {event.beat}</span>
                          <strong>{event.summary}</strong>
                          <p>{event.effect}{event.parentId ? ` Linked to ${event.parentId}.` : ""}</p>
                        </div>
                      )) : <p className="no-observation">No material transition was recorded in this window.</p>}
                    </div>
                  </>
                )}
              </aside>
            </div>

            <div className="turn-scrubber">
              <button disabled={turnIndex <= 0} onClick={() => setTurnIndex((value) => Math.max(0, value - 1))}>←</button>
              <div>
                <div className="scrubber-label"><span>Decision timeline</span><strong>{turnIndex + 1} / {replay.turns.length}</strong></div>
                <input type="range" min="0" max={Math.max(0, replay.turns.length - 1)} value={Math.min(turnIndex, replay.turns.length - 1)} onChange={(event) => setTurnIndex(Number(event.target.value))} aria-label="Replay turn" />
                <div className="turn-marks" aria-hidden="true">{Array.from({ length: maxTurns }, (_, index) => <i key={index} />)}</div>
              </div>
              <button disabled={turnIndex >= replay.turns.length - 1} onClick={() => setTurnIndex((value) => Math.min(replay.turns.length - 1, value + 1))}>→</button>
            </div>

            <section className="comparison-section">
              <div className="comparison-title">
                <div><p className="eyebrow">Outcome comparison</p><h3>Evidence, not a morality score.</h3></div>
                <details>
                  <summary>LLM player contract</summary>
                  <div className="contract-grid">
                    <span><b>Observe</b> Local qualitative cues and visible events</span>
                    <span><b>Act</b> Move, observe, attend, nourish, ward, or wait</span>
                    <span><b>Explain</b> One concise public reason and optional belief update</span>
                    <span><b>Never receives</b> Hidden state, field values, or evaluator traces</span>
                  </div>
                </details>
              </div>
              <div className="comparison-table" role="table" aria-label="Run outcome comparison">
                <div className="comparison-row comparison-head" role="row">
                  <span role="columnheader">Run</span><span role="columnheader">Interventions</span><span role="columnheader">Resource vitality</span><span role="columnheader">Avg. energy</span><span role="columnheader">Hazard exposure</span><span role="columnheader">Witness memories</span><span role="columnheader">Observer trust</span>
                </div>
                {replays.map((item, index) => (
                  <button className={`comparison-row ${runIndex === index ? "selected" : ""}`} role="row" key={item.id} onClick={() => { setRunIndex(index); setTurnIndex(item.turns.length - 1); }}>
                    <strong role="cell">{item.label}</strong>
                    <span role="cell">{item.final_summary.interventions}</span>
                    <span role="cell">{percent(item.final_summary.resource_vitality)}</span>
                    <span role="cell">{percent(item.final_summary.average_energy)}</span>
                    <span role="cell">{item.final_summary.hazard_exposure_beats} beats</span>
                    <span role="cell">{item.final_summary.witnessed_memories}</span>
                    <span role="cell">{percent(item.final_summary.average_observer_trust)}</span>
                  </button>
                ))}
              </div>
              {multiSeed && (
                <div className="multi-seed-study">
                  <div className="multi-seed-heading">
                    <div><span>Five-seed mechanics check</span><strong>Do these differences survive a change of history?</strong></div>
                    <small>{multiSeed.seeds.join(" · ")} · {multiSeed.decision_windows} windows each</small>
                  </div>
                  <div className="multi-seed-grid">
                    {multiSeed.controllers.map((controller) => (
                      <article key={controller.id}>
                        <span>{controller.label}</span>
                        <div><strong>{percent(controller.mean.resource_vitality)}</strong><small>mean resource vitality</small></div>
                        <div><strong>{percent(controller.mean.average_energy)}</strong><small>mean creature energy</small></div>
                        <div><strong>{controller.mean.hazard_exposure_beats.toFixed(1)}</strong><small>hazard-contact beats</small></div>
                        <p>{controller.mean.interventions.toFixed(1)} interventions · {controller.mean.witnessed_memories.toFixed(1)} witnessed memories</p>
                      </article>
                    ))}
                  </div>
                  <p>{multiSeed.note} Seed ranges remain available in the recorded report; these means are descriptive, not statistical proof.</p>
                </div>
              )}
              {replay.controller === "passive" ? (
                <p className="study-footnote">This unattended run establishes what the same seeded clearing does without observer decisions. Its transitions still appear in the causal ledger, but none originate with an intervention.</p>
              ) : (
                <p className="study-footnote"><b>First intentional fork:</b> turn {firstIntervention?.turn ?? "none"}. This is not a goodness score: compare material vitality, creature energy, hazard contact, and witnessed treatment together. An intervention can improve one condition while worsening another.</p>
              )}
            </section>
          </>
        )}
      </section>
    </div>
  );
}
