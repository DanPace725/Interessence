import { compilePacks } from './runtime-loader';

interface EntityView {
  id: string;
  kind: string;
  x: number;
  y: number;
  chi: number;
  energy: number;
}

export interface PreviewState {
  entities: EntityView[];
}

// Placeholder: reuse compilePacks and a minimal JS tick (mirrors C++ logic lightly)
export function stepPreview(worldText: string, heuristicsText: string, signalText: string): PreviewState | null {
  const res = compilePacks(worldText, heuristicsText, signalText);
  if (!res.ok || !res.bundle) return null;

  const entities = res.bundle.entities.map((e) => ({
    id: e.id,
    kind: e.kind,
    x: e.position.x,
    y: e.position.y,
    chi: typeof e.state.chi === 'number' ? (e.state.chi as number) : 0,
    energy: typeof e.state.energy === 'number' ? (e.state.energy as number) : 0
  }));

  return { entities };
}
