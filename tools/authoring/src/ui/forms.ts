import heuristicsSchema from '@schemas/heuristics-pack.schema.json';
import worldSchema from '@schemas/world-pack.schema.json';
import signalSchema from '@schemas/signal-pack.schema.json';
import { logError } from './log';
import { setPack, getPacks, subscribe } from '../state/store';

type HeuristicsSchema = typeof heuristicsSchema;

function buildHeuristicsForm(container: HTMLElement, data: any, schema: HeuristicsSchema) {
  container.innerHTML = '';
  const params = (schema as any).properties?.parameters?.properties || {};
  const current = (data && typeof data === 'object' && (data as any).parameters) || {};

  Object.entries(params).forEach(([key, def]: [string, any]) => {
    const row = document.createElement('div');
    row.className = 'form-row';
    const label = document.createElement('label');
    label.textContent = key;
    row.appendChild(label);

    if (def.type === 'boolean') {
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!current[key];
      input.addEventListener('change', () => {
        current[key] = input.checked;
        syncHeuristics(container, current);
      });
      row.appendChild(input);
    } else {
      const input = document.createElement('input');
      input.type = 'number';
      input.step = '0.01';
      if (typeof current[key] === 'number') input.value = String(current[key]);
      input.addEventListener('input', () => {
        const v = Number(input.value);
        if (!Number.isNaN(v)) {
          current[key] = v;
          syncHeuristics(container, current);
        }
      });
      row.appendChild(input);
    }

    container.appendChild(row);
  });
}

function syncHeuristics(container: HTMLElement, parameters: Record<string, unknown>) {
  // Merge back into full pack
  let parsed: any = {};
  try {
    parsed = JSON.parse(getPacks().heuristicsText || '{}');
  } catch {
    // ignore
  }
  parsed.schemaVersion = parsed.schemaVersion || '0.1.0';
  parsed.metadata = parsed.metadata || { name: 'Heuristics' };
  parsed.parameters = { ...(parsed.parameters || {}), ...parameters };
  const text = JSON.stringify(parsed, null, 2);
  const ta = document.getElementById('heuristics-pack') as HTMLTextAreaElement | null;
  if (ta) ta.value = text;
  setPack('heuristics', text);
}

export function initForms() {
  const heuristicsContainer = document.getElementById('heuristics-form');
  const worldContainer = document.getElementById('world-form');
  const signalContainer = document.getElementById('signal-form');

  const render = () => {
    const packs = getPacks();
    // Heuristics
    if (heuristicsContainer) {
      try {
        const parsed = JSON.parse(packs.heuristicsText || '{}');
        buildHeuristicsForm(heuristicsContainer, parsed, heuristicsSchema as HeuristicsSchema);
      } catch (err) {
        heuristicsContainer.innerHTML = '';
        logError(`Heuristics JSON invalid: ${(err as Error).message}`);
      }
    }
    // World
    if (worldContainer) {
      try {
        const parsed = JSON.parse(packs.worldText || '{}');
        buildWorldForm(worldContainer, parsed, worldSchema as any);
      } catch (err) {
        worldContainer.innerHTML = '';
        logError(`World JSON invalid: ${(err as Error).message}`);
      }
    }
    // Signal
    if (signalContainer) {
      try {
        const parsed = JSON.parse(packs.signalText || '{}');
        buildSignalForm(signalContainer, parsed, signalSchema as any);
      } catch (err) {
        signalContainer.innerHTML = '';
        logError(`Signal JSON invalid: ${(err as Error).message}`);
      }
    }
  };

  render();
  subscribe(render);
}

// Helpers for nested path get/set
function getAtPath(obj: any, path: string[], fallback: any) {
  let cur = obj;
  for (const p of path) {
    if (cur && typeof cur === 'object' && p in cur) cur = cur[p];
    else return fallback;
  }
  return cur;
}

function setAtPath(obj: any, path: string[], value: any) {
  let cur = obj;
  for (let i = 0; i < path.length - 1; i++) {
    const p = path[i];
    if (!cur[p] || typeof cur[p] !== 'object') cur[p] = {};
    cur = cur[p];
  }
  cur[path[path.length - 1]] = value;
}

function buildWorldForm(container: HTMLElement, data: any, _schema: any) {
  container.innerHTML = '';
  const fields: Array<{ label: string; path: string[]; type: 'number' | 'boolean' }> = [
    { label: 'plantEcology', path: ['toggles', 'plantEcology'], type: 'boolean' },
    { label: 'adaptiveReward', path: ['toggles', 'adaptiveReward'], type: 'boolean' },
    { label: 'scentGradient', path: ['toggles', 'scentGradient'], type: 'boolean' },
    { label: 'mitosis', path: ['toggles', 'mitosis'], type: 'boolean' },
    { label: 'decay', path: ['toggles', 'decay'], type: 'boolean' },
    { label: 'signalField', path: ['toggles', 'signalField'], type: 'boolean' },
    { label: 'participation', path: ['toggles', 'participation'], type: 'boolean' },
    { label: 'autonomy', path: ['toggles', 'autonomy'], type: 'boolean' },
    { label: 'rendering', path: ['toggles', 'rendering'], type: 'boolean' },

    { label: 'resourceRadius', path: ['geometry', 'resourceRadius'], type: 'number' },
    { label: 'trailCell', path: ['geometry', 'trailCell'], type: 'number' },
    { label: 'fertilityCell', path: ['geometry', 'fertilityCell'], type: 'number' },
    { label: 'patchRadius', path: ['geometry', 'patchRadius'], type: 'number' },
    { label: 'harvestRadius', path: ['geometry', 'harvestRadius'], type: 'number' },
    { label: 'scentMaxRange', path: ['geometry', 'scentMaxRange'], type: 'number' },
    { label: 'linkRadius', path: ['geometry', 'linkRadius'], type: 'number' },
    { label: 'wallAvoidMargin', path: ['geometry', 'wallAvoidMargin'], type: 'number' },
    { label: 'sampleDistance', path: ['geometry', 'sampleDistance'], type: 'number' },

    { label: 'maxAgents', path: ['constraints', 'maxAgents'], type: 'number' },
    { label: 'resourceRespawnCooldown', path: ['constraints', 'resourceRespawnCooldown'], type: 'number' },
    { label: 'adaptiveRewardMin', path: ['constraints', 'adaptiveRewardMin'], type: 'number' },
    { label: 'adaptiveRewardMax', path: ['constraints', 'adaptiveRewardMax'], type: 'number' },

    { label: 'resourceInitialMin', path: ['ecology', 'resourceInitialMin'], type: 'number' },
    { label: 'resourceInitialMax', path: ['ecology', 'resourceInitialMax'], type: 'number' },
    { label: 'resourceStableMin', path: ['ecology', 'resourceStableMin'], type: 'number' },
    { label: 'resourceStableMax', path: ['ecology', 'resourceStableMax'], type: 'number' },
    { label: 'resourceDepletionRate', path: ['ecology', 'resourceDepletionRate'], type: 'number' },
    { label: 'resourceRecoveryChance', path: ['ecology', 'resourceRecoveryChance'], type: 'number' },
    { label: 'resourceScaleWithAgents', path: ['ecology', 'resourceScaleWithAgents'], type: 'boolean' },
    { label: 'resourceBaseAbundance', path: ['ecology', 'resourceBaseAbundance'], type: 'number' },
    { label: 'resourceCompetition', path: ['ecology', 'resourceCompetition'], type: 'number' },

    { label: 'plant initialFertility', path: ['ecology', 'plantEcology', 'initialFertility'], type: 'number' },
    { label: 'plant fertilityVariation', path: ['ecology', 'plantEcology', 'fertilityVariation'], type: 'number' },
    { label: 'plant seedChance', path: ['ecology', 'plantEcology', 'seedChance'], type: 'number' },
    { label: 'plant seedDistance', path: ['ecology', 'plantEcology', 'seedDistance'], type: 'number' },
    { label: 'plant growthThreshold', path: ['ecology', 'plantEcology', 'growthFertilityThreshold'], type: 'number' },
    { label: 'plant growthChance', path: ['ecology', 'plantEcology', 'growthChance'], type: 'number' },
    { label: 'plant patchCount', path: ['ecology', 'plantEcology', 'patchCount'], type: 'number' },
    { label: 'plant patchRadius', path: ['ecology', 'plantEcology', 'patchRadius'], type: 'number' }
  ];

  const parsed = data && typeof data === 'object' ? data : {};

  fields.forEach((f) => {
    const row = document.createElement('div');
    row.className = 'form-row';
    const label = document.createElement('label');
    label.textContent = f.label;
    row.appendChild(label);

    if (f.type === 'boolean') {
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!getAtPath(parsed, f.path, false);
      input.addEventListener('change', () => {
        setAtPath(parsed, f.path, input.checked);
        syncWorld(parsed);
      });
      row.appendChild(input);
    } else {
      const input = document.createElement('input');
      input.type = 'number';
      input.step = '0.01';
      const val = getAtPath(parsed, f.path, '');
      if (typeof val === 'number') input.value = String(val);
      input.addEventListener('input', () => {
        const v = Number(input.value);
        if (!Number.isNaN(v)) {
          setAtPath(parsed, f.path, v);
          syncWorld(parsed);
        }
      });
      row.appendChild(input);
    }
    container.appendChild(row);
  });
}

function syncWorld(parsed: any) {
  const text = JSON.stringify(parsed, null, 2);
  const ta = document.getElementById('world-pack') as HTMLTextAreaElement | null;
  if (ta) ta.value = text;
  setPack('world', text);
}

function buildSignalForm(container: HTMLElement, data: any, _schema: any) {
  container.innerHTML = '';
  const parsed = data && typeof data === 'object' ? data : {};
  const fields: Array<{ label: string; path: string[]; type: 'number' | 'boolean' }> = [
    { label: 'cellSize', path: ['field', 'cellSize'], type: 'number' },
    { label: 'decayPerSec', path: ['field', 'decayPerSec'], type: 'number' },
    { label: 'diffusePerSec', path: ['field', 'diffusePerSec'], type: 'number' },
    { label: 'channels', path: ['field', 'channels'], type: 'number' },
    { label: 'memoryLength', path: ['field', 'memoryLength'], type: 'number' },
    { label: 'activationThreshold', path: ['field', 'activationThreshold'], type: 'number' },
    { label: 'participation.enabled', path: ['participation', 'enabled'], type: 'boolean' },
    { label: 'participation.maxForceFraction', path: ['participation', 'maxForceFraction'], type: 'number' },
    { label: 'participation.resource.radius', path: ['participation', 'modes', 'resource', 'radius'], type: 'number' },
    { label: 'participation.resource.strength', path: ['participation', 'modes', 'resource', 'strength'], type: 'number' },
    { label: 'participation.distress.radius', path: ['participation', 'modes', 'distress', 'radius'], type: 'number' },
    { label: 'participation.distress.strength', path: ['participation', 'modes', 'distress', 'strength'], type: 'number' },
    { label: 'participation.bond.radius', path: ['participation', 'modes', 'bond', 'radius'], type: 'number' },
    { label: 'participation.bond.strength', path: ['participation', 'modes', 'bond', 'strength'], type: 'number' }
  ];

  fields.forEach((f) => {
    const row = document.createElement('div');
    row.className = 'form-row';
    const label = document.createElement('label');
    label.textContent = f.label;
    row.appendChild(label);

    if (f.type === 'boolean') {
      const input = document.createElement('input');
      input.type = 'checkbox';
      input.checked = !!getAtPath(parsed, f.path, false);
      input.addEventListener('change', () => {
        setAtPath(parsed, f.path, input.checked);
        syncSignal(parsed);
      });
      row.appendChild(input);
    } else {
      const input = document.createElement('input');
      input.type = 'number';
      input.step = '0.01';
      const val = getAtPath(parsed, f.path, '');
      if (typeof val === 'number') input.value = String(val);
      input.addEventListener('input', () => {
        const v = Number(input.value);
        if (!Number.isNaN(v)) {
          setAtPath(parsed, f.path, v);
          syncSignal(parsed);
        }
      });
      row.appendChild(input);
    }
    container.appendChild(row);
  });
}

function syncSignal(parsed: any) {
  const text = JSON.stringify(parsed, null, 2);
  const ta = document.getElementById('signal-pack') as HTMLTextAreaElement | null;
  if (ta) ta.value = text;
  setPack('signal', text);
}
