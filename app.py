import streamlit as st
import pandas as pd
import plotly.express as px
import time
import os

st.set_page_config(page_title="Real-Time Brand Guardian", layout="wide")

# --- STEP 1: LOAD DATA WITH AGGRESSIVE MAPPING ---
@st.cache_data
def load_and_map():
    filename = 'fully_cleaned_social_media_data.csv'  # CSV 

    if not os.path.exists(filename):
        st.error(f"❌ File '{filename}' not found.")
        return None, None

    df = pd.read_csv(filename)

    mapping = {}

    for original_col in df.columns:
        col = original_col.lower().strip()

        if 'sentiment' in col and 'conf' not in col and 'gold' not in col:
            mapping['sent'] = original_col

        if 'clean_text' in col or ('text' in col and 'coord' not in col) or 'tweet' in col:
            if 'sent' not in col:
                mapping['text'] = original_col

        if 'airline' in col or 'brand' in col or 'entity' in col:
            if 'sent' not in col:
                mapping['brand'] = original_col

    # Fallbacks
    mapping.setdefault('sent', df.columns[2])
    mapping.setdefault('text', df.columns[10])
    mapping.setdefault('brand', df.columns[5])

    return df, mapping


df_full, mapping = load_and_map()

# --- STEP 2: DASHBOARD UI ---
st.title("📈 Real-Time Brand Sentiment Monitor")

if df_full is not None:

    with st.expander("🔍 View Detected Columns"):
        st.write("Sentiment:", mapping['sent'])
        st.write("Text:", mapping['text'])
        st.write("Brand:", mapping['brand'])

    st.sidebar.header("Alert Settings")
    threshold = st.sidebar.slider("Negative Alert Threshold (%)", 5, 50, 25)

    # Placeholders (IMPORTANT)
    alert_slot = st.empty()
    metric_slot = st.empty()
    col1, col2 = st.columns(2)
    chart_slot = col1.empty()
    trend_slot = col2.empty()

    if st.sidebar.button("▶️ Start Live Stream"):

        neg_history = []

        for i in range(50):

            batch = df_full.sample(min(25, len(df_full)))
            batch['sent_clean'] = batch[mapping['sent']].astype(str).str.lower().str.strip()

            neg_pct = (batch['sent_clean'].eq('negative').mean()) * 100
            neg_history.append(neg_pct)
            if len(neg_history) > 20:
                neg_history.pop(0)

            # ALERTS
            with alert_slot:
                if neg_pct >= threshold:
                    st.error(f"🚨 **PR RISK ALERT** — Negative sentiment at **{neg_pct:.1f}%**")
                else:
                    st.success(f"✅ Brand Stable — Negative sentiment at **{neg_pct:.1f}%**")

            # METRICS
            with metric_slot:
                m1, m2, m3 = st.columns(3)
                m1.metric("Live Mentions", len(batch))
                m2.metric("Negative %", f"{neg_pct:.1f}%")
                m3.metric("Brand", batch[mapping['brand']].iloc[0])

            # BAR CHART (NO KEY)
            with chart_slot:
                fig_bar = px.bar(
                    batch,
                    x=mapping['brand'],
                    color=mapping['sent'],
                    barmode='group',
                    title="Real-Time Sentiment Breakdown"
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # TREND LINE (NO KEY)
            with trend_slot:
                trend_df = pd.DataFrame({
                    "Update": range(len(neg_history)),
                    "Negative %": neg_history
                })

                fig_line = px.line(
                    trend_df,
                    x="Update",
                    y="Negative %",
                    title="Negative Sentiment Trend"
                )
                fig_line.add_hline(y=threshold, line_dash="dash", line_color="red")

                st.plotly_chart(fig_line, use_container_width=True)

            time.sleep(3)

    else:
        st.info("System Ready. Click **Start Live Stream** to begin.")

