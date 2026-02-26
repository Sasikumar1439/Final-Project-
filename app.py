import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import os

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
    base_path = os.path.dirname(os.path.abspath(__file__))

    model_path = os.path.join(base_path, "sentiment_model.pkl")
    tfidf_path = os.path.join(base_path, "tfidf_vectorizer.pkl")

    model = joblib.load(model_path)
    tfidf = joblib.load(tfidf_path)

    return model, tfidf

model, tfidf = load_model()

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_path, "final_cleaned_social_media_data.csv")

    df = pd.read_csv(csv_path)

    # Fix CSV if loaded as single column
    if len(df.columns) == 1:
        df = df[df.columns[0]].str.split(",", expand=True)
        df.columns = ['TweetID', 'Entity', 'Sentiment', 'TweetContent']

    return df

try:
    data = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
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

    if str(prediction).lower() == "negative":
        st.error(f"🚨 HIGH RISK for {brand_name} | Sentiment: NEGATIVE")

    elif str(prediction).lower() == "neutral":
        st.warning(f"⚠️ MEDIUM RISK for {brand_name} | Sentiment: NEUTRAL")

    else:
        st.success(f"✅ LOW RISK for {brand_name} | Sentiment: POSITIVE")

# ---------------- BRAND FILTER DASHBOARD ----------------
st.divider()
st.subheader("📈 Brand Analytics Dashboard")

if not data.empty and 'Entity' in data.columns:

    selected_brand = st.selectbox(
        "Select Brand to View Analytics",
        options=["All"] + sorted(data['Entity'].dropna().unique().tolist())
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
    st.warning("Dataset not found or columns incorrect. Please check CSV file.")

# ---------------- SIDEBAR ----------------
st.sidebar.title("Dashboard Info")
st.sidebar.write("Model: Naive Bayes")
st.sidebar.write("Vectorizer: TF-IDF")
st.sidebar.write("Purpose: Brand Risk Detection")

# ---------------- TOP 10 MOST POSITIVE BRANDS ----------------
st.divider()
st.subheader("🏆 Top 10 Positive Brand Comparison")

if not data.empty and 'Entity' in data.columns and 'Sentiment' in data.columns:

    # Filter only positive sentiment
    positive_data = data[data['Sentiment'].str.lower() == 'positive']

    # Count positives per brand
    positive_counts = (
        positive_data.groupby('Entity')
        .size()
        .reset_index(name='Positive Count')
        .sort_values(by='Positive Count', ascending=False)
        .head(10)
    )

    # Calculate percentage for pie chart
    total_positive = positive_counts['Positive Count'].sum()
    positive_counts['Percentage'] = (positive_counts['Positive Count'] / total_positive) * 100

    # Create two half-width columns
    col1, col2 = st.columns(2)

    # -------- BAR CHART (LEFT) --------
    with col1:
        fig_bar = px.bar(
            positive_counts,
            x='Entity',
            y='Positive Count',
            color='Entity',
            text='Positive Count',
            title='Brand Comparison by Positive Count'
        )

        # Remove brand names from side, keep only x-axis labels
        fig_bar.update_layout(
            xaxis_title="Brand",
            yaxis_title="Positive Count",
            showlegend=False
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    # -------- PIE CHART (RIGHT) --------
    with col2:
        fig_pie = px.pie(
            positive_counts,
            names='Entity',
            values='Percentage',
            title='Top 10 Positive Brands (Percentage Share)'
        )

        # Show only percentage and brand name
        fig_pie.update_traces(textinfo='percent+label')

        st.plotly_chart(fig_pie, use_container_width=True)

else:
    st.warning("Cannot display Top 10 Positive Brands. Check dataset columns.")
