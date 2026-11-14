"""Interface Streamlit : classer un avis, ou un fichier d'avis, en appelant l'API /v1."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent))
import client  # noqa: E402

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
        try:
            avis = pd.read_csv(fichier)
        except Exception:
            avis = None
        if avis is None or "text" not in avis.columns:
            st.error("Format refusé : le fichier doit être un CSV avec une colonne text.")
        else:
            avis = avis[["text"]].dropna().astype({"text": str}).reset_index(drop=True)
            reponses = client.predire_lot(session, avis["text"].tolist())
            avis["verdict"] = [r.label if r.ok else "REFUS OU ERREUR" for r in reponses]
            avis["confiance"] = pd.to_numeric([r.score for r in reponses], errors="coerce")
            st.dataframe(avis, use_container_width=True)
            st.write(client.resumer(reponses))

            st.subheader("Répartition des verdicts")
            st.bar_chart(avis["verdict"].value_counts())

            st.subheader("Distribution de la confiance")
            # include_lowest : un score de 0,50 tombe dans la première tranche
            tranches = pd.cut(avis["confiance"], bins=[0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                              labels=["0,5 à 0,6", "0,6 à 0,7", "0,7 à 0,8", "0,8 à 0,9", "0,9 à 1"],
                              include_lowest=True)
            st.bar_chart(tranches.value_counts().sort_index())
            st.caption("Sous 0,6 : avis renvoyés à un humain. Ces graphiques résument les sorties "
                       "du modèle ; sans étiquettes de référence, ils ne mesurent pas sa justesse.")

            st.download_button("Télécharger les résultats (CSV)", avis.to_csv(index=False).encode("utf-8"),
                               file_name="resultats.csv", mime="text/csv")
