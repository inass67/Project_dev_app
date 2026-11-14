// Tests du client web : node --test web/client.test.mjs (aucun serveur, aucun navigateur).
import { test } from "node:test";
import assert from "node:assert/strict";
import { classer, texteResultat, urlDe, MESSAGES } from "./client.js";

const repondre = (statut, corps) => async () => ({
  ok: statut >= 200 && statut < 300,
  status: statut,
  json: async () => corps,
});

test("verdict positif", async () => {
  const r = await classer("http://api", "cle", "super", repondre(200, { label: "POSITIVE", score: 0.9 }));
  assert.equal(r.ok, true);
  assert.equal(r.verdict, "Avis positif");
});

test("verdict négatif", async () => {
  const r = await classer("http://api", "cle", "nul", repondre(200, { label: "NEGATIVE", score: 0.8 }));
  assert.equal(r.verdict, "Avis négatif");
});

test("abstention", async () => {
  const r = await classer("http://api", "cle", "bof", repondre(200, { label: "INDETERMINE", score: 0.55 }));
  assert.match(r.verdict, /humain/);
});

test("clé refusée : 401", async () => {
  const r = await classer("http://api", "x", "avis", repondre(401, { erreur: { code: "NON_AUTHENTIFIE" } }));
  assert.equal(r.ok, false);
  assert.equal(r.message, MESSAGES.NON_AUTHENTIFIE);
});

test("rôle refusé : 403", async () => {
  const r = await classer("http://api", "x", "avis", repondre(403, { erreur: { code: "ACCES_REFUSE" } }));
  assert.equal(r.code, "ACCES_REFUSE");
});

test("entrée invalide : 422", async () => {
  const r = await classer("http://api", "x", "a", repondre(422, { erreur: { code: "ENTREE_INVALIDE" } }));
  assert.equal(r.message, MESSAGES.ENTREE_INVALIDE);
});

test("modèle indisponible : 503", async () => {
  const r = await classer("http://api", "x", "a", repondre(503, { erreur: { code: "MODELE_INDISPONIBLE" } }));
  assert.equal(r.message, MESSAGES.MODELE_INDISPONIBLE);
});

test("API injoignable", async () => {
  const r = await classer("http://api", "x", "a", async () => { throw new TypeError("Failed to fetch"); });
  assert.equal(r.code, "INJOIGNABLE");
});

test("corps non JSON", async () => {
  const fetchFn = async () => ({ ok: false, status: 502, json: async () => { throw new SyntaxError(); } });
  const r = await classer("http://api", "x", "a", fetchFn);
  assert.equal(r.message, "Erreur de l'API (502)");
});

test("texte vide : aucun appel", async () => {
  let appele = false;
  const r = await classer("http://api", "x", "   ", async () => { appele = true; });
  assert.equal(appele, false);
  assert.equal(r.code, "VIDE");
});

test("la requête porte la clé et vise /v1/predict", async () => {
  let vu;
  await classer("http://api/", "ma-cle", "avis", async (url, options) => {
    vu = { url, options };
    return { ok: true, status: 200, json: async () => ({ label: "POSITIVE", score: 0.7 }) };
  });
  assert.equal(vu.url, "http://api/v1/predict");
  assert.equal(vu.options.headers["X-API-Key"], "ma-cle");
  assert.deepEqual(JSON.parse(vu.options.body), { text: "avis" });
});

test("affichage et adresse", () => {
  assert.equal(urlDe(" http://api// "), "http://api");
  assert.equal(texteResultat({ ok: true, verdict: "Avis positif", score: 0.777 }), "Avis positif (confiance 78 %)");
});
