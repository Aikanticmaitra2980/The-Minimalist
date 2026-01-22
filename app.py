# ... (Keep everything from Part 1 to Part 5 the same) ...

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
        if st.button("← Back to Meditation"):
            st.session_state.page = 'Home'
            st.rerun()

    # Model Inference
    input_data = np.array([[sleep, work, exercise, caffeine, screen]])
    prediction = model.predict(input_data)[0]

    # Header Display
    st.markdown(f'<h1 style="text-align: center;">THE MINIMALIST x {user_name.upper() if user_name else "YOU"}</h1>', unsafe_allow_html=True)
    
    _, col_mid, _ = st.columns([1, 2, 1])
    with col_mid:
        st.markdown(f"""
            <div style="text-align: center; padding: 20px; background: rgba(255,255,255,0.05); border-radius: 20px; border: 1px solid rgba(114, 44, 227, 0.2);">
                <h2 style="color: #888; font-weight: 300; margin-bottom: 0;">CURRENT ALIGNMENT</h2>
                <h1 style="font-size: 100px; margin-top: -10px; color: #722ce3;">{round(prediction, 1)}%</h1>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if not user_name.strip():
            st.warning("⚠️ Enter a name in the sidebar to enable Cloud Sync.")
            st.button("🚀 SYNC TO GOOGLE FIREBASE", disabled=True, use_container_width=True)
        else:
            if st.button("🚀 SYNC TO GOOGLE FIREBASE", use_container_width=True):
                save_log_with_check(user_name, prediction, sleep, work, exercise, caffeine, screen)

    st.divider()

    # --- UPDATED TABS SECTION ---
    tab1, tab2, tab3, tab4 = st.tabs(["🖼️ VISUAL SNAPSHOT", "📊 METRIC CHART", "☁️ CLOUD HISTORY", "👨‍💻 THE DEVELOPER"])
    
    with tab1:
        df_radar = pd.DataFrame(dict(
            r=[sleep, work/1.5, exercise/15, caffeine, screen],
            theta=['Sleep','Work','Exercise','Caffeine','Screen']))
        fig = px.line_polar(df_radar, r='r', theta='theta', line_close=True)
        fig.update_traces(fill='toself', fillcolor='rgba(114, 44, 227, 0.3)', line_color="#722ce3", line_width=4)
        fig.update_layout(polar=dict(bgcolor="rgba(0,0,0,0)", radialaxis=dict(visible=False), angularaxis=dict(color="white")),
                          paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        chart_data = pd.DataFrame({'Metric': ['Sleep', 'Work', 'Screen'], 'Hours': [sleep, work, screen]})
        st.bar_chart(chart_data, x='Metric', y='Hours', color="#722ce3")

    with tab3:
        try:
            logs = st.session_state.db.collection("user_logs").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(5).get()
            if logs:
                st.write("### Recent Syncs from Google Cloud")
                for doc in logs:
                    d = doc.to_dict()
                    st.text(f"☁️ {d.get('name', 'User')} | Score: {round(d.get('efficiency_score', 0), 1)}%")
            else:
                st.info("No cloud data found yet.")
        except:
            st.info("Sync your data to view global history.")

    with tab4:
        st.markdown("### **Project Vision & Technical Stack**")
        st.write("""
            **The Minimalist** was developed to bridge the gap between high-performance habit tracking and mental clarity. 
            By leveraging data science, we can visualize how our biological choices impact our daily output.
        """)
        st.info("""
            **Core Skills Demonstrated:**
            - **Machine Learning:** Random Forest Regression for predictive alignment.
            - **Cloud Architecture:** Secure NoSQL integration via Google Firebase.
            - **UI/UX Design:** Custom CSS injection and responsive Plotly visualizations.
        """)

    # --- ENHANCED ARCHITECT FOOTER ---
    st.divider()
    st.markdown("<h2 style='text-align: center; letter-spacing: 3px;'>THE ARCHITECT</h2>", unsafe_allow_html=True)
    
    col_img, col_info = st.columns([1, 2])
    with col_img:
        st.image("https://scontent.fccu5-1.fna.fbcdn.net/v/t39.30808-6/550939647_122094055065044657_3789721203803613706_n.jpg?_nc_cat=102&ccb=1-7&_nc_sid=a5f93a&_nc_ohc=o9azU6rrPysQ7kNvwEvpwno&_nc_oc=Adk1JvWm7p6VRUicvywIHtsLsCls1VQaG5zHs6r9R7ZsPRv-AxadK3QttrbpPezpd5M&_nc_zt=23&_nc_ht=scontent.fccu5-1.fna&_nc_gid=5lvWZWHvIQSHJy2ezsbrig&oh=00_AfobYDvrcZENkLbtYMzrB6xLv08pCi2lrBroHKlDkCWfhw&oe=69771FF9", use_container_width=True)

    with col_info:
        st.markdown("### **Aikantic Maitra**")
        st.markdown("#### *Full Stack Data Engineering*")
        st.write("""
            Passionate about building minimalist, data-driven applications that prioritize user mental wellbeing. 
            Focused on scalable cloud infrastructure and interpretable AI.
        """)
        st.markdown(f"""
            <a href="https://github.com/Aikanticmaitra2980" target="_blank"><button style="border:1px solid #722ce3; border-radius:5px; background:transparent; color:white; padding:5px 15px; cursor:pointer;">GitHub</button></a>
            <a href="https://www.linkedin.com/in/aikantic-maitra-118b48362/" target="_blank"><button style="border:1px solid #722ce3; border-radius:5px; background:transparent; color:white; padding:5px 15px; cursor:pointer;">LinkedIn</button></a>
        """, unsafe_allow_html=True)
