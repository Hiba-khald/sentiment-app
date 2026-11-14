"""Interface Streamlit : un avis, ou un fichier d'avis, classés par l'API /v1."""
import pandas as pd
import streamlit as st

try:  # pytest importe ui.client ; streamlit run ui/app.py ajoute ui/ au chemin
    from ui import client
except ModuleNotFoundError:  # pragma: no cover - lancement direct par Streamlit
    import client  # type: ignore[no-redef]

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
        if not reponse.ok:
            if reponse.message == client.REFUS:
                st.warning(reponse.message)
            else:
                st.error(reponse.message)

with onglet_lot:
    fichier = st.file_uploader("Fichier CSV d'avis", type=["csv"])
    if fichier is not None:
        try:
            donnees = pd.read_csv(fichier)
        except Exception as exc:
            st.error(f"CSV illisible : {exc}")
            donnees = pd.DataFrame()
        if not donnees.empty and "text" not in donnees.columns:
            st.error("Le fichier doit contenir une colonne « text ».")
        elif donnees.empty:
            st.info("Le fichier ne contient aucun avis.")
        else:
            textes = donnees["text"].fillna("").astype(str).tolist()
            with st.spinner("Analyse des avis en cours..."):
                reponses = client.predire_lot(session, textes)
            resultats = pd.DataFrame({
                "avis": textes,
                "verdict": [
                    client.VERDICTS.get(r.label, "REFUS OU ERREUR") if r.ok else "REFUS OU ERREUR"
                    for r in reponses
                ],
                "confiance": [r.score for r in reponses],
            })
            st.dataframe(resultats, use_container_width=True)
            st.write(client.resumer(reponses))

            st.subheader("Répartition des verdicts")
            st.bar_chart(resultats["verdict"].value_counts())
            st.subheader("Distribution de la confiance")
            tranches = pd.cut(
                pd.to_numeric(resultats["confiance"], errors="coerce"),
                bins=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                labels=["0,5 à 0,6", "0,6 à 0,7", "0,7 à 0,8", "0,8 à 0,9", "0,9 à 1"],
            )
            st.bar_chart(tranches.value_counts().sort_index())
            st.caption("Sous 0,6 : avis renvoyés à un humain.")

            csv = resultats.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Télécharger les résultats",
                csv,
                "resultats_sentiment.csv",
                "text/csv",
            )
