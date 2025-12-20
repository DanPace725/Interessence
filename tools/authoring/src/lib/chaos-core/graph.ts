import { RPEntity, RPRelation } from './types';

export class RPGraph {
  private entities: Map<string, RPEntity>;
  private relations: RPRelation[];

  constructor() {
    this.entities = new Map();
    this.relations = [];
  }

  addEntity(entity: RPEntity): void {
    if (this.entities.has(entity.id)) {
      throw new Error(`Entity with ID '${entity.id}' already exists.`);
    }
    this.entities.set(entity.id, entity);
  }

  addRelation(relation: RPRelation): void {
    if (!this.entities.has(relation.source)) {
      throw new Error(`Source entity '${relation.source}' does not exist.`);
    }
    if (!this.entities.has(relation.target)) {
      throw new Error(`Target entity '${relation.target}' does not exist.`);
    }
    this.relations.push(relation);
  }

  getEntity(id: string): RPEntity | undefined {
    return this.entities.get(id);
  }

  getEntities(): RPEntity[] {
    return Array.from(this.entities.values());
  }

  getRelations(): RPRelation[] {
    return this.relations;
  }

  clear(): void {
    this.entities.clear();
    this.relations = [];
  }

  toJSON() {
    return {
      nodes: this.getEntities(),
      edges: this.relations
    };
  }
}
