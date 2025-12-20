import { setupPackEditor } from './ui/packs';
import { initVisuals } from './ui/visuals';
import { initForms } from './ui/forms';
import { log } from './ui/log';
import { compilePacks } from './lib/runtime-loader';
import { getPacks } from './state/store';
import { initPreview } from './ui/preview';

function init() {
  setupPackEditor();
  initVisuals();
  initForms();
  initPreview();
  // Quick sanity compile on load
  const bundle = compilePacks('', '', '');
  if (!bundle.ok) {
    log('Bundle compile will run after packs load.');
  } else {
    log('Bundle compiler ready.');
  }
  // Attach a debug compile button (validate already exists)
  const validateBtn = document.getElementById('validate');
  validateBtn?.addEventListener('click', () => {
    const packs = getPacks();
    const result = compilePacks(packs.worldText, packs.heuristicsText, packs.signalText);
    if (!result.ok) {
      result.errors.forEach((e) => log(`Compile error: ${e}`));
    } else {
      log('Compiled bundle successfully.');
    }
  });
  log('Authoring UI loaded. Use Load Packs or paste JSON into the text areas.');
}

init();
