from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

# load sentiment model
model = joblib.load("sentiment_model.pkl")
tfidf = joblib.load("tfidf_vectorizer.pkl")

users_file = "users.csv"

# ================= HOME =================
@app.route("/")
def home():
    return render_template("signup.html")

# ================= LOGIN PAGE =================
@app.route("/loginpage")
def loginpage():
    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

# ================= SIGNUP =================
@app.route("/signup", methods=["POST"])
def signup():

    data = request.json
    username = data["username"]
    password = data["password"]

    users = pd.read_csv(users_file)

    if username in users["username"].values:
        return jsonify({"status":"exists"})

    new_user = pd.DataFrame([[username,password]],columns=["username","password"])
    users = pd.concat([users,new_user],ignore_index=True)

    users.to_csv(users_file,index=False)

    return jsonify({"status":"success"})


# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():

    data = request.json
    username = data["username"]
    password = data["password"]

    users = pd.read_csv(users_file)

    user = users[
        (users["username"]==username) &
        (users["password"]==password)
    ]

    if len(user)>0:
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"fail"})


# ================= SENTIMENT =================
@app.route("/predict", methods=["POST"])
def predict():

    text = request.json["text"]

    vect = tfidf.transform([text])
    prediction = model.predict(vect)[0]

    return jsonify({"sentiment":prediction})


# ================= CHART DATA =================
@app.route("/data")
def data():

    df = pd.read_csv("final_cleaned_social_media_data.csv")

    sentiment_counts = df["Sentiment"].value_counts().to_dict()

    risk_counts = df[df["Sentiment"]=="Negative"]["Entity"].value_counts().head(5).to_dict()

    return jsonify({
        "sentiment":sentiment_counts,
        "risk":risk_counts
    })


if __name__ == "__main__":
    app.run(debug=True)