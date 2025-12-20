import { RelationalField } from '../lib/chaos-core/field';
import { RPEntity } from '../lib/chaos-core/types';

interface WorldPack {
  entities?: Array<{
    id: string;
    kind: string;
    position?: { x: number; y: number; z?: number };
    rp?: Partial<RPEntity>;
  }>;
}

interface SignalPack {
  field?: {
    cellSize?: number;
    decayPerSec?: number;
    diffusePerSec?: number;
    channels?: number;
    memoryLength?: number;
    activationThreshold?: number;
  };
}

export function renderSignal(canvas: HTMLCanvasElement, worldText: string, signalText: string) {
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const { width, height } = canvas.getBoundingClientRect();
  canvas.width = width;
  canvas.height = height;
  ctx.clearRect(0, 0, width, height);
  ctx.fillStyle = '#0e131d';
  ctx.fillRect(0, 0, width, height);

  let parsed: WorldPack;
  let signal: SignalPack = {};
  try {
    parsed = JSON.parse(worldText || '{}');
  } catch {
    ctx.fillStyle = '#f26d6d';
    ctx.fillText('World pack JSON invalid', 10, 20);
    return;
  }
  try {
    signal = JSON.parse(signalText || '{}');
  } catch {
    // ignore
  }

  const rpDefaults = { P1_identity: 0.5, P2_dynamics: 0.5, P3_geometry: 0.5, P4_constraints: 0.5, P5_epistemic: 0.5, P6_meta: 0.5 };
  const entities: RPEntity[] = (parsed.entities || []).map((e) => {
    const pos = e.position || { x: Math.random() * width, y: Math.random() * height, z: 0 };
    return {
      id: e.id,
      type: e.kind,
      position: { x: pos.x, y: pos.y, z: pos.z ?? 0 },
      velocity: { x: 0, y: 0, z: 0 },
      ...rpDefaults,
      ...(e.rp || {})
    };
  });

  const field = new RelationalField(entities);
  const cellSize = signal.field?.cellSize ?? 10;
  const cols = Math.max(8, Math.floor(width / cellSize));
  const rows = Math.max(6, Math.floor(height / cellSize));
  const cellW = width / cols;
  const cellH = height / rows;

  let maxVal = -Infinity;
  let minVal = Infinity;
  const values: number[] = [];

  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const sample = { x: i * cellW, y: j * cellH, z: 0 };
      const v = field.calculateField(sample);
      values.push(v);
      if (v > maxVal) maxVal = v;
      if (v < minVal) minVal = v;
    }
  }

  const range = maxVal - minVal || 1;
  let idx = 0;
  for (let j = 0; j < rows; j++) {
    for (let i = 0; i < cols; i++) {
      const v = values[idx++];
      const t = (v - minVal) / range;
      const r = Math.floor(30 + 180 * t);
      const g = Math.floor(60 + 120 * t);
      const b = 255 - Math.floor(180 * t);
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(i * cellW, j * cellH, cellW + 1, cellH + 1);
    }
  }
}
