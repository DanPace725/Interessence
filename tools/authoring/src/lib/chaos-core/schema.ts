import { EdgeType } from './types';

export interface DatasetMetadata {
  name: string;
  description?: string;
  version?: string;
}

export interface RPFingerprint {
  P1_identity: number;
  P2_dynamics: number;
  P3_geometry: number;
  P4_constraints: number;
  P5_epistemic: number;
  P6_meta: number;
}

export interface DatasetNode {
  id: string;
  type: string;
  label?: string;
  rp?: Partial<RPFingerprint>;
}

export interface DatasetEdge {
  source: string;
  target: string;
  type: EdgeType;
  weight?: number;
}

export interface RPDataset {
  metadata: DatasetMetadata;
  nodes: DatasetNode[];
  edges: DatasetEdge[];
}

export function validateDataset(data: unknown): data is RPDataset {
  if (!data || typeof data !== 'object') return false;
  const d = data as RPDataset;
  if (!d.metadata || typeof d.metadata.name !== 'string') return false;
  if (!Array.isArray(d.nodes)) return false;
  for (const node of d.nodes) {
    if (typeof node.id !== 'string' || typeof node.type !== 'string') return false;
  }
  if (!Array.isArray(d.edges)) return false;
  for (const edge of d.edges) {
    if (typeof edge.source !== 'string' || typeof edge.target !== 'string') return false;
  }
  return true;
}

export function getDefaultRP(type: string): RPFingerprint {
  switch (type) {
    case 'file':
      return { P1_identity: 0.8, P2_dynamics: 0.3, P3_geometry: 0.5, P4_constraints: 0.7, P5_epistemic: 0.6, P6_meta: 0.4 };
    case 'class':
      return { P1_identity: 0.9, P2_dynamics: 0.4, P3_geometry: 0.6, P4_constraints: 0.8, P5_epistemic: 0.7, P6_meta: 0.5 };
    case 'function':
      return { P1_identity: 0.6, P2_dynamics: 0.7, P3_geometry: 0.4, P4_constraints: 0.5, P5_epistemic: 0.5, P6_meta: 0.3 };
    case 'module':
      return { P1_identity: 0.7, P2_dynamics: 0.2, P3_geometry: 0.8, P4_constraints: 0.9, P5_epistemic: 0.8, P6_meta: 0.6 };
    default:
      return { P1_identity: 0.5, P2_dynamics: 0.5, P3_geometry: 0.5, P4_constraints: 0.5, P5_epistemic: 0.5, P6_meta: 0.5 };
  }
}
