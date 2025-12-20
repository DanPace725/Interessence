import Ajv from 'ajv';
import addFormats from 'ajv-formats';
import worldSchema from '@schemas/world-pack.schema.json';
import heuristicsSchema from '@schemas/heuristics-pack.schema.json';
import signalSchema from '@schemas/signal-pack.schema.json';

const ajv = new Ajv({ 
  allErrors: true, 
  strict: false,
  validateSchema: false // Skip meta-schema validation for Draft 2020-12 compatibility
});
addFormats(ajv);

const validators = {
  world: ajv.compile(worldSchema as object),
  heuristics: ajv.compile(heuristicsSchema as object),
  signal: ajv.compile(signalSchema as object)
};

export function validatePack(kind: 'world' | 'heuristics' | 'signal', data: unknown) {
  const validate = validators[kind];
  const ok = validate(data);
  return {
    valid: !!ok,
    errors: validate.errors ?? []
  };
}
