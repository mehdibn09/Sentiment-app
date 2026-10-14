"""Interface de démonstration du classifieur de sentiment (Design SaaS / Dashboard Pro).

Usage : streamlit run ui/app.py
Prérequis : models/sentiment.joblib, produit par python src/train.py (TP2).
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from helpers import charger_predicteur, classer, predire_lot, resumer

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Sentiment Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS INJECTÉ POUR CHANGER INTÉGRALEMENT LE DESIGN ---
st.markdown("""
<style>
    /* Importation de la police Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Style global et fond */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }

    /* Personnalisation de la barre latérale */
    section[data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }

    /* Cartes personnalisées */
    .custom-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
    }

    /* Titres et sous-titres */
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-bottom: 28px;
    }

    /* Stylisation des boutons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    
    div[data-testid="stFormSubmitButton"] > button, .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
    }
    
    div[data-testid="stFormSubmitButton"] > button:hover, .stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(99, 102, 241, 0.4);
    }

    /* Zone de texte */
    .stTextArea textarea {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }

    /* Onglets modernes */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #334155;
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 500;
        border: none !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #334155 !important;
        color: #ffffff !important;
        font-weight: 600;
    }

    /* Badges de résultats */
    .badge-positive {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 16px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .badge-negative {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #f87171;
        padding: 16px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .badge-warning {
        background: rgba(245, 158, 11, 0.15);
        border: 1px solid #f59e0b;
        color: #fbbf24;
        padding: 16px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

RACINE = Path(__file__).resolve().parents[1]

@st.cache_resource
def predicteur():
    return charger_predicteur()

try:
    predire = predicteur()
except FileNotFoundError as erreur:
    st.error(str(erreur))
    st.info("Dans un terminal, à la racine du dépôt : `python src/train.py --allocine`")
    st.stop()

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚡ SentimentAI")
    st.caption("Plateforme d'analyse prédictive")
    st.markdown("---")
    
    st.subheader("⚙️ Modèle")
    st.success("Modèle TP2 chargé", icon="✅")
    
    st.markdown("---")
    st.markdown("**Statistiques rapide**")
    st.metric("Seuil d'incertitude", "60%")
    st.metric("Moteur", "Scikit-Learn")

# --- ENTÊTE PRINCIPAL ---
st.markdown('<div class="hero-title">Analyse de sentiment des avis clients</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Moteur de classification temps réel · Interface de démonstration académique</div>', unsafe_allow_html=True)

onglet_avis, onglet_lot, onglet_aide = st.tabs(["🔍 Analyse d'un avis", "📁 Traitement par lot (CSV)", "📖 Documentation"])

with onglet_avis:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    texte = st.text_area("Entrez le texte de l'avis client", "Livraison rapide, produit conforme.", height=120)
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        analyser = st.button("Lancer l'analyse 🚀", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if analyser:
        if not texte.strip():
            st.warning("Veuillez saisir un texte avant de lancer l'analyse.")
        else:
            r = classer(texte, predire)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("Résultat du diagnostic")
            
            colonne_verdict, colonne_score = st.columns([2, 1])
            with colonne_verdict:
                if r["incertain"]:
                    st.markdown(f'<div class="badge-warning">⚠️ À vérifier par un agent (Tendance : « {r["label"]} »)</div>', unsafe_allow_html=True)
                elif r["label"] == "negative":
                    st.markdown('<div class="badge-negative">🚨 Avis Négatif — Priorité Haute</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="badge-positive">✅ Avis Positif</div>', unsafe_allow_html=True)
            
            with colonne_score:
                st.metric("Score de Confiance", f"{r['score']:.0%}")
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.progress(float(r["score"]))
            st.markdown('</div>', unsafe_allow_html=True)

with onglet_lot:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("Importez un fichier CSV contenant une colonne nommée `review`.")
    fichier = st.file_uploader("Téléverser le fichier CSV", type="csv")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if fichier is not None:
        try:
            df = predire_lot(pd.read_csv(fichier), predire)
        except (KeyError, ValueError) as erreur:
            st.error(str(erreur))
        else:
            r = resumer(df)
            
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns(3)
            c1.metric("Total des avis", r["total"])
            c2.metric("Avis Négatifs", f"{r['negatifs']} ({r['part_negatifs']} %)")
            c3.metric("Cas Incertains", r["a_verifier"])
            st.markdown('</div>', unsafe_allow_html=True)
            
            col_graph, col_table = st.columns([1, 1])
            with col_graph:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.subheader("Répartition")
                st.bar_chart(df["prediction"].value_counts())
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_table:
                st.markdown('<div class="custom-card">', unsafe_allow_html=True)
                st.subheader("Résultats détaillés")
                st.dataframe(
                    df.sort_values(["prediction", "confiance"], ascending=[True, False]),
                    use_container_width=True,
                )
                st.download_button(
                    "📥 Exporter les résultats (CSV)",
                    df.to_csv(index=False).encode("utf-8"),
                    "resultats_analyse.csv",
                    "text/csv",
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)

with onglet_aide:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown(
        """
        ### 🛠️ Fonctionnement du système
        
        * **Moteur unifié :** L'interface exploite le modèle entraîné lors du TP2 via la méthode `predict()`. Aucune logique métier n'est dupliquée.
        * **Gestion de l'incertitude :** Si le score de confiance passe en dessous de **60 %**, la prédiction bascule en statut *Incertain* pour révision humaine.
        * **Usage :** Outil de démonstration et d'audit métier avant mise en production de l'API REST.
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)