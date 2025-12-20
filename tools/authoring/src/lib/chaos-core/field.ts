import { RPEntity } from './types';

interface Vector3 {
  x: number;
  y: number;
  z: number;
}

export class RelationalField {
  private entities: RPEntity[];

  // Field Constants
  private epsilon = 1.0; // Softening parameter (Equation 2)
  private falloffScale = 20.0; // Scale for radial falloff
  private epistemicRadius = 30.0; // Radius for full visibility (Equation 6)
  private occlusionAlpha = 0.2; // Attenuation factor outside radius

  constructor(entities: RPEntity[]) {
    this.entities = entities;
  }

  /**
   * Computes the scalar field value at a point F(x)
   * Equation 3: F(x) = Sum(F_i(x))
   */
  public calculateField(point: Vector3): number {
    let totalField = 0;

    for (const entity of this.entities) {
      totalField += this.computeInfluence(point, entity);
    }

    return totalField;
  }

  /**
   * Computes the influence of a single node F_i(x) at a point
   * Equation 2: F_i(x) = w_i / (|x-p_i|^2 + epsilon)
   * Includes attenuation for occlusion (Equation 6)
   */
  private computeInfluence(point: Vector3, entity: RPEntity): number {
    const dx = point.x - entity.position.x;
    const dy = point.y - entity.position.y;
    const dz = point.z - entity.position.z;
    const distSq = dx * dx + dy * dy + dz * dz;

    const weight = this.getInfluenceWeight(entity);

    // Equation 2: Inverse-square with softening
    // Using exponential falloff for smoother basins as per spec option
    // F_i(x) = w_i * exp(-distSq / sigma^2)
    let influence = weight * Math.exp(-distSq / (this.falloffScale * this.falloffScale));

    // Equation 6: Occlusion / Attenuation
    // If |x - p_i| > r_i, attenuate
    if (distSq > this.epistemicRadius * this.epistemicRadius) {
      influence *= this.occlusionAlpha;
    }

    return influence;
  }

  /**
   * Computes the gradient of the field at a point: grad F(x)
   * Equation 5: Vector pointing in direction of steepest ascent
   * We calculate analytical gradient of the sum of Gaussians
   */
  public calculateGradient(point: Vector3): Vector3 {
    const gradient = { x: 0, y: 0, z: 0 };

    for (const entity of this.entities) {
      const dx = point.x - entity.position.x;
      const dy = point.y - entity.position.y;
      const dz = point.z - entity.position.z;
      const distSq = dx * dx + dy * dy + dz * dz;

      const weight = this.getInfluenceWeight(entity);

      // Derivative of Gaussian:
      // d/dx (w * exp(-r^2/s^2)) = w * exp(...) * (-2x / s^2)

      const factor = -2.0 / (this.falloffScale * this.falloffScale);
      let influence = weight * Math.exp(-distSq / (this.falloffScale * this.falloffScale));

      // Apply Occlusion Attenuation to gradient too (simplified derivative approx)
      if (distSq > this.epistemicRadius * this.epistemicRadius) {
        influence *= this.occlusionAlpha;
      }

      // Contribution to gradient
      const gFactor = influence * factor;

      gradient.x += gFactor * dx;
      gradient.y += gFactor * dy;
      gradient.z += gFactor * dz;
    }

    return gradient;
  }

  /**
   * Derives influence weight w_i from RP fingerprint
   * P2_dynamics (positive) = Repulsor (Peak) - high activity pushes
   * P4_constraints (negative) = Attractor (Basin) - high constraints pull
   */
  private getInfluenceWeight(entity: RPEntity): number {
    const dynamicsWeight = 10.0; // P2 contribution
    const constraintWeight = 15.0; // P4 contribution (stronger attractors)

    // H = Dynamics (push up) - Constraints (pull down)
    return entity.P2_dynamics * dynamicsWeight - entity.P4_constraints * constraintWeight;
  }
}
