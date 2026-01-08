import streamlit as st
import pandas as pd
import joblib

st.set_page_config(page_title="Brand Sentiment Dashboard", layout="wide")

# Load model & vectorizer
model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")

# Load dataset
data = pd.read_csv("fully_cleaned_dashboard_data.csv")

st.title("📊 Real-Time Brand Sentiment Analysis")

st.write("This dashboard analyzes social media reviews and predicts sentiment.")

# Text input
user_input = st.text_input("Enter a tweet or review")

if user_input:
    vector = vectorizer.transform([user_input])
    prediction = model.predict(vector)[0]

    if prediction == "Positive":
        st.success("😊 Positive Sentiment")
    elif prediction == "Negative":
        st.error("😡 Negative Sentiment")
    else:
        st.info("😐 Neutral Sentiment")

st.subheader("Sample Data")
st.dataframe(data.head(20))
