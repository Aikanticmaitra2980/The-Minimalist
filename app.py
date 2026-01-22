import streamlit as st
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
from google.cloud import firestore
from google.oauth2 import service_account

# --- 1. SMART FIREBASE INITIALIZATION ---
if 'db' not in st.session_state:
    try:
        # Check for Secrets (Streamlit Cloud or Local .streamlit/secrets.toml)
        if "firebase_secrets" in st.secrets:
            creds_dict = dict(st.secrets["firebase_secrets"])
            if "\\n" in creds_dict.get("private_key", ""):
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
            creds = service_account.Credentials.from_service_account_info(creds_dict)
            st.session_state.db = firestore.Client(credentials=creds, project=creds_dict["project_id"])
        # Fallback to Local JSON
        else:
            st.session_state.db = firestore.Client.from_service_account_json("the-minimalist-cfcaf-firebase-adminsdk-fbsvc-ba5ae5bc99.json")
    except Exception as e:
        st.session_state.db = None
        st.error(f"Cloud Connection Warning: {e}")

# --- 2. CLOUD SYNC FUNCTION ---
def save_log_with_check(name, score, s, w, e, c, sc):
    try:
        if st.session_state.db is None:
            st.error("Database not connected.")
            return
        
        # Check if name exists
        query = st.session_state.db.collection("user_logs").where("name", "==", name).limit(1).get()
        if len(query) > 0:
            st.error(f"The name '{name}' is already taken. Try a unique identifier.")
        else:
            doc_ref = st.session_state.db.collection("user_logs").document()
            doc_ref.set({
                "name": name, "efficiency_score": float(score),
                "sleep": s, "work": w, "exercise": e, "caffeine": c, "screen": sc,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            st.toast(f"Success! {name}'s data secured in Cloud.", icon="☁️")
    except Exception as err:
        st.error(f"Cloud Error: {err}")

# --- 3. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="The Minimalist", page_icon="🧘", layout="wide")

if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def start_app():
    st.session_state.page = 'Dashboard'

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div.stButton > button { transition: all 0.3s ease-in-out; border-radius: 12px !important; }
    div.stButton > button:hover { transform: translateY(-3px); box-shadow: 0px 8px 15px rgba(114, 44, 227, 0.4) !important; }
    div[data-baseweb="slider"] [role="slider"] { border: 2px solid #722ce3 !important; box-shadow: 0px 0px 12px rgba(114, 44, 227, 0.6) !important; }
    .hero-container { text-align: center; padding-top: 15vh; color: white; }
    .hero-title { font-size: 5rem !important; font-weight: 800; letter-spacing: -2px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOAD MODEL ---
try:
    model = joblib.load('minimalist_model.pkl')
except:
    st.error("Model file missing.")

# --- 5. PAGE NAVIGATION: HOME ---
if st.session_state.page == 'Home':
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.6)), 
                        url("https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1920&q=80");
            background-size: cover; background-position: center;
        }
        </style>
        <div class="hero-container">
            <h1 class="hero-title">THE MINIMALIST.</h1>
            <p style="font-size: 1.5rem; opacity: 0.8; letter-spacing: 2px;">FIND YOUR CENTER. OPTIMIZE YOUR LIFE.</p>
        </div>
    """, unsafe_allow_html=True)
    _, col_btn, _ = st.columns([1, 1, 1])
    with col_btn:
        st.button("GET STARTED →", use_container_width=True, on_click=start_app)

# --- 6. PAGE NAVIGATION: DASHBOARD ---
elif st.session_state.page == 'Dashboard':
    with st.sidebar:
        st.markdown("### 👤 IDENTITY")
        user_name = st.text_input("Enter Name", placeholder="Your Name...")
        st.divider()
        st.markdown("### 🛠️ CONFIGURATION")
        sleep = st.slider("Sleep (Hours)", 4.0, 10.0, 7.5)
        work = st.slider("Work (Hours)", 2.0, 12.0, 8.0)
        exercise = st.slider("Exercise (Minutes)", 0, 120, 30)
        caffeine = st.slider("Caffeine (Cups)", 0, 6, 2)
        screen = st.slider("Screen (Hours)", 1.0, 8.0, 3.0)
        st.divider()
        if st.button("← Back to Home"):
            st.session_state.page = 'Home'; st.rerun()

    input_data = np.array([[sleep, work, exercise, caffeine, screen]])
    prediction = model.predict(input_data)[0]

    st.markdown(f'<h1 style="text-align: center;">THE MINIMALIST x {user_name.upper() if user_name else "YOU"}</h1>', unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(114, 44, 227, 0.2);">
                <h2 style="color: #888; font-weight: 300; margin-bottom: 0;">CURRENT ALIGNMENT</h2>
                <h1 style="font-size: 100px; margin-top: -10px; color: #722ce3;">{round(prediction, 1)}%</h1>
            </div>
        """, unsafe_allow_html=True)
        
        if not user_name.strip():
            st.warning("⚠️ Enter name to enable Cloud Sync.")
        else:
            if st.button("🚀 SYNC TO GOOGLE FIREBASE", use_container_width=True):
                save_log_with_check(user_name, prediction, sleep, work, exercise, caffeine, screen)

    st.divider()

    # --- THE ONE AND ONLY TABS SECTION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ VISUAL SNAPSHOT", "📊 METRIC CHART", "☁️ CLOUD HISTORY", "👨‍💻 THE ARCHITECT"])
    
    with tab1:
        df_radar = pd.DataFrame(dict(r=[sleep, work/1.5, exercise/15, caffeine, screen],
                                     theta=['Sleep','Work','Exercise','Caffeine','Screen']))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(114, 44, 227, 0.3)', line_color="#722ce3")
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False), angularaxis=dict(color="white")),
                          paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        chart_data = pd.DataFrame({'Metric': ['Sleep', 'Work', 'Screen'], 'Hours': [sleep, work, screen]})
        st.bar_chart(chart_data, x='Metric', y='Hours', color="#722ce3")

    with tab3:
        try:
            if st.session_state.db:
                logs = st.session_state.db.collection("user_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).get()
                for doc in logs:
                    d = doc.to_dict()
                    st.text(f"☁️ {d.get('name', 'User')} | Alignment: {round(d.get('efficiency_score', 0), 1)}%")
            else:
                st.info("Database not connected.")
        except:
            st.info("Sync data to view history.")

    with tab4:
        st.markdown("### Meet the Developer")
        col_img, col_info = st.columns([1, 2])
        with col_img:
            st.image("https://media.licdn.com/dms/image/v2/D5603AQF1Fvggzuh1zA/profile-displayphoto-crop_800_800/B56ZlZLFqeI8AI-/0/1758137706303?e=1770854400&v=beta&t=Zj0F13CZsoDP6dXfoItPPeyGmQFkI2zdZCzKmdCf7Bw", use_container_width=True)
        with col_info:
            st.markdown("### **Aikantic Maitra**")
            st.info("**Full Stack Data Engineer**")
            st.write("Specializing in bridging Machine Learning and Cloud Infrastructure.")
            st.markdown("#### 🚀 Project Tech Stack")
            st.markdown("- **AI:** Scikit-Learn Random Forest\n- **Cloud:** Google Firebase Firestore\n- **UI:** Streamlit & Plotly")
            st.divider()
            st.markdown("[GitHub](https://github.com/Aikanticmaitra2980) | [LinkedIn](https://www.linkedin.com/in/aikantic-maitra-118b48362/)")
