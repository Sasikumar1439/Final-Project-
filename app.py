from flask import Flask, render_template, request, redirect, session, jsonify
import joblib
import pandas as pd

app = Flask(__name__)
app.secret_key = "keerthi_secret"

# ================= LOAD MODEL =================
model = joblib.load("sentiment_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

# ================= LOAD DATA =================
data = pd.read_csv("final_cleaned_social_media_data.csv")
data["Entity"] = data["Entity"].astype(str).str.strip()
data["Sentiment"] = data["Sentiment"].astype(str).str.strip()

# ================= LOAD USERS =================
users_data = pd.read_csv("users.csv")


# ================= HOME =================
@app.route("/")
def home():
    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    brands = sorted(data["Entity"].dropna().unique())
    return render_template("dashboard.html", brands=brands)


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    user = users_data[
        (users_data["username"] == username) &
        (users_data["password"] == password)
    ]

    if not user.empty:
        session["user"] = username
        return redirect("/dashboard")

    return render_template("login.html", error="Invalid Credentials")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data_json = request.get_json()

        if not data_json:
            return jsonify({"error": "No input provided"}), 400

        comment = data_json.get("comment", "").strip()
        brand = data_json.get("brand", "").strip()

        if not comment:
            return jsonify({"error": "Comment cannot be empty"}), 400

        vect = tfidf.transform([comment])
        prediction = model.predict(vect)[0]

        confidence = None
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(vect)[0]
            confidence = round(max(probabilities) * 100, 2)

        return jsonify({
            "brand": brand,
            "risk": prediction,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= BRAND STATS =================
@app.route("/brand_stats/<brand>")
def brand_stats(brand):

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        brand = brand.strip()

        if brand.lower() == "all":
            filtered_df = data.copy()
        else:
            filtered_df = data[
                data["Entity"].str.lower() == brand.lower()
            ]
        print("Selected Brand:", brand)
        print("Rows Found:", len(filtered_df))
    
        sentiment_counts = filtered_df["Sentiment"].value_counts()

        result = {
            "Positive": int(sentiment_counts.get("Positive", 0)),
            "Neutral": int(sentiment_counts.get("Neutral", 0)),
            "Negative": int(sentiment_counts.get("Negative", 0)),
            "Irrelevant": int(sentiment_counts.get("Irrelevant", 0)),
            "Total": int(len(filtered_df))
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
