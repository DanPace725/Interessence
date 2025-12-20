import { subscribe, getPacks } from '../state/store';
import { renderGraph } from './graph';
import { renderSignal } from './signal';

export function initVisuals() {
  const graphCanvas = document.getElementById('graph-view') as HTMLCanvasElement | null;
  const signalCanvas = document.getElementById('signal-view') as HTMLCanvasElement | null;

  const redraw = () => {
    const packs = getPacks();
    if (graphCanvas) renderGraph(graphCanvas, packs.worldText);
    if (signalCanvas) renderSignal(signalCanvas, packs.worldText, packs.signalText);
  };

  redraw();
  subscribe(redraw);
}
