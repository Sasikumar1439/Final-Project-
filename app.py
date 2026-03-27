import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

# --- 1. Page Configuration ---
st.set_page_config(page_title="Brand PR Risk Monitor", page_icon="🛡️", layout="wide")

# --- 2. Path & Session Memory Initialization ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, 'final_cleaned_social_media_data.csv')

if 'risk_history' not in st.session_state:
    st.session_state['risk_history'] = []

# --- 3. Load ML Assets ---
@st.cache_resource
def load_assets():
    try:
        model = joblib.load(os.path.join(BASE_DIR, 'sentiment_model.pkl'))
        tfidf = joblib.load(os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl'))
        return model, tfidf
    except Exception as e:
        st.error(f"Error loading model files: {e}")
        return None, None

model, tfidf = load_assets()

# --- 4. Sidebar Branding ---
st.sidebar.title("🛡️ PR Risk System")
st.sidebar.success("SVM Model: 83% Accuracy")
st.sidebar.info("Monitoring brand mentions for immediate reputational threats.")

# --- 5. Main Header ---
st.title("Real-Time Brand Monitoring & PR Risk Dashboard")
st.markdown("---")

# --- 6. Live Risk Analysis (Interactivity) ---
st.subheader("🔍 Analyze Live Mention")

# Brand name + comment input row
col_brand, col_text = st.columns([1, 2])

with col_brand:
    brand_name = st.text_input(
        "🏷️ Brand Name:",
        placeholder="e.g., Apple, Nike, Tesla..."
    )
    # Optional: dropdown of known brands from CSV
    try:
        df_preview = pd.read_csv(CSV_FILE)
        known_brands = sorted(df_preview['Entity'].dropna().unique().tolist())
        selected_brand = st.selectbox(
            "Or select existing brand:",
            options=["(Type manually above)"] + known_brands
        )
        # Use dropdown value if manual field is empty
        if not brand_name and selected_brand != "(Type manually above)":
            brand_name = selected_brand
    except:
        pass  # CSV not available, manual input only

with col_text:
    user_input = st.text_area(
        "📝 Paste Tweet or News Snippet:",
        height=120,
        placeholder="e.g., This new update is crashing my phone, terrible service!"
    )

# Assess button — full width below inputs
if st.button("🔎 Assess PR Risk", type="primary", use_container_width=True):
    if user_input and model:
        if not brand_name:
            brand_name = "Unknown Brand"

        # Model Prediction
        prediction = model.predict(tfidf.transform([user_input]))[0]
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Store in History
        new_entry = {
            "Time": timestamp,
            "Brand": brand_name,
            "Content": user_input[:60] + ("..." if len(user_input) > 60 else ""),
            "Sentiment": prediction,
            "Action": "🚨 INVESTIGATE" if prediction == 'Negative' else "✅ LOGGED"
        }
        st.session_state['risk_history'].insert(0, new_entry)

        # Show Results
        st.markdown("#### 📊 Analysis Result")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("Brand", brand_name)
        res_col2.metric("Sentiment", prediction)
        res_col3.metric("Action", "INVESTIGATE" if prediction == 'Negative' else "LOGGED")

        if prediction == 'Negative':
            st.error(f"🚨 ALERT: HIGH PR RISK detected for **{brand_name}** — Sentiment: {prediction}")
        elif prediction == 'Positive':
            st.success(f"✅ POSITIVE SENTIMENT detected for **{brand_name}** — Sentiment: {prediction}")
        else:
            st.info(f"⚖️ NEUTRAL SENTIMENT detected for **{brand_name}** — Sentiment: {prediction}")

    else:
        st.warning("Please enter text and ensure model files are in the folder.")

# --- 7. Risk Alert History Table ---
st.markdown("---")
with st.expander("📜 View Recent Scan History", expanded=False):
    if st.session_state['risk_history']:
        history_df = pd.DataFrame(st.session_state['risk_history'])

        # Color-code rows by sentiment
        def highlight_sentiment(row):
            if row['Sentiment'] == 'Negative':
                return ['background-color: #ffe6e6'] * len(row)
            elif row['Sentiment'] == 'Positive':
                return ['background-color: #e6ffe6'; colour:black] * len(row)
            else:
                return ['background-color: #f0f0ff'; colour:black] * len(row)

        st.dataframe(
            history_df.style.apply(highlight_sentiment, axis=1),
            use_container_width=True
        )

        col_dl, col_clr = st.columns([1, 1])
        with col_dl:
            csv_export = history_df.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download History CSV", csv_export, "scan_history.csv", "text/csv")
        with col_clr:
            if st.button("🗑️ Clear History"):
                st.session_state['risk_history'] = []
                st.rerun()
    else:
        st.write("No scans performed yet.")

# --- 8. Historical Analytics (Visualizations) ---
st.markdown("---")
st.subheader("📈 Historical Brand Analytics")

try:
    df_hist = pd.read_csv("final_cleaned_social_media_data.csv")

    tab1, tab2, tab3 = st.tabs(["PR Risk Analysis", "Global Sentiment Distribution", "Brand Deep Dive"])

    with tab1:
        neg_df = df_hist[df_hist['Sentiment'] == 'Negative']
        risk_counts = neg_df['Entity'].value_counts().nlargest(10).reset_index()
        risk_counts.columns = ['Brand', 'Negative Mentions']

        fig_bar = px.bar(
            risk_counts, x='Brand', y='Negative Mentions',
            title="Top 10 Brands Under PR Risk",
            color='Negative Mentions', color_continuous_scale='Reds'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        fig_pie = px.pie(
            df_hist, names='Sentiment',
            title="Overall Market Sentiment Ratio",
            color='Sentiment',
            color_discrete_map={
                'Positive': '#00CC96',
                'Negative': '#EF553B',
                'Neutral': '#636EFA'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab3:
        # Per-brand sentiment breakdown
        brands_list = sorted(df_hist['Entity'].dropna().unique().tolist())
        chosen_brand = st.selectbox("Select a brand to inspect:", brands_list, key="deepdive")

        brand_df = df_hist[df_hist['Entity'] == chosen_brand]
        brand_sentiment = brand_df['Sentiment'].value_counts().reset_index()
        brand_sentiment.columns = ['Sentiment', 'Count']

        fig_brand = px.bar(
            brand_sentiment, x='Sentiment', y='Count',
            title=f"Sentiment Breakdown for {chosen_brand}",
            color='Sentiment',
            color_discrete_map={
                'Positive': '#00CC96',
                'Negative': '#EF553B',
                'Neutral': '#636EFA'
            }
        )
        st.plotly_chart(fig_brand, use_container_width=True)

        st.markdown(f"**Sample mentions for {chosen_brand}:**")
        st.dataframe(
            brand_df[['Sentiment', 'TweetContent']].sample(min(5, len(brand_df))),
            use_container_width=True
        )

except Exception as e:
    st.error(f"Could not load charts. Error: {e}")
