import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Brand Risk Dashboard", layout="wide")

# ---------------- CUSTOM BACKGROUND ----------------
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        .stTextInput>div>div>input {
            background-color: #1e2a38;
            color: white;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_background()

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    model = joblib.load("sentiment_model.pkl")
    tfidf = joblib.load("tfidf_vectorizer.pkl")
    return model, tfidf

model, tfidf = load_model()

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("final_cleaned_social_media_data.csv")

try:
    data = load_data()
except:
    data = pd.DataFrame()

# ---------------- TITLE ----------------
st.title("🛡️ Brand Reputation & Risk Monitoring Dashboard")
st.write("Monitor brand mentions and detect PR risk instantly")

# ---------------- SEARCH SECTION ----------------
st.subheader("🔍 Brand Risk Analysis")

col1, col2 = st.columns(2)

with col1:
    brand_name = st.text_input("Enter Brand Name:")

with col2:
    comment = st.text_input("Enter Comment / Mention:")

# ---------------- RISK ANALYSIS ----------------
if brand_name and comment:

    full_text = brand_name + " " + comment

    vect = tfidf.transform([full_text])
    prediction = model.predict(vect)[0]

    st.divider()
    st.subheader("📊 Risk Result")

    if prediction.lower() == "negative":
        st.error(f"🚨 HIGH RISK for {brand_name}\nSentiment: NEGATIVE")

    elif prediction.lower() == "neutral":
        st.warning(f"⚠️ MEDIUM RISK for {brand_name}\nSentiment: NEUTRAL")

    else:
        st.success(f"✅ LOW RISK for {brand_name}\nSentiment: POSITIVE")

# ---------------- BRAND FILTER DASHBOARD ----------------
st.divider()
st.subheader("📈 Brand Analytics Dashboard")

if not data.empty:

    selected_brand = st.selectbox(
        "Select Brand to View Analytics",
        options=["All"] + sorted(data['Entity'].unique().tolist())
    )

    if selected_brand != "All":
        filtered_data = data[data['Entity'] == selected_brand]
    else:
        filtered_data = data

    col1, col2 = st.columns(2)

    with col1:
        fig1 = px.histogram(
            filtered_data,
            x="Sentiment",
            color="Sentiment",
            title="Sentiment Distribution"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        fig2 = px.pie(
            filtered_data,
            names="Sentiment",
            title="Sentiment Share"
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.warning("Dataset not found. Please add final_cleaned_social_media_data.csv")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Dashboard Info")
st.sidebar.write("Model: Naive Bayes")
st.sidebar.write("Vectorizer: TF‑IDF")
st.sidebar.write("Purpose: Brand Risk Detection")

  
