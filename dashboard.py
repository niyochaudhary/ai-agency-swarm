import sys
import os
import streamlit as st
import pandas as pd
import time
from datetime import datetime
import re
import importlib

# Path fix
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import config
importlib.reload(config)

import core.swarm_master
import core.builder_master
importlib.reload(core.swarm_master)
importlib.reload(core.builder_master)
from core.swarm_master import SwarmMaster
from core.builder_master import BuilderMaster
import agents.hunter_agent
import agents.builder_agent
import agents.research_agent
import agents.scraper_agent
importlib.reload(agents.hunter_agent)
importlib.reload(agents.builder_agent)
importlib.reload(agents.research_agent)
importlib.reload(agents.scraper_agent)

import memory.database
importlib.reload(memory.database)
from memory.database import SwarmMemory

# Page Configuration
st.set_page_config(
    page_title="AI Swarm Agency | Premium Admin",
    page_icon="👑",
    layout="wide"
)

# --- PREMIUM CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    
    .main { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: white; }
    
    .stApp { background-color: transparent; }
    
    /* Premium Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        transition: transform 0.3s ease;
    }
    .metric-card:hover { transform: translateY(-5px); border-color: #6366f1; }
    .metric-card h1 { font-size: 3rem !important; color: #818cf8 !important; margin: 10px 0; }
    .metric-card h3 { font-size: 1rem !important; color: #94a3b8 !important; text-transform: uppercase; letter-spacing: 2px; }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s;
        height: 3.5em;
    }
    .stButton>button:hover { opacity: 0.9; box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
    
    /* Inputs */
    .stTextInput>div>div>input {
        background: rgba(0, 0, 0, 0.2) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Email Box */
    .email-box {
        background: #1e293b;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #334155;
        color: #f1f5f9;
        font-size: 0.95rem;
        line-height: 1.6;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid rgba(255, 255, 255, 0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- AUTHENTICATION ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

def login():
    st.markdown("<h1 style='text-align: center; color: white;'>👑 AI Agency Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("Login"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Launch Swarm"):
                if user == config.DASHBOARD_USERNAME and pw == config.DASHBOARD_PASSWORD:
                    st.session_state['authenticated'] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials, Admiral.")

if not st.session_state['authenticated']:
    login()
    st.stop()

# --- MAIN APP ---
master = SwarmMaster()
db = SwarmMemory()
builder_swarm = BuilderMaster()

# Sidebar
st.sidebar.markdown("<h2 style='text-align: center;'>🤖 Swarm Control</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation", ["🚀 Overview", "🔍 Start New Hunt", "📂 Memory Vault", "🏗️ Project Delivery", "📧 Sent Logs", "⚙️ Settings"])

if st.sidebar.button("🔒 Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

# --- Overview ---
if menu == "🚀 Overview":
    st.title("🚀 Strategic Overview")
    leads = db.get_all_leads()
    total = len(leads['ids']) if leads['ids'] else 0
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card"><h3>Total Leads</h3><h1>{total}</h1></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><h3>Active Swarms</h3><h1>4</h1></div>', unsafe_allow_html=True)
    with col3: st.markdown(f'<div class="metric-card"><h3>Revenue Goal</h3><h1>1 Cr</h1></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📈 Recent Activity")
    hunts = db.get_hunt_history()
    if hunts and hunts['ids']:
        h_data = [{"Time": m.get('timestamp'), "Niche": m.get('niche'), "Location": m.get('location')} for m in hunts['metadatas']]
        st.table(pd.DataFrame(h_data).tail(5))
    else: st.info("No hunt history yet.")

# --- Start New Hunt ---
elif menu == "🔍 Start New Hunt":
    st.title("🔍 Deploy Hunt Swarm")
    col1, col2 = st.columns(2)
    with col1: n = st.text_input("Target Niche", placeholder="e.g. Real Estate")
    with col2: l = st.text_input("Target Location", placeholder="e.g. New York")
    
    count = st.slider("Leads to find", 1, 20, 5)
    
    if st.button("🔥 Launch Autonomous Hunt"):
        if n and l:
            with st.spinner("🤖 Swarm is searching the web..."):
                master.orchestrate_hunt(n, l, count=count)
                st.success("Hunt Complete! Leads secured in Memory Vault.")
                time.sleep(2)
                st.rerun()

# --- Memory Vault ---
elif menu == "📂 Memory Vault":
    st.title("📂 Memory Vault")
    leads = db.get_all_leads()
    if leads['ids']:
        df_data = []
        for i in range(len(leads['ids'])):
            m = leads['metadatas'][i]
            df_data.append({"Name": m.get('name', 'N/A'), "Website": m.get('website', 'N/A'), "Niche": m.get('niche', 'N/A')})
        
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        
        st.markdown("---")
        sel = st.selectbox("Select Lead to Action", [l.get('name', 'Unknown') for l in leads['metadatas']])
        
        for i in range(len(leads['ids'])):
            if leads['metadatas'][i].get('name') == sel:
                lead_data = leads['metadatas'][i]
                pitch_content = leads['documents'][i]
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("#### 📝 AI Generated Pitch")
                    st.text_area("Content", pitch_content, height=400, label_visibility="collapsed")
                
                with col2:
                    st.markdown("#### 📧 Outreach")
                    recipient_email = st.text_input("CEO Email", value=lead_data.get('email', ''))
                    
                    if st.button("🚀 Send Outreach Now"):
                        if not recipient_email:
                            st.error("Email required!")
                        else:
                            with st.spinner("Transmitting..."):
                                master.sender.sender_email = st.session_state.get('sender_email', getattr(config, 'SENDER_EMAIL', ""))
                                master.sender.app_password = st.session_state.get('app_password', getattr(config, 'EMAIL_PASSWORD', ""))
                                master.sender.dry_run = not st.session_state.get('live_mode', False)
                                
                                if master.sender.send_email(sel, recipient_email, pitch_content):
                                    st.success("Message Transmitted!")
                                    st.balloons()
                                else: st.error("Transmission failed.")
                
                if st.button("🗑️ Purge Lead Data"):
                    db.delete_lead(leads['ids'][i])
                    st.rerun()

# --- Project Delivery ---
elif menu == "🏗️ Project Delivery":
    st.title("🏗️ Project Factory")
    leads = db.get_all_leads()
    if leads['ids']:
        for i in range(len(leads['ids'])):
            name = leads['metadatas'][i].get('name', 'Unknown')
            with st.expander(f"💎 {name}"):
                if st.button(f"🛠️ Build Full Solution for {name}", key=f"b_{i}"):
                    with st.spinner("AI Factory is coding..."):
                        path = builder_swarm.launch_project(name, leads['documents'][i])
                        st.session_state[f"path_{i}"] = path
                        st.success("Project Engineered!")
                
                if f"path_{i}" in st.session_state:
                    st.info(f"📂 Build Path: {st.session_state[f'path_{i}']}")
                    delivery_email = st.text_input("Delivery Email", value=leads['metadatas'][i].get('email', ''), key=f"e_{i}")
                    
                    if st.button(f"📬 Deliver to CEO", key=f"d_{i}"):
                        with st.spinner("Delivering..."):
                            roadmap_file = os.path.join(st.session_state[f"path_{i}"], "roadmap.md")
                            roadmap_content = open(roadmap_file, "r").read() if os.path.exists(roadmap_file) else "Roadmap inside."
                            
                            delivery_pitch = f"Hello {name},\n\nYour AI Solution is ready.\n\nROADMAP:\n{roadmap_content}\n\nCodebase is prepared."
                            
                            master.sender.sender_email = st.session_state.get('sender_email', getattr(config, 'SENDER_EMAIL', ""))
                            master.sender.app_password = st.session_state.get('app_password', getattr(config, 'EMAIL_PASSWORD', ""))
                            master.sender.dry_run = not st.session_state.get('live_mode', False)
                            
                            if master.sender.send_email(name, delivery_email, delivery_pitch):
                                st.success("Solution Delivered!")

# --- Sent Logs ---
elif menu == "📧 Sent Logs":
    st.title("📧 Transmission Logs")
    try:
        logs = db.get_outbox_logs()
        if logs and logs['ids']:
            data = [{"Time": m.get('timestamp'), "Recipient": m.get('recipient_name'), "Status": m.get('status')} for m in logs['metadatas']]
            st.dataframe(pd.DataFrame(data), use_container_width=True)
            sel_log = st.selectbox("Read Transmission", [f"{l.get('recipient_name')} ({l.get('timestamp')})" for l in logs['metadatas']])
            for i in range(len(logs['ids'])):
                if f"{logs['metadatas'][i].get('recipient_name')} ({logs['metadatas'][i].get('timestamp')})" == sel_log:
                    st.markdown(f'<div class="email-box">{logs["documents"][i]}</div>', unsafe_allow_html=True)
        else: st.info("No transmissions logged.")
    except Exception as e: st.error(f"Error: {e}")

# --- Settings ---
elif menu == "⚙️ Settings":
    st.title("⚙️ System Configuration")
    
    with st.expander("🔐 Security Settings"):
        new_user = st.text_input("Admin Username", value=config.DASHBOARD_USERNAME)
        new_pw = st.text_input("New Password", type="password")
        if st.button("Update Credentials"):
            # Update config.py
            with open("config.py", "r") as f: lines = f.readlines()
            with open("config.py", "w") as f:
                for line in lines:
                    if "DASHBOARD_USERNAME =" in line: f.write(f'DASHBOARD_USERNAME = "{new_user}"\n')
                    elif "DASHBOARD_PASSWORD =" in line: f.write(f'DASHBOARD_PASSWORD = "{new_pw if new_pw else config.DASHBOARD_PASSWORD}"\n')
                    else: f.write(line)
            st.success("Security updated! Please restart server for full effect.")
            
    with st.form("Email Gateway"):
        st.markdown("### 📧 Email SMTP Gateway")
        st.session_state['sender_email'] = st.text_input("Gmail", value=getattr(config, 'SENDER_EMAIL', ""))
        st.session_state['app_password'] = st.text_input("App Password", type="password")
        st.session_state['live_mode'] = st.toggle("Live Outreach Mode")
        if st.form_submit_button("Save Gateway Config"): st.success("Gateway Updated!")
        
    if st.button("🗑️ Factory Reset Database"):
        db.clear_database()
        st.rerun()
