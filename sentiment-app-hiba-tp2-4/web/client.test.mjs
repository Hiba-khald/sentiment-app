import { test } from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { analyser, pourcentage } = require("./client.js");

// Fausse fonction fetch : ni serveur ni navigateur.
const fausse = (statut, corps) => async () => ({
  ok: statut >= 200 && statut < 300,
  status: statut,
  json: async () => {
    if (corps === undefined) throw new Error("pas du JSON");
    return corps;
  },
});
const erreur = (code) => ({ erreur: { code, message: "peu importe", champs: [] } });

test("1. avis positif", async () => {
  const r = await analyser("http://x", "k", "bien", fausse(200, { label: "POSITIVE", score: 0.777, text: "bien" }));
  assert.equal(r.ok, true);
  assert.equal(r.libelle, "Avis positif");
  assert.equal(r.confiance, "Confiance : 78 %");
});

test("2. INDETERMINE renvoie vers un humain", async () => {
  const r = await analyser("http://x", "k", "bof", fausse(200, { label: "INDETERMINE", score: 0.56, text: "bof" }));
  assert.equal(r.ok, true);
  assert.ok(r.libelle.startsWith("Je ne sais pas"));
});

test("3. la clé est envoyée dans X-API-Key", async () => {
  let vu;
  await analyser("http://x", "ma-cle", "t", async (url, opts) => { vu = opts; return fausse(200, { label: "NEGATIVE", score: 0.9, text: "t" })(); });
  assert.equal(vu.headers["X-API-Key"], "ma-cle");
});

test("4. le corps est du JSON avec le champ text", async () => {
  let vu;
  await analyser("http://x", "k", "mon avis", async (url, opts) => { vu = opts; return fausse(200, { label: "NEGATIVE", score: 0.9, text: "t" })(); });
  assert.deepEqual(JSON.parse(vu.body), { text: "mon avis" });
});

test("5. la route appelée est /v1/predict, même avec un / final", async () => {
  let url;
  await analyser("http://x:8000/", "k", "t", async (u) => { url = u; return fausse(200, { label: "NEGATIVE", score: 0.9, text: "t" })(); });
  assert.equal(url, "http://x:8000/v1/predict");
});

test("6. 401 : clé absente ou invalide", async () => {
  const r = await analyser("http://x", "", "t", fausse(401, erreur("NON_AUTHENTIFIE")));
  assert.equal(r.ok, false);
  assert.match(r.message, /Clé d'API/);
});

test("7. 403 : accès refusé", async () => {
  const r = await analyser("http://x", "k", "t", fausse(403, erreur("ACCES_REFUSE")));
  assert.match(r.message, /Accès refusé/);
});

test("8. 422 : texte refusé", async () => {
  const r = await analyser("http://x", "k", " ", fausse(422, erreur("ENTREE_INVALIDE")));
  assert.match(r.message, /refusé/);
});

test("9. 503 : modèle indisponible", async () => {
  const r = await analyser("http://x", "k", "t", fausse(503, erreur("MODELE_INDISPONIBLE")));
  assert.match(r.message, /modèle/);
});

test("10. code inconnu : message générique avec le statut", async () => {
  const r = await analyser("http://x", "k", "t", fausse(418, erreur("THEIERE")));
  assert.match(r.message, /418/);
});

test("11. API arrêtée : fetch échoue", async () => {
  const r = await analyser("http://x", "k", "t", async () => { throw new TypeError("fetch failed"); });
  assert.equal(r.ok, false);
  assert.match(r.message, /injoignable/);
});

test("12. réponse d'erreur qui n'est pas du JSON", async () => {
  const r = await analyser("http://x", "k", "t", fausse(500, undefined));
  assert.equal(r.ok, false);
  assert.match(r.message, /500/);
  assert.equal(pourcentage(0.5), "50 %");
});
