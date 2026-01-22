import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from google.cloud import firestore
from google.oauth2 import service_account

# --- 1. FIREBASE INITIALIZATION ---
if 'db' not in st.session_state:
    try:
        if "firebase_secrets" in st.secrets:
            creds_dict = dict(st.secrets["firebase_secrets"])
            if "\\n" in creds_dict.get("private_key", ""):
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            st.session_state.db = firestore.Client(credentials=creds, project=creds_dict["project_id"])
        else:
            st.session_state.db = firestore.Client.from_service_account_json("the-minimalist-cfcaf-firebase-adminsdk-fbsvc-ba5ae5bc99.json")
    except Exception as e:
        st.session_state.db = None

# --- 2. CLOUD SYNC FUNCTION ---
def save_log(name, score, s, w, e, c, sc):
    try:
        doc_ref = st.session_state.db.collection("user_logs").document()
        doc_ref.set({
            "name": name, "efficiency_score": score,
            "sleep": s, "work": w, "exercise": e, "caffeine": c, "screen": sc,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
        st.toast(f"Secured in Cloud!", icon="☁️")
    except:
        st.error("Sync Failed.")

# --- 3. UI SETUP ---
st.set_page_config(page_title="The Minimalist", page_icon="🧘", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .hero-title { font-size: 4rem !important; font-weight: 800; text-align: center; padding-top: 10vh; }
    </style>
    """, unsafe_allow_html=True)

model = joblib.load('minimalist_model.pkl')

# --- 4. NAVIGATION ---
if st.session_state.page == 'Home':
    st.markdown('<h1 class="hero-title">THE MINIMALIST.</h1>', unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    if col_btn.button("GET STARTED →", use_container_width=True):
        st.session_state.page = 'Dashboard'
        st.rerun()

elif st.session_state.page == 'Dashboard':
    with st.sidebar:
        st.header("👤 IDENTITY")
        user_name = st.text_input("Name")
        st.divider()
        sleep = st.slider("Sleep", 4.0, 10.0, 7.5)
        work = st.slider("Work", 2.0, 12.0, 8.0)
        exercise = st.slider("Exercise", 0, 120, 30)
        caffeine = st.slider("Caffeine", 0, 6, 2)
        screen = st.slider("Screen", 1.0, 8.0, 3.0)
        if st.button("← Home"):
            st.session_state.page = 'Home'
            st.rerun()

    # Prediction
    prediction = model.predict(np.array([[sleep, work, exercise, caffeine, screen]]))[0]

    st.markdown(f"<h1 style='text-align: center;'>ALIGNMENT: {round(prediction, 1)}%</h1>", unsafe_allow_html=True)
    
    if user_name and st.button("🚀 SYNC TO CLOUD", use_container_width=True):
        save_log(user_name, prediction, sleep, work, exercise, caffeine, screen)

    st.divider()

    # --- THE ONLY TAB DEFINITION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ VISUAL", "📊 METRICS", "☁️ HISTORY", "👨‍💻 ARCHITECT"])

    with tab1:
        df_radar = pd.DataFrame(dict(r=[sleep, work/1.5, exercise/15, caffeine, screen], theta=['Sleep','Work','Exercise','Caffeine','Screen']))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(114, 44, 227, 0.3)', line_color="#722ce3")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.bar_chart(pd.DataFrame({'Metric': ['Sleep', 'Work', 'Screen'], 'Hours': [sleep, work, screen]}), x='Metric', y='Hours', color="#722ce3")

    with tab3:
        if st.session_state.db:
            logs = st.session_state.db.collection("user_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).get()
            for doc in logs:
                d = doc.to_dict()
                st.text(f"☁️ {d.get('name')} | {round(d.get('efficiency_score', 0), 1)}%")
        else:
            st.info("No cloud connection.")

    with tab4:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image("https://media.licdn.com/dms/image/v2/D5603AQF1Fvggzuh1zA/profile-displayphoto-crop_800_800/B56ZlZLFqeI8AI-/0/1758137706303?e=1770854400&v=beta&t=Zj0F13CZsoDP6dXfoItPPeyGmQFkI2zdZCzKmdCf7Bw")
        with c2:
            st.header("Aikantic Maitra")
            st.info("Full Stack Data Engineer")
            st.write("Specializing in ML and Cloud Infrastructure.")
            st.markdown("[GitHub](https://github.com/Aikanticmaitra2980) | [LinkedIn](https://www.linkedin.com/in/aikantic-maitra-118b48362/)")
