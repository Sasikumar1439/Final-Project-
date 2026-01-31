import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os

# --- 1. Page Configuration ---
st.set_page_config(page_title="Brand PR Risk Monitor", page_icon="🛡️", layout="wide")

# --- 2. Load the SVM Model & Vectorizer ---
import streamlit as st
import joblib
import os

# Get the folder where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_model():
    # Join the folder path with the filenames
    model_path = os.path.join(BASE_DIR, 'sentiment_model.pkl')
    tfidf_path = os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl')
    
    # Error handling if files are still missing
    if not os.path.exists(model_path):
        st.error(f"❌ File not found: {model_path}. Please run train_model.py first!")
        st.stop()
        
    model = joblib.load(model_path)
    tfidf = joblib.load(tfidf_path)
    return model, tfidf

model, tfidf = load_model()

# --- 3. Sidebar Status ---
st.sidebar.title("System Status")
st.sidebar.success("SVM Model: Active (83% Acc)")
st.sidebar.info("Monitoring for High-Risk Negative Sentiment spikes across social platforms.")

# --- 4. Main Dashboard Header ---
st.title("🛡️ Real-Time Brand Monitoring & PR Risk Dashboard")
st.markdown("---")

# --- 5. Real-Time Prediction (The "Risk Detector") ---
st.subheader("🔍 Analyze Live Mention")
col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("Paste Tweet or News Snippet:", placeholder="Example: The service is terrible and I want a refund!")
    
with col2:
    if st.button("Assess PR Risk", type="primary"):
        if user_input and model:
            # Transform text and predict
            prediction = model.predict(tfidf.transform([user_input]))[0]
            
            if prediction == 'Negative':
                st.error(f"🚨 ALERT: HIGH PR RISK ({prediction})")
                st.write("**Action:** Immediate response recommended.")
            elif prediction == 'Positive':
                st.success(f"✅ RISK LEVEL: NONE ({prediction})")
                st.write("**Action:** Brand Advocate detected. Consider engaging.")
            else:
                st.info(f"⚖️ RISK LEVEL: LOW ({prediction})")
        else:
            st.warning("Please enter text to analyze.")

# --- 6. Historical Brand Health (Analytics) ---
st.markdown("---")
st.subheader("📈 Historical Brand Analytics")

try:
    df = pd.read_csv('final_cleaned_social_media_data.csv')
    
    tab1, tab2 = st.tabs(["Risk by Brand", "Global Sentiment"])
    
    with tab1:
        # Show which brands are facing the most "Negative" mentions
        neg_df = df[df['Sentiment'] == 'Negative']
        risk_counts = neg_df['Entity'].value_counts().nlargest(10).reset_index()
        risk_counts.columns = ['Brand', 'Negative Mentions']
        
        fig_bar = px.bar(risk_counts, x='Brand', y='Negative Mentions', 
                         title="Top 10 Brands Under PR Risk",
                         color='Negative Mentions', color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        # Overall Sentiment Distribution
        fig_pie = px.pie(df, names='Sentiment', title="Overall Market Sentiment",
                        color='Sentiment',
                        color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'})
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.warning("Could not load historical charts. Ensure the CSV file is in the folder.")import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os

# --- 1. Page Configuration ---
st.set_page_config(page_title="Brand PR Risk Monitor", page_icon="🛡️", layout="wide")

# --- 2. Load the SVM Model & Vectorizer ---
import streamlit as st
import joblib
import os

# Get the folder where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@st.cache_resource
def load_model():
    # Join the folder path with the filenames
    model_path = os.path.join(BASE_DIR, 'sentiment_model.pkl')
    tfidf_path = os.path.join(BASE_DIR, 'tfidf_vectorizer.pkl')
    
    # Error handling if files are still missing
    if not os.path.exists(model_path):
        st.error(f"❌ File not found: {model_path}. Please run train_model.py first!")
        st.stop()
        
    model = joblib.load(model_path)
    tfidf = joblib.load(tfidf_path)
    return model, tfidf

model, tfidf = load_model()

# --- 3. Sidebar Status ---
st.sidebar.title("System Status")
st.sidebar.success("SVM Model: Active (83% Acc)")
st.sidebar.info("Monitoring for High-Risk Negative Sentiment spikes across social platforms.")

# --- 4. Main Dashboard Header ---
st.title("🛡️ Real-Time Brand Monitoring & PR Risk Dashboard")
st.markdown("---")

# --- 5. Real-Time Prediction (The "Risk Detector") ---
st.subheader("🔍 Analyze Live Mention")
col1, col2 = st.columns([2, 1])

with col1:
    user_input = st.text_area("Paste Tweet or News Snippet:", placeholder="Example: The service is terrible and I want a refund!")
    
with col2:
    if st.button("Assess PR Risk", type="primary"):
        if user_input and model:
            # Transform text and predict
            prediction = model.predict(tfidf.transform([user_input]))[0]
            
            if prediction == 'Negative':
                st.error(f"🚨 ALERT: HIGH PR RISK ({prediction})")
                st.write("**Action:** Immediate response recommended.")
            elif prediction == 'Positive':
                st.success(f"✅ RISK LEVEL: NONE ({prediction})")
                st.write("**Action:** Brand Advocate detected. Consider engaging.")
            else:
                st.info(f"⚖️ RISK LEVEL: LOW ({prediction})")
        else:
            st.warning("Please enter text to analyze.")

# --- 6. Historical Brand Health (Analytics) ---
st.markdown("---")
st.subheader("📈 Historical Brand Analytics")

try:
    df = pd.read_csv('final_cleaned_social_media_data.csv')
    
    tab1, tab2 = st.tabs(["Risk by Brand", "Global Sentiment"])
    
    with tab1:
        # Show which brands are facing the most "Negative" mentions
        neg_df = df[df['Sentiment'] == 'Negative']
        risk_counts = neg_df['Entity'].value_counts().nlargest(10).reset_index()
        risk_counts.columns = ['Brand', 'Negative Mentions']
        
        fig_bar = px.bar(risk_counts, x='Brand', y='Negative Mentions', 
                         title="Top 10 Brands Under PR Risk",
                         color='Negative Mentions', color_continuous_scale='Reds')
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        # Overall Sentiment Distribution
        fig_pie = px.pie(df, names='Sentiment', title="Overall Market Sentiment",
                        color='Sentiment',
                        color_discrete_map={'Positive':'#00CC96', 'Negative':'#EF553B', 'Neutral':'#636EFA'})
        st.plotly_chart(fig_pie, use_container_width=True)

except Exception as e:
    st.warning("Could not load historical charts. Ensure the CSV file is in the folder.")
