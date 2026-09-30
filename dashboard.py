import streamlit as st
import pandas as pd
from database import SessionLocal, Ad

st.set_page_config(page_title="AdOps Dashboard", layout="wide")

# Helper to query DB
def get_all_ads():
    with SessionLocal() as db:
        return db.query(Ad).all()

st.title("📊 AdOps Management Dashboard")

tab1, tab2 = st.tabs(["Performance Analytics", "Campaign Management"])

# --- TAB 1: Analytics ---
with tab1:
    ads = get_all_ads()
    if ads:
        # Convert SQLAlchemy objects to dictionaries for Pandas
        data = [{
            "ID": ad.id, "Name": ad.name, "Advertiser": ad.advertiser,
            "Active": ad.active, "Impressions": ad.impressions, "Clicks": ad.clicks
        } for ad in ads]
        
        df = pd.DataFrame(data)
        df["CTR (%)"] = (df["Clicks"] / df["Impressions"] * 100).fillna(0).round(2)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Impressions", df["Impressions"].sum())
        col2.metric("Total Clicks", df["Clicks"].sum())
        
        avg_ctr = round((df["Clicks"].sum() / df["Impressions"].sum() * 100), 2) if df["Impressions"].sum() > 0 else 0
        col3.metric("System-wide CTR", f"{avg_ctr}%")
        
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No campaigns found. Create one in the Campaign Management tab.")

# --- TAB 2: Management ---
with tab2:
    st.subheader("Launch New Campaign")
    with st.form("new_campaign_form"):
        name = st.text_input("Campaign Name")
        adv = st.text_input("Advertiser")
        ad_type = st.selectbox("Ad Format", ["banner", "sidebar", "video", "native"])
        url = st.text_input("Destination URL (e.g., https://example.com)")
        
        if st.form_submit_button("Create Ad"):
            with SessionLocal() as db:
                new_ad = Ad(name=name, advertiser=adv, type=ad_type, url=url)
                db.add(new_ad)
                db.commit()
            st.success(f"Campaign '{name}' created successfully!")
            
            # Generate the tag (Using the 'name' variable from your form inputs)
            ad_tag = f'''<iframe src="http://localhost:8000?campaign={name}" width="300" height="250" frameborder="0"></iframe>'''
            
            st.write("**Copy your Ad Tag:**")
            st.code(ad_tag, language='html')

    st.divider()
    st.subheader("Manage Existing Campaigns")
    ads = get_all_ads()
    
    if not ads:
        st.info("No campaigns to manage.")
    else:
        for ad in ads:
            # Create three columns: Name/Status, Toggle Button, Delete Button
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"**{ad.name}** ({ad.advertiser}) - Current status: {'🟢 Active' if ad.active else '🔴 Paused'}")
            
            # Toggle Button
            if col2.button(f"{'Pause' if ad.active else 'Activate'}", key=f"toggle_{ad.id}"):
                with SessionLocal() as db:
                    db_ad = db.query(Ad).filter(Ad.id == ad.id).first()
                    db_ad.active = not db_ad.active
                    db.commit()
                st.rerun()
                
            # Delete Button
            if col3.button("🗑️ Delete", key=f"delete_{ad.id}", type="primary"):
                with SessionLocal() as db:
                    db.query(Ad).filter(Ad.id == ad.id).delete()
                    db.commit()
                st.success(f"Deleted campaign: {ad.name}")
                st.rerun()
