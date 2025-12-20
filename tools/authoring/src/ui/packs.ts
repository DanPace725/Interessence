import { log, logError } from './log';
import { validatePack } from '../lib/validation';
import { setPack } from '../state/store';

function safeParse(text: string) {
  try {
    return { data: JSON.parse(text) as unknown, error: null };
  } catch (err) {
    return { data: null, error: (err as Error).message };
  }
}

export function setupPackEditor() {
  const worldArea = document.getElementById('world-pack') as HTMLTextAreaElement | null;
  const heuristicsArea = document.getElementById('heuristics-pack') as HTMLTextAreaElement | null;
  const signalArea = document.getElementById('signal-pack') as HTMLTextAreaElement | null;
  const loadBtn = document.getElementById('load-packs');
  const loadSampleBtn = document.getElementById('load-sample');
  const saveBtn = document.getElementById('save-packs');
  const validateBtn = document.getElementById('validate');

  loadBtn?.addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.multiple = true;
    input.onchange = async () => {
      if (!input.files) return;
      for (const file of Array.from(input.files)) {
        const text = await file.text();
        if (file.name.includes('world') && worldArea) {
          worldArea.value = text;
          setPack('world', text);
        } else if (file.name.includes('heuristics') && heuristicsArea) {
          heuristicsArea.value = text;
          setPack('heuristics', text);
        } else if (file.name.includes('signal') && signalArea) {
          signalArea.value = text;
          setPack('signal', text);
        }
      }
      log('Loaded selected JSON files into editors.');
    };
    input.click();
  });

  loadSampleBtn?.addEventListener('click', async () => {
    try {
      const [world, heuristics, signal] = await Promise.all([
        fetch('/samples/forest-world-pack.json').then((r) => r.text()),
        fetch('/samples/forest-heuristics-pack.json').then((r) => r.text()),
        fetch('/samples/forest-signal-pack.json').then((r) => r.text())
      ]);
      if (worldArea) {
        worldArea.value = world;
        setPack('world', world);
      }
      if (heuristicsArea) {
        heuristicsArea.value = heuristics;
        setPack('heuristics', heuristics);
      }
      if (signalArea) {
        signalArea.value = signal;
        setPack('signal', signal);
      }
      log('Loaded sample forest packs.');
    } catch (err) {
      logError(`Failed to load samples: ${(err as Error).message}`);
    }
  });

  validateBtn?.addEventListener('click', () => {
    const blocks = [
      { name: 'world', area: worldArea },
      { name: 'heuristics', area: heuristicsArea },
      { name: 'signal', area: signalArea }
    ];
    for (const block of blocks) {
      if (!block.area) continue;
      const { data, error } = safeParse(block.area.value || '{}');
      if (error) {
        logError(`${block.name} pack JSON invalid: ${error}`);
        return;
      }
      const result = validatePack(block.name as 'world' | 'heuristics' | 'signal', data);
      if (!result.valid) {
        const msg = result.errors.map(e => `${e.instancePath || '/'} ${e.message || ''}`).join('; ');
        logError(`${block.name} pack failed schema: ${msg}`);
        return;
      }
    }
    log('All packs are valid against their schemas.');
  });

  saveBtn?.addEventListener('click', () => {
    const files = [
      { name: 'world-pack.json', area: worldArea },
      { name: 'heuristics-pack.json', area: heuristicsArea },
      { name: 'signal-pack.json', area: signalArea }
    ];
    for (const f of files) {
      if (!f.area) continue;
      const blob = new Blob([f.area.value], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = f.name;
      a.click();
      URL.revokeObjectURL(url);
    }
    log('Exported packs to downloads.');
  });

  // Live state updates when user types
  worldArea?.addEventListener('input', () => setPack('world', worldArea.value));
  heuristicsArea?.addEventListener('input', () => setPack('heuristics', heuristicsArea.value));
  signalArea?.addEventListener('input', () => setPack('signal', signalArea.value));
}
