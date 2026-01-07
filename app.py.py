import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

st.set_page_config(page_title="Real-Time Brand Guardian", layout="wide")

# --- STEP 1: LOAD DATA WITH AGGRESSIVE MAPPING ---
@st.cache_data
def load_and_map():
    # Ensure this matches the file I sent you
    filename = 'fully_cleaned_dashboard_data.xls' 
    
    if not os.path.exists(filename):
        st.error(f"❌ File '{filename}' not found. Please ensure the CSV is in the same folder as this script.")
        return None, None

    df = pd.read_csv(filename)
    
    # Aggressive Search Logic
    mapping = {}
    all_cols = [c.strip() for c in df.columns]
    
    for original_col in df.columns:
        col = original_col.lower().strip()
        
        # 1. Find Sentiment (priority: 'airline_sentiment', then 'sentiment')
        if 'sentiment' in col and 'conf' not in col and 'gold' not in col:
            mapping['sent'] = original_col
            
        # 2. Find Text (priority: 'clean_text', then 'text', then 'tweet')
        if 'clean_text' in col or ('text' in col and 'coord' not in col) or 'tweet' in col:
            if 'sent' not in col: # Don't accidentally pick 'airline_sentiment' as text
                mapping['text'] = original_col
                
        # 3. Find Brand (priority: 'airline', then 'brand', then 'entity')
        if 'airline' in col or 'brand' in col or 'entity' in col:
            if 'sent' not in col: # Don't pick 'airline_sentiment' as brand
                mapping['brand'] = original_col

    # Fallback: If still missing, pick the most likely candidates by index
    if 'sent' not in mapping: mapping['sent'] = 'airline_sentiment' if 'airline_sentiment' in df.columns else df.columns[2]
    if 'text' not in mapping: mapping['text'] = 'clean_text' if 'clean_text' in df.columns else df.columns[10]
    if 'brand' not in mapping: mapping['brand'] = 'airline' if 'airline' in df.columns else df.columns[5]

    return df, mapping

df_full, mapping = load_and_map()

# --- STEP 2: DASHBOARD UI ---
st.title("📈 Real-Time Brand Sentiment Monitor")

if df_full is not None:
    # Diagnostic Info (Optional: Remove after it works)
    with st.expander("🔍 View Detected Columns"):
        st.write(f"**Found Sentiment:** {mapping.get('sent')}")
        st.write(f"**Found Text:** {mapping.get('text')}")
        st.write(f"**Found Brand:** {mapping.get('brand')}")

    # Sidebar
    st.sidebar.header("Alert Settings")
    threshold = st.sidebar.slider("Negative Alert Threshold (%)", 5, 50, 25)
    
    # UI Slots
    alert_slot = st.empty()
    metric_slot = st.empty()
    col1, col2 = st.columns(2)
    chart_slot = col1.empty()
    trend_slot = col2.empty()

    if st.sidebar.button("▶️ Start Live Stream"):
        neg_history = []
        
        for i in range(1, 51):
            # Batching
            batch = df_full.sample(min(25, len(df_full)))
            
            # Sentiment Calculation
            # Standardize column for comparison
            batch['sent_clean'] = batch[mapping['sent']].astype(str).str.lower().str.strip()
            neg_pct = (len(batch[batch['sent_clean'] == 'negative']) / len(batch)) * 100
            
            neg_history.append(neg_pct)
            if len(neg_history) > 20: neg_history.pop(0)

            # 1. Alerts
            with alert_slot:
                if neg_pct >= threshold:
                    st.error(f"### 🚨 PR RISK ALERT \n Negative sentiment at **{neg_pct:.1f}%**! Action required.")
                else:
                    st.success(f"### ✅ BRAND STABLE \n Negative sentiment at **{neg_pct:.1f}%**.")

            # 2. Metrics
            with metric_slot:
                m1, m2, m3 = st.columns(3)
                m1.metric("Live Mentions", len(batch))
                m2.metric("Negative Ratio", f"{neg_pct:.1f}%")
                m3.metric("Current Brand", batch[mapping['brand']].iloc[0])

            # 3. Bar Chart
            with chart_slot:
                fig_bar = px.bar(batch, x=mapping['brand'], color=mapping['sent'], 
                                 title="Real-Time Sentiment Breakdown", barmode='group',
                                 color_discrete_map={'negative':'#ff4b4b', 'neutral':'#f1c40f', 'positive':'#2ecc71'})
                st.plotly_chart(fig_bar, use_container_width=True)

            # 4. Trend Line
            with trend_slot:
                trend_df = pd.DataFrame({"Update": range(len(neg_history)), "Neg %": neg_history})
                fig_line = px.line(trend_df, x="Update", y="Neg %", title="Sentiment Trend")
                fig_line.add_hline(y=threshold, line_dash="dash", line_color="red")
                st.plotly_chart(fig_line, use_container_width=True)

            time.sleep(3)
    else:
        st.info("System Ready. Click 'Start Live Stream' to begin.")