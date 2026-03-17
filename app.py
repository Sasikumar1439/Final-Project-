import streamlit as st
import joblib
import pandas as pd
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Brand PR Risk Monitor",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- LOAD MODEL ----------------
model = joblib.load("sentiment_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# ---------------- HEADER ----------------
st.title("🛡 Brand PR Risk Monitor")
st.markdown("---")

# ---------------- MAIN LAYOUT ----------------
col1, col2 = st.columns([1,2])

# -------- LEFT PANEL --------
with col1:

    st.subheader("PR Risk System")

    st.info("SVM Model: **83% Accuracy**")

    st.write(
        "Monitoring brand mentions for immediate reputational threats."
    )

# -------- RIGHT PANEL --------
with col2:

    st.subheader("🔍 Analyze Live Mention")

    brand = st.text_input("Brand Name")

    tweet = st.text_area(
        "Paste Tweet or News Snippet"
    )

    brand_select = st.selectbox(
        "Or select existing brand",
        ["Choose an option","Apple","Nike","Tesla","Samsung"]
    )

    if st.button("🔎 Assess PR Risk"):

        if tweet.strip()=="":
            st.warning("Please enter text")

        else:

            vect = tfidf.transform([tweet])
            prediction = model.predict(vect)[0]

            st.markdown("---")
            st.subheader("📊 Analysis Result")

            colA,colB,colC = st.columns(3)

            with colA:
                st.write("Brand")
                st.header(brand if brand else brand_select)

            with colB:
                st.write("Sentiment")
                st.header(prediction)

            with colC:

                if prediction=="Negative":
                    action="INVESTIGATE"
                elif prediction=="Neutral":
                    action="WATCH"
                else:
                    action="MONITOR"

                st.write("Action")
                st.header(action)

            if prediction=="Negative":

                st.error(
                    f"🚨 ALERT: HIGH PR RISK detected for {brand} — Sentiment: {prediction}"
                )
                
