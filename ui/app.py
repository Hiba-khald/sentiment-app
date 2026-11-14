"""Interface Streamlit : un avis, ou un fichier CSV d'avis."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # pour importer "ui"

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from ui import client  # noqa: E402

st.set_page_config(page_title="Analyse de sentiment")
st.title("Analyse de sentiment des avis")

session = client.creer_session()
etat = client.sante(session)
if etat.ok:
    st.caption(f"API prête : {etat.message}")
else:
    st.error(etat.message)

onglet_avis, onglet_lot = st.tabs(["Un avis", "Un fichier d'avis"])

with onglet_avis:
    texte = st.text_area("Avis client")
    if st.button("Analyser"):
        reponse = client.predire(session, texte)
        if reponse.ok and reponse.label is not None and reponse.score is not None:
            st.metric(client.VERDICTS[reponse.label], f"{reponse.score:.0%}")
            if reponse.label == "INDETERMINE":
                st.info("La confiance est sous le seuil d'abstention : un humain doit trancher.")
        elif reponse.message == client.REFUS:
            st.warning(reponse.message)
        else:
            st.error(reponse.message)

with onglet_lot:
    fichier = st.file_uploader("Fichier CSV avec une colonne text", type="csv")
    if fichier is not None:
        donnees = pd.read_csv(fichier)
        if "text" not in donnees.columns:
            st.error("Le fichier doit contenir une colonne « text ».")
        else:
            textes = donnees["text"].fillna("").astype(str).tolist()
            with st.spinner("Analyse en cours..."):
                reponses = client.predire_lot(session, textes)
            avis = pd.DataFrame({
                "text": textes,
                "verdict": [client.VERDICTS[r.label] if r.ok and r.label else r.message
                            for r in reponses],
                "confiance": [r.score for r in reponses],
            })
            st.dataframe(avis)
            st.write(client.resumer(reponses))

            st.subheader("Répartition des verdicts")
            st.bar_chart(avis["verdict"].value_counts())

            st.subheader("Distribution de la confiance")
            tranches = pd.cut(
                avis["confiance"], bins=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0], include_lowest=True,
                labels=["0,5 à 0,6", "0,6 à 0,7", "0,7 à 0,8", "0,8 à 0,9", "0,9 à 1"])
            st.bar_chart(tranches.value_counts().sort_index())
            st.caption("Les tranches sont fermées à droite : une confiance de exactement 0,6 "
                       "tombe dans la première tranche, alors que l'abstention est stricte (< 0,6).")

            st.download_button("Télécharger les résultats (CSV)",
                               avis.to_csv(index=False).encode("utf-8"),
                               file_name="resultats.csv", mime="text/csv")