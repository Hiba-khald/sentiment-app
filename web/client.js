// Client web de l'API /v1. Utilisable dans le navigateur (balise <script>) et testable avec Node.
const LIBELLES = {
  POSITIVE: "Avis positif",
  NEGATIVE: "Avis négatif",
  INDETERMINE: "Je ne sais pas : à faire vérifier par un humain",
};

// On teste le code stable de l'erreur, jamais son message.
const MESSAGES = {
  NON_AUTHENTIFIE: "Clé d'API absente ou invalide.",
  ACCES_REFUSE: "Accès refusé pour cette clé.",
  ENTREE_INVALIDE: "Avis refusé : texte vide ou trop long.",
  MODELE_INDISPONIBLE: "Le modèle n'est pas disponible.",
  ERREUR_INTERNE: "Erreur interne de l'API.",
};

function pourcentage(score) {
  return Math.round(score * 100) + " %";
}

async function analyser(apiUrl, cle, texte, fetchFn) {
  const appel = fetchFn || globalThis.fetch;
  const url = apiUrl.replace(/\/+$/, "") + "/v1/predict";
  let reponse;
  try {
    reponse = await appel(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-API-Key": cle },
      body: JSON.stringify({ text: texte }),
    });
  } catch (e) {
    return { ok: false, message: "API injoignable : lancez l'API et vérifiez l'adresse." };
  }
  let corps = null;
  try {
    corps = await reponse.json();
  } catch (e) {
    corps = null;
  }
  if (reponse.ok && corps && corps.label) {
    return {
      ok: true,
      label: corps.label,
      libelle: LIBELLES[corps.label] || corps.label,
      score: corps.score,
      confiance: "Confiance : " + pourcentage(corps.score),
    };
  }
  const code = corps && corps.erreur ? corps.erreur.code : "";
  return { ok: false, message: MESSAGES[code] || "Erreur inattendue (" + reponse.status + ")." };
}

if (typeof module !== "undefined") {
  module.exports = { analyser, pourcentage, LIBELLES, MESSAGES };
}
