type Listener = () => void;

interface PacksState {
  worldText: string;
  heuristicsText: string;
  signalText: string;
}

const state: PacksState = {
  worldText: '',
  heuristicsText: '',
  signalText: ''
};

const listeners: Listener[] = [];

export function setPack(kind: 'world' | 'heuristics' | 'signal', text: string) {
  if (kind === 'world') state.worldText = text;
  if (kind === 'heuristics') state.heuristicsText = text;
  if (kind === 'signal') state.signalText = text;
  listeners.forEach((fn) => fn());
}

export function getPacks(): PacksState {
  return { ...state };
}

export function subscribe(fn: Listener) {
  listeners.push(fn);
  return () => {
    const idx = listeners.indexOf(fn);
    if (idx >= 0) listeners.splice(idx, 1);
  };
}
