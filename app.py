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
col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("Paste Tweet or News Snippet here:", height=100, placeholder="e.g., This new update is crashing my phone, terrible service!")
    
with col2:
    if st.button("Assess PR Risk", type="primary"):
        if user_input and model:
            # Model Prediction
            prediction = model.predict(tfidf.transform([user_input]))[0]
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Store in History
            new_entry = {
                "Time": timestamp,
                "Content": user_input[:50] + "...",
                "Sentiment": prediction,
                "Action": "🚨 INVESTIGATE" if prediction == 'Negative' else "✅ LOGGED"
            }
            st.session_state['risk_history'].insert(0, new_entry)
            
            # Show Results
            if prediction == 'Negative':
                st.error(f"🚨 ALERT: HIGH PR RISK ({prediction})")
            elif prediction == 'Positive':
                st.success(f"✅ POSITIVE SENTIMENT ({prediction})")
            else:
                st.info(f"⚖️ NEUTRAL SENTIMENT ({prediction})")
        else:
            st.warning("Please enter text and ensure model files are in the folder.")

# --- 7. Risk Alert History Table ---
with st.expander("📜 View Recent Scan History"):
    if st.session_state['risk_history']:
        history_df = pd.DataFrame(st.session_state['risk_history'])
        st.table(history_df)
        if st.button("Clear History"):
            st.session_state['risk_history'] = []
            st.rerun()
    else:
        st.write("No scans performed yet.")

# --- 8. Historical Analytics (Visualizations) ---
st.markdown("---")
st.subheader("📈 Historical Brand Analytics")

try:
    # Load the specific CSV mentioned
    df_hist = pd.read_csv(CSV_FILE)
    
    # Ensure column names match your project structure
    # Based on your notebook: ['TweetID', 'Entity', 'Sentiment', 'TweetContent']
    
    tab1, tab2 = st.tabs(["PR Risk Analysis", "Global Sentiment Distribution"])
    
    with tab1:
        # Show which brands have the most "Negative" mentions
        neg_df = df_hist[df_hist['Sentiment'] == 'Negative']
        risk_counts = neg_df['Entity'].value_counts().nlargest(10).reset_index()
        risk_counts.columns = ['Brand', 'Negative Mentions']
        
        fig_bar = px.bar(risk_counts, x='Brand', y='Negative Mentions', 
                         title="Top 10 Brands Under PR Risk",
                         color='Negative Mentions', color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        # Overall Sentiment Pie Chart
        fig_pie = px.pie(df_hist, names='Sentiment', title="Overall Market Sentiment Ratio",
                        color='Sentiment',
                        color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'})
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.error(f"Could not load charts. Error: {e}")
