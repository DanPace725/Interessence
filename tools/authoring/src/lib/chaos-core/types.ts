export type EdgeType = 'constraint' | 'influence' | 'info' | 'meta';

export interface RPConstraints {
  [key: string]: unknown;
}

export interface RPEntity {
  id: string;
  type: string;
  position: { x: number; y: number; z: number };
  velocity: { x: number; y: number; z: number };
  
  // RP Fingerprint (0-1 intensities)
  /** P1: Identity/Ontology - what this entity IS */
  P1_identity: number;
  /** P2: Dynamics - activity, motion, energy level */
  P2_dynamics: number;
  /** P3: Geometry - spatial/conceptual closeness weight */
  P3_geometry: number;
  /** P4: Constraints - boundary rigidity, structure */
  P4_constraints: number;
  /** P5: Epistemic - visibility, knowledge, accessibility */
  P5_epistemic: number;
  /** P6: Meta - meta-relational importance, abstraction level */
  P6_meta: number;
  
  constraints?: RPConstraints;
  metaTags?: string[];
}

export interface RPRelation {
  source: string;
  target: string;
  weight: number;
  type: EdgeType;
}

/**
 * Factory function to create an RPEntity with defaults
 */
export function createRPEntity(
  id: string,
  type: string,
  overrides: Partial<Omit<RPEntity, 'id' | 'type'>> = {}
): RPEntity {
  const entity: RPEntity = {
    id,
    type,
    position: overrides.position ?? { x: 0, y: 0, z: 0 },
    velocity: overrides.velocity ?? { x: 0, y: 0, z: 0 },
    
    // RP Fingerprint defaults (random or specified)
    P1_identity: overrides.P1_identity ?? Math.random(),
    P2_dynamics: overrides.P2_dynamics ?? Math.random(),
    P3_geometry: overrides.P3_geometry ?? Math.random(),
    P4_constraints: overrides.P4_constraints ?? Math.random(),
    P5_epistemic: overrides.P5_epistemic ?? Math.random(),
    P6_meta: overrides.P6_meta ?? Math.random(),
    
    constraints: overrides.constraints ?? {},
    metaTags: overrides.metaTags ?? []
  };
  return entity;
}
