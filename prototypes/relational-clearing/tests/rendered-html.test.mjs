import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

async function render() {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the Relational Clearing shell", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /<title>The Relational Clearing<\/title>/i);
  assert.match(html, /Interessence field study 01/i);
  assert.match(html, /A small ecology of memory, partial knowledge, and consequence/i);
  assert.match(html, /Open agent study/i);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton|Your site is taking shape/i);
});

test("keeps the prototype deterministic and explicitly relational", async () => {
  const [page, simulation, art, packageJson] = await Promise.all([
    readFile(new URL("app/page.tsx", root), "utf8"),
    readFile(new URL("app/simulation.ts", root), "utf8"),
    readFile(new URL("app/world-art.ts", root), "utf8"),
    readFile(new URL("package.json", root), "utf8"),
  ]);
  assert.match(page, /Replay same seed/);
  assert.match(page, /Relational memory/);
  assert.match(page, /Why this action\?/);
  assert.match(page, /AgentStudy/);
  assert.match(simulation, /rngState/);
  assert.match(simulation, /trustObserver/);
  assert.match(simulation, /changeBond/);
  assert.doesNotMatch(simulation, /Math\.random/);
  assert.match(art, /drawBrambleback/);
  assert.match(art, /drawWickwing/);
  assert.match(art, /drawMirehorn/);
  assert.doesNotMatch(packageJson, /react-loading-skeleton/);
});
