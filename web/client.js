// Client de l'API /v1 : aucune dépendance, utilisable dans le navigateur et testé avec Node.

export const VERDICTS = {
  POSITIVE: "Avis positif",
  NEGATIVE: "Avis négatif",
  INDETERMINE: "Je ne sais pas : un humain doit vérifier",
};

export const MESSAGES = {
  INJOIGNABLE: "API injoignable : vérifiez l'adresse et lancez uvicorn api.main:app",
  NON_AUTHENTIFIE: "Clé d'API absente ou invalide",
  ACCES_REFUSE: "Cette clé n'a pas le droit d'utiliser ce service",
  ENTREE_INVALIDE: "Avis refusé : saisissez un texte non vide (2000 caractères au plus)",
  MODELE_INDISPONIBLE: "Le modèle n'est pas chargé côté API",
  VIDE: "Saisissez un avis avant d'analyser",
};

/** Normalise l'adresse de l'API : sans barre oblique finale. */
export function urlDe(base) {
  return String(base || "").trim().replace(/\/+$/, "");
}

/**
 * Envoie un avis à POST /v1/predict.
 * Renvoie toujours un objet { ok, label?, score?, verdict?, code?, message? } : jamais d'exception.
 * fetchFn est injectable : les tests passent une fausse fonction fetch.
 */
export async function classer(base, cle, texte, fetchFn = globalThis.fetch) {
  if (!texte || !String(texte).trim()) return { ok: false, code: "VIDE", message: MESSAGES.VIDE };
  let reponse;
  try {
    reponse = await fetchFn(`${urlDe(base)}/v1/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle || "" },
      body: JSON.stringify({ text: texte }),
    });
  } catch {
    // échec réseau ou refus CORS : le navigateur ne dit pas lequel
    return { ok: false, code: "INJOIGNABLE", message: MESSAGES.INJOIGNABLE };
  }
  let corps = null;
  try {
    corps = await reponse.json();
  } catch {
    corps = null;
  }
  if (reponse.ok && corps && corps.label) {
    return { ok: true, label: corps.label, score: corps.score, verdict: VERDICTS[corps.label] ?? corps.label };
  }
  const code = corps?.erreur?.code ?? "";
  return { ok: false, code, message: MESSAGES[code] ?? `Erreur de l'API (${reponse.status})` };
}

/** Texte à afficher pour un résultat. */
export function texteResultat(r) {
  if (!r.ok) return r.message;
  return `${r.verdict} (confiance ${Math.round(r.score * 100)} %)`;
}
