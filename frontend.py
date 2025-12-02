import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import time
import os

# --- CONFIG ---
API_URL = "http://127.0.0.1:8000"

# Fix for proxy issues on some local networks
os.environ["NO_PROXY"] = "127.0.0.1,localhost"

st.set_page_config(page_title="Deep Analytics Hub", layout="wide")

st.title("🎓 Detailed Student Analytics")

# --- SIDEBAR: UPLOAD ---
with st.sidebar:
    st.header("Upload PDF")
    uploaded_file = st.file_uploader("Upload Result Gazette", type="pdf")
    
    if uploaded_file and st.button("Deep Extract & Analyze"):
        with st.spinner("AI is extracting Subject-wise data... (Do not close this tab)"):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                
                # FIX: Increased timeout to 20 minutes (1200s) for large PDFs
                res = requests.post(f"{API_URL}/upload", files=files, timeout=1200)
                
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Success! Processed {data.get('records_processed')} students.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"Server Error: {res.text}")
            except requests.exceptions.ReadTimeout:
                st.error("The request timed out, but the backend might still be working. Check your terminal.")
            except Exception as e:
                st.error(f"Connection Failed: {e}")

# --- TABS ---
tab1, tab2 = st.tabs(["📊 Dashboard", "💬 Deep Query Chat"])

# --- DASHBOARD ---
with tab1:
    try:
        res = requests.get(f"{API_URL}/stats", timeout=3)
        if res.status_code == 200:
            data = res.json()
            
            # Metrics
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Students", data['total'])
            c2.metric("Class Average CGPA", data['avg_cgpa'])
            
            # Pass Rate
            passed = sum([x['count'] for x in data['pass_fail'] if "PASS" in str(x['_id']).upper()])
            total = data['total'] if data['total'] > 0 else 1
            c3.metric("Pass Rate", f"{round(passed/total*100, 1)}%")
            
            st.divider()
            
            # Charts
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("Pass/Fail Status")
                if data['pass_fail']:
                    df = pd.DataFrame(data['pass_fail'])
                    fig = px.pie(df, names='_id', values='count', hole=0.4)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No Pass/Fail data yet.")
            
            with col_b:
                st.subheader("CGPA Distribution")
                if data['cgpa_dist']:
                    df = pd.DataFrame(data['cgpa_dist'], columns=['CGPA'])
                    fig = px.histogram(df, x="CGPA", nbins=20)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No CGPA data yet.")
        else:
            st.warning("Backend not reachable. Ensure 'backend.py' is running.")
    except:
        st.info("Upload a PDF to generate statistics.")

# --- CHATBOT ---
with tab2:
    st.header("Ask anything about Marks, Subjects, or Toppers")
    st.caption("Examples: 'Who got the highest marks in Python?', 'How much did Rahul score in Physics?', 'List all students who failed'.")
    
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about the results..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.chat_message("assistant"):
            with st.spinner("Analyzing database..."):
                try:
                    # Timeout 300s because deep aggregation queries can be slow
                    api_res = requests.post(f"{API_URL}/chat", json={"query": prompt}, timeout=300)
                    if api_res.status_code == 200:
                        ans = api_res.json()['answer']
                        st.markdown(ans)
                        st.session_state.messages.append({"role": "assistant", "content": ans})
                    else:
                        st.error("Error generating answer.")
                except Exception as e:
                    st.error(f"Error: {e}")