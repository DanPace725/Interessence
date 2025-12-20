import { getPacks, subscribe } from '../state/store';
import { initRuntime, tickRuntime } from '../lib/js-runtime';

let sim: ReturnType<typeof initRuntime> | null = null;
let running = false;
let rafId: number | null = null;

export function initPreview() {
  const canvas = document.createElement('canvas');
  canvas.id = 'sim-view';
  canvas.width = 600;
  canvas.height = 400;
  const visuals = document.getElementById('visuals');
  if (visuals) visuals.appendChild(canvas);

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  const buildSim = () => {
    const packs = getPacks();
    sim = initRuntime(packs.worldText, packs.heuristicsText, packs.signalText);
  };

  const draw = () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#0e131d';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (!sim) {
      ctx.fillStyle = '#f26d6d';
      ctx.fillText('Preview unavailable (compile error)', 10, 20);
      return;
    }
    for (const e of sim.entities) {
      if (e.kind === 'resource') {
        ctx.fillStyle = '#4cd964';
        ctx.beginPath();
        ctx.arc(canvas.width / 2 + e.position.x, canvas.height / 2 + e.position.y, 6, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.fillStyle = '#4f6af3';
        ctx.beginPath();
        ctx.arc(canvas.width / 2 + e.position.x, canvas.height / 2 + e.position.y, 8, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#ffcc00';
        ctx.fillRect(canvas.width / 2 + e.position.x - 10, canvas.height / 2 + e.position.y - 14, Math.min(20, getNumber(e.state, 'chi', 0) * 0.2), 3);
        ctx.fillStyle = '#34c759';
        ctx.fillRect(canvas.width / 2 + e.position.x - 10, canvas.height / 2 + e.position.y - 10, Math.min(20, getNumber(e.state, 'energy', 0) * 0.2), 3);
      }
    }
  };

  const tickAndDraw = () => {
    if (sim) tickRuntime(sim);
    draw();
    if (running) {
      rafId = requestAnimationFrame(tickAndDraw);
    }
  };

  // Controls
  const startBtn = document.getElementById('sim-start');
  const stopBtn = document.getElementById('sim-stop');
  const stepBtn = document.getElementById('sim-step');
  startBtn?.addEventListener('click', () => {
    buildSim();
    running = true;
    if (rafId) cancelAnimationFrame(rafId);
    tickAndDraw();
  });
  stopBtn?.addEventListener('click', () => {
    running = false;
    if (rafId) cancelAnimationFrame(rafId);
  });
  stepBtn?.addEventListener('click', () => {
    if (!sim) buildSim();
    if (sim) tickRuntime(sim);
    draw();
  });

  const getNumber = (state: Record<string, any>, key: string, fallback = 0) => {
    const v = state[key];
    if (typeof v === 'number') return v;
    if (typeof v === 'boolean') return v ? 1 : 0;
    return fallback;
  };

  buildSim();
  draw();
  subscribe(() => {
    buildSim();
    draw();
  });
}
