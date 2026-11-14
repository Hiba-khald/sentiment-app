import test from "node:test";
import assert from "node:assert/strict";
import client from "./client.js";

const reponse = (status, corps) => ({ ok: status < 400, status, json: async () => corps });

test("succès : verdict et score", async () => {
  const f = async () => reponse(200, { label: "POSITIVE", score: 0.78 });
  const r = await client.analyser(f, "http://x", "k", "bien");
  assert.deepEqual(r, { ok: true, label: "POSITIVE", score: 0.78 });
});

test("la clé est envoyée dans l'en-tête X-API-Key", async () => {
  let vu;
  const f = async (url, opts) => { vu = { url, opts }; return reponse(200, { label: "NEGATIVE", score: 0.9 }); };
  await client.analyser(f, "http://x/", "ma-cle", "mauvais");
  assert.equal(vu.url, "http://x/v1/predict");
  assert.equal(vu.opts.headers["X-API-Key"], "ma-cle");
});

test("401 : message sur la clé", async () => {
  const f = async () => reponse(401, { erreur: { code: "NON_AUTHENTIFIE" } });
  const r = await client.analyser(f, "http://x", "", "bien");
  assert.equal(r.ok, false);
  assert.match(r.message, /Clé/);
});

test("API arrêtée : message injoignable", async () => {
  const f = async () => { throw new TypeError("fetch failed"); };
  const r = await client.analyser(f, "http://x", "k", "bien");
  assert.equal(r.message, client.INJOIGNABLE);
});