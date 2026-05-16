# AI-Driven PR Risk & Brand Sentiment Analytics Platform

An end-to-end Machine Learning pipeline and interactive dashboard designed to monitor corporate reputation and detect PR threats. This system processes a high-volume dataset of over 70,000 social media records to classify public sentiment and trigger automated risk alerts for proactive crisis management.

Live Link: [Insert your Streamlit Cloud Link Here]

---

## 🚀 Key Features

* **High-Volume Analysis:** Built to ingest and process a massive dataset of 70,000+ social media mentions.
* **Core ML Engine:** Implements a Linear Support Vector Machine (Linear SVM) combined with TF-IDF Vectorization, achieving a **83% classification accuracy**.
* **Real-Time Interface:** An interactive Streamlit dashboard allowing users to analyze text entries or batch-process uploads.
* **Risk Mitigation:** Automatically calculates brand health metrics and flags potential PR crises in real-time.

---

## 🛠️ Tech Stack & Libraries

* **Language:** Python
* **Web Framework:** Streamlit
* **Machine Learning & NLP:** Scikit-learn, Pandas, Joblib
* **Data Visualization:** Matplotlib, Plotly

---

## 📁 Repository Structure

```text
├── app.py                 # Main Streamlit dashboard application
├── train_model.py         # Script to clean data and train the SVM pipeline
├── svm_model.pkl          # Trained and serialized SVM model
├── tfidf_vectorizer.pkl   # Saved TF-IDF vectorizer parameters
├── requirements.txt       # List of python dependencies
└── README.md              # Project documentation
