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
import agents.fiverr_agent
import agents.freelancer_agent
importlib.reload(agents.hunter_agent)
importlib.reload(agents.builder_agent)
importlib.reload(agents.research_agent)
importlib.reload(agents.scraper_agent)
importlib.reload(agents.fiverr_agent)
importlib.reload(agents.freelancer_agent)

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
SESSION_FILE = os.path.join(current_dir, ".session")

if 'authenticated' not in st.session_state:
    # Check if a persistent session file exists
    if os.path.exists(SESSION_FILE):
        st.session_state['authenticated'] = True
    else:
        st.session_state['authenticated'] = False

def login():
    st.markdown("<h1 style='text-align: center; color: white;'>👑 AI Agency Portal</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("Login"):
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            remember = st.checkbox("Keep me logged in ( survives refresh )", value=True)
            if st.form_submit_button("Launch Swarm"):
                if user == config.DASHBOARD_USERNAME and pw == config.DASHBOARD_PASSWORD:
                    st.session_state['authenticated'] = True
                    if remember:
                        with open(SESSION_FILE, "w") as f:
                            f.write("authenticated")
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
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
    st.rerun()

# --- Overview ---
if menu == "🚀 Overview":
    st.title("🚀 Strategic Overview")
    leads = db.get_all_leads()
    total = len(leads['ids']) if leads['ids'] else 0
    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(f'<div class="metric-card"><h3>Total Leads</h3><h1>{total}</h1></div>', unsafe_allow_html=True)
    with col2: st.markdown(f'<div class="metric-card"><h3>Active Swarms</h3><h1>5</h1></div>', unsafe_allow_html=True)
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
            df_data.append({
                "Name": m.get('name', 'N/A'), 
                "Website": m.get('website', 'N/A'), 
                "Email": m.get('email', 'Not Found'),
                "LinkedIn": m.get('linkedin', 'N/A'),
                "Niche": m.get('niche', 'N/A')
            })
        
        st.dataframe(pd.DataFrame(df_data), use_container_width=True)
        
        st.markdown("---")
        sel = st.selectbox("Select Lead to Action", [l.get('name', 'Unknown') for l in leads['metadatas']])
        
        for i in range(len(leads['ids'])):
            if leads['metadatas'][i].get('name') == sel:
                lead_data = leads['metadatas'][i]
                pitch_content = leads['documents'][i]
                
                col1, col2 = st.columns([2, 1])
                lead_id = leads['ids'][i]
                with col1:
                    st.markdown("#### 📝 Edit Outreach Message")
                    # Capture edited text
                    current_pitch = st.text_area("Edit your message here", value=pitch_content, height=450, key=f"edit_pitch_{lead_id}")
                    
                    if st.button("💾 Save & Update Message", key=f"save_{lead_id}"):
                        db.update_lead_pitch(lead_id, current_pitch)
                        st.success("Message saved! Now you can send it.")
                        time.sleep(0.5)
                        st.rerun()
                
                with col2:
                    st.markdown("#### 📧 Outreach Console")
                    recipient_email = st.text_input("Recipient Email", value=lead_data.get('email', ''), key=f"email_{lead_id}")
                    
                    # Social Contact Options
                    found_linkedin = lead_data.get('linkedin', '')
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if found_linkedin:
                            st.link_button("🔗 LinkedIn Profile", found_linkedin, use_container_width=True)
                        else:
                            st.button("🔗 No LinkedIn Found", disabled=True, use_container_width=True, key=f"noln_{lead_id}")
                    
                    st.markdown("---")
                    
                    if st.button("🚀 Send THIS Edited Message", key=f"send_{lead_id}"):
                        if not recipient_email:
                            st.error("Email required!")
                        else:
                            with st.spinner("Transmitting..."):
                                master.sender.sender_email = st.session_state.get('sender_email', getattr(config, 'SENDER_EMAIL', ""))
                                master.sender.app_password = st.session_state.get('app_password', getattr(config, 'EMAIL_PASSWORD', ""))
                                master.sender.dry_run = not st.session_state.get('live_mode', False)
                                
                                # Send the EXACT content from the text area
                                if master.sender.send_email(sel, recipient_email, current_pitch):
                                    if master.sender.dry_run:
                                        st.warning("⚠️ Message Logged (Dry Run Mode). Enable 'Live Mode' in Settings.")
                                    else:
                                        st.success("🚀 Message Sent Successfully!")
                                        st.balloons()
                                else: st.error("Transmission failed.")
                
                if st.button("🗑️ Purge Lead Data", key=f"purge_btn_{lead_id}"):
                    db.delete_lead(lead_id)
                    st.rerun()

# --- Project Delivery ---
elif menu == "🏗️ Project Delivery":
    st.title("🏗️ Project Factory")
    leads = db.get_all_leads()
    if leads['ids']:
        for i in range(len(leads['ids'])):
            name = leads['metadatas'][i].get('name', 'Unknown')
            lead_id = leads['ids'][i]
            pitch_data = leads['documents'][i]
            
            with st.expander(f"💎 {name}"):
                st.markdown("### 🛠️ Step 1: Configuration")
                custom_reqs = st.text_area("📝 Customer Specific Requirements / Instructions", 
                                          value=f"Build a custom AI solution for {name} that focuses on their niche. Ensure it is professional and functional.",
                                          key=f"reqs_{i}", height=100)
                
                delivery_email = st.text_input("Customer Email", value=leads['metadatas'][i].get('email', ''), key=f"e_{i}")
                
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                # --- DEMO BUILD ---
                with col1:
                    st.subheader("1️⃣ Demo Phase")
                    if st.button(f"🏗️ Build Demo Roadmap", key=f"build_demo_{i}"):
                        with st.spinner("AI is designing roadmap..."):
                            path = builder_swarm.launch_project(name, f"DEMO ONLY: {pitch_data}\n\nREQS: {custom_reqs}")
                            st.session_state[f"demo_path_{i}"] = path
                            st.success("Demo Roadmap Ready!")
                    
                    if f"demo_path_{i}" in st.session_state:
                        if st.button(f"🎥 Send Demo to Gmail", key=f"send_demo_{i}"):
                            with st.spinner("Sending Demo..."):
                                roadmap_file = os.path.join(st.session_state[f"demo_path_{i}"], "roadmap.md")
                                roadmap_content = open(roadmap_file, "r").read() if os.path.exists(roadmap_file) else "Custom AI Roadmap prepared."
                                demo_pitch = f"Hello {name},\n\nI've engineered a custom AI Roadmap for your business.\n\nROADMAP PREVIEW:\n{roadmap_content[:800]}...\n\nLet's discuss this demo!"
                                
                                master.sender.sender_email = st.session_state.get('sender_email', getattr(config, 'SENDER_EMAIL', ""))
                                master.sender.app_password = st.session_state.get('app_password', getattr(config, 'EMAIL_PASSWORD', ""))
                                master.sender.dry_run = not st.session_state.get('live_mode', False)
                                
                                if master.sender.send_email(f"DEMO: {name}", delivery_email, demo_pitch):
                                    st.success("Demo Sent Successfully!")
                                else: st.error("Failed to send demo.")

                # --- FULL PROJECT BUILD ---
                with col2:
                    st.subheader("2️⃣ Project Phase")
                    if st.button(f"🚀 Build Full Project", key=f"build_full_{i}"):
                        with st.spinner("AI Factory is coding full solution..."):
                            path = builder_swarm.launch_project(name, f"FULL BUILD: {pitch_data}\n\nREQS: {custom_reqs}")
                            st.session_state[f"full_path_{i}"] = path
                            st.success("Full Project Engineered!")
                    
                    if f"full_path_{i}" in st.session_state:
                        if st.button(f"📬 Deliver to Gmail", key=f"send_full_{i}"):
                            with st.spinner("Delivering Project..."):
                                delivery_pitch = f"Hello {name},\n\nYour full custom AI Solution is ready for deployment.\n\nAll assets have been prepared."
                                master.sender.sender_email = st.session_state.get('sender_email', getattr(config, 'SENDER_EMAIL', ""))
                                master.sender.app_password = st.session_state.get('app_password', getattr(config, 'EMAIL_PASSWORD', ""))
                                master.sender.dry_run = not st.session_state.get('live_mode', False)
                                
                                if master.sender.send_email(f"PROJECT: {name}", delivery_email, delivery_pitch):
                                    st.success("Project Delivered Successfully!")
                                else: st.error("Failed to deliver project.")

                st.markdown("---")
                st.markdown("### 📑 Proposal & Agreement")
                col_p1, col_p2 = st.columns(2)
                with col_p1:
                    proj_price = st.number_input("Project Price", value=500, key=f"price_{i}")
                    currency = st.selectbox("Currency", ["USD", "INR", "GBP", "EUR"], key=f"curr_{i}")
                with col_p2:
                    milestones = st.text_area("Milestones", value="- 30% Advance Deposit\n- 40% On First Prototype\n- 30% Final Delivery", height=100, key=f"ms_{i}")
                
                if st.button(f"📄 Generate Agreement", key=f"gen_{i}"):
                    proposal_text = builder_swarm.generate_proposal(name, f"AI Automation Suite for {name}", proj_price, currency, milestones)
                    st.session_state[f"proposal_{i}"] = proposal_text
                
                if f"proposal_{i}" in st.session_state:
                    st.markdown('<div class="email-box">', unsafe_allow_html=True)
                    st.markdown(st.session_state[f"proposal_{i}"])
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.download_button("📥 Download Agreement (Markdown)", st.session_state[f"proposal_{i}"], file_name=f"Agreement_{name}.md", key=f"dl_{i}")

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
