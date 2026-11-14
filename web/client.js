// Client web de l'API /v1 : la logique (analyser) est séparée de l'affichage pour être testable.
(function (racine) {
  const MESSAGES = {
    ENTREE_INVALIDE: "Avis refusé : saisissez un texte non vide (2000 caractères maximum).",
    NON_AUTHENTIFIE: "Clé d'API absente ou invalide.",
    ACCES_REFUSE: "Cette clé n'a pas le droit d'utiliser cette route.",
    MODELE_INDISPONIBLE: "Le modèle n'est pas chargé côté serveur.",
  };
  const INJOIGNABLE = "API injoignable : vérifiez qu'elle est lancée, son adresse et l'origine autorisée (CORS).";
  const VERDICTS = {
    POSITIVE: "Avis positif",
    NEGATIVE: "Avis négatif",
    INDETERMINE: "Je ne sais pas : à faire vérifier par un humain",
  };

  // fetchFn est injectée : le navigateur passe fetch, les tests passent une fausse fonction
  async function analyser(fetchFn, apiUrl, cle, texte) {
    let r;
    try {
      r = await fetchFn(apiUrl.replace(/\/+$/, "") + "/v1/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-API-Key": cle },
        body: JSON.stringify({ text: texte }),
      });
    } catch (e) {
      return { ok: false, message: INJOIGNABLE };
    }
    if (r.ok) {
      const corps = await r.json();
      return { ok: true, label: corps.label, score: corps.score };
    }
    let code = "";
    try { code = (await r.json()).erreur.code; } catch (e) { /* corps non JSON */ }
    // on teste le code stable, jamais le message, qui peut changer
    return { ok: false, message: MESSAGES[code] || "Erreur de l'API (" + r.status + ")." };
  }

  if (typeof document !== "undefined") {
    const $ = (id) => document.getElementById(id);
    $("bouton").addEventListener("click", async () => {
      const zone = $("resultat");
      $("bouton").disabled = true;
      const res = await analyser(fetch.bind(window), $("url").value, $("cle").value, $("texte").value);
      $("bouton").disabled = false;
      zone.style.display = "block";
      if (!res.ok) {
        zone.className = "erreur";
        $("titre-resultat").textContent = res.message;
        $("detail").textContent = "";
        $("jauge").style.width = "0";
        return;
      }
      zone.className = res.label === "POSITIVE" ? "positif" : res.label === "NEGATIVE" ? "negatif" : "doute";
      $("titre-resultat").textContent = VERDICTS[res.label];
      $("detail").textContent = "Confiance : " + Math.round(res.score * 100) + " %";
      $("jauge").style.width = Math.round(res.score * 100) + "%";
    });
  }

  if (typeof module !== "undefined") module.exports = { analyser, MESSAGES, INJOIGNABLE };
})(this);