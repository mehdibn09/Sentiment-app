"""Interface de démonstration du classifieur de sentiment (Design SaaS / Dashboard Pro).

Usage : streamlit run ui/app.py
Prérequis : l'API tourne (uvicorn api.main:app). La page est un client de l'API (TP5) :
elle n'importe jamais predict() ni le fichier .joblib.
"""
import client
import pandas as pd
import streamlit as st

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

def nouvelle_session():
    """Une connexion à l'API par session de navigateur."""
    if "session" not in st.session_state:
        st.session_state["session"] = client.creer_session()
    return st.session_state["session"]


session = nouvelle_session()
etat = client.sante(session)

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.title("⚡ SentimentAI")
    st.caption("Plateforme d'analyse prédictive")
    st.markdown("---")

    st.subheader("⚙️ API")
    st.caption(client.API_URL)
    st.metric("Moteur", "Scikit-Learn")

# --- ENTÊTE PRINCIPAL ---
st.markdown('<div class="hero-title">Analyse de sentiment des avis clients</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Moteur de classification temps réel · Interface de démonstration académique</div>', unsafe_allow_html=True)

if etat.ok:
    st.success(f"API prête : {etat.message}")
else:
    st.error(etat.message)
    st.stop()

BADGES = {
    "POSITIVE": ("badge-positive", "✅"),
    "NEGATIVE": ("badge-negative", "🚨"),
    "INDETERMINE": ("badge-warning", "⚠️"),
}

onglet_avis, onglet_lot, onglet_aide = st.tabs(["🔍 Un avis", "📁 Un fichier d'avis", "📖 Documentation"])

with onglet_avis:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    texte = st.text_area("Entrez le texte de l'avis client", "Livraison rapide, produit conforme.", height=120)

    col_btn, _ = st.columns([1, 4])
    with col_btn:
        analyser = st.button("Analyser", type="primary", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if analyser:
        r = client.predire(session, texte)
        if not r.ok:
            st.warning(r.message)
        else:
            classe, icone = BADGES[r.label]
            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("Résultat du diagnostic")

            colonne_verdict, colonne_score = st.columns([2, 1])
            with colonne_verdict:
                st.markdown(f'<div class="{classe}">{icone} {client.VERDICTS[r.label]}</div>', unsafe_allow_html=True)
            with colonne_score:
                st.metric("Confiance", f"{r.score:.0%}")

            if r.label == "INDETERMINE":
                st.info("La confiance est sous le seuil d'abstention : un humain doit trancher.")
            st.progress(float(r.score))
            st.markdown('</div>', unsafe_allow_html=True)

with onglet_lot:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.write("Importez un fichier CSV contenant une colonne nommée `review`.")
    fichier = st.file_uploader("Téléverser le fichier CSV", type="csv")
    st.markdown('</div>', unsafe_allow_html=True)

    if fichier is not None:
        try:
            avis = pd.read_csv(fichier)
        except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
            st.error("Fichier illisible : un CSV encodé en UTF-8 est attendu.")
            avis = None
        if avis is not None and "review" not in avis.columns:
            st.error("Colonne `review` absente du fichier.")
        elif avis is not None:
            textes = avis["review"].fillna("").astype(str).tolist()
            reponses = client.predire_lot(session, textes)
            tableau = pd.DataFrame({
                "review": textes,
                "verdict": [client.VERDICTS[r.label] if r.ok and r.label else r.message for r in reponses],
                "confiance": [round(r.score, 3) if r.ok and r.score is not None else None for r in reponses],
            })

            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("Résumé")
            st.write(client.resumer(reponses))
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="custom-card">', unsafe_allow_html=True)
            st.subheader("Résultats détaillés")
            st.dataframe(tableau, use_container_width=True)
            st.download_button(
                "📥 Télécharger les résultats",
                tableau.to_csv(index=False).encode("utf-8"),
                "resultats.csv",
                "text/csv",
                use_container_width=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

with onglet_aide:
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    st.markdown(
        """
        ### 🛠️ Fonctionnement du système

        * **Client de l'API :** l'interface envoie `POST /predict` à l'API et traduit chaque réponse en message clair. Elle n'importe jamais le modèle : un modèle réentraîné ne demande aucune modification de la page.
        * **Abstention :** sous le seuil de confiance fixé par l'API, le verdict est `INDETERMINE` : « Je ne sais pas : à faire vérifier par un humain ».
        * **Erreurs :** texte refusé (422), modèle non chargé (503) et API injoignable sont expliqués à l'utilisateur.
        """
    )
    st.markdown('</div>', unsafe_allow_html=True)
