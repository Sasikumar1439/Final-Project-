let barChart = null;
let pieChart = null;

/* =========================
   PREDICT RISK FUNCTION
========================= */
function predictRisk() {

    const brandInput = document.getElementById("brandInput");
    const commentInput = document.getElementById("commentInput");
    const resultDiv = document.getElementById("riskResult");

    if (!brandInput || !commentInput || !resultDiv) return;

    const brand = brandInput.value.trim();
    const comment = commentInput.value.trim();

    if (!brand || !comment) {
        alert("Please enter both Entity and Comment");
        return;
    }

    // Loading state
    resultDiv.innerHTML = `
        <div class="risk-alert medium-risk">
            ⏳ Analyzing sentiment...
        </div>
    `;

    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            brand: brand,
            comment: comment
        })
    })
    .then(response => {
        if (!response.ok) throw new Error("Prediction failed");
        return response.json();
    })
    .then(data => {

        if (!data || !data.risk) {
            resultDiv.innerHTML = `
                <div class="risk-alert high-risk">
                    ❌ Prediction failed. Try again.
                </div>
            `;
            return;
        }

        let sentiment = data.risk.toLowerCase();
        let riskHTML = "";

        if (sentiment === "positive") {
            riskHTML = `
                <div class="risk-alert low-risk">
                    ✅ LOW RISK for ${brand} | Sentiment: POSITIVE
                </div>`;
        }
        else if (sentiment === "neutral") {
            riskHTML = `
                <div class="risk-alert medium-risk">
                    ⚠ MEDIUM RISK for ${brand} | Sentiment: NEUTRAL
                </div>`;
        }
        else if (sentiment === "negative") {
            riskHTML = `
                <div class="risk-alert high-risk">
                    🚨 HIGH RISK for ${brand} | Sentiment: NEGATIVE
                </div>`;
        }
        else {
            riskHTML = `
                <div class="risk-alert medium-risk">
                    ℹ Result: ${data.risk}
                </div>`;
        }

        resultDiv.innerHTML = riskHTML;

        // Auto select brand in dropdown (if exists)
        const select = document.getElementById("brandSelect");
        if (select) {
            select.value = brand;
        }

        loadBrandStats();
    })
    .catch(error => {
        console.error("Prediction error:", error);
        resultDiv.innerHTML = `
            <div class="risk-alert high-risk">
                ❌ Server Error. Please try again.
            </div>
        `;
    });
}


/* =========================
   LOAD BRAND STATS
========================= */
function loadBrandStats() {

    const select = document.getElementById("brandSelect");
    if (!select) return;

    const brand = select.value;
    if (!brand) return;

    fetch(`/brand_stats/${brand}`)
    .then(response => response.json())
    .then(data => {

        const labels = ["Positive", "Neutral", "Negative", "Irrelevant"];
        const values = [
            data.Positive || 0,
            data.Neutral || 0,
            data.Negative || 0,
            data.Irrelevant || 0
        ];

        const barCanvas = document.getElementById("barChart");
        const pieCanvas = document.getElementById("pieChart");

        if (!barCanvas || !pieCanvas) return;

        // 🔥 Destroy old charts safely
        if (barChart) {
            barChart.destroy();
            barChart = null;
        }

        if (pieChart) {
            pieChart.destroy();
            pieChart = null;
        }

        // 🔥 Clear canvas manually
        barCanvas.getContext("2d").clearRect(0, 0, barCanvas.width, barCanvas.height);
        pieCanvas.getContext("2d").clearRect(0, 0, pieCanvas.width, pieCanvas.height);

        // Create new bar chart
        barChart = new Chart(barCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Sentiment Count",
                    data: values,
                    backgroundColor: ["#28a745","#ffc107","#dc3545","#6c757d"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

        // Create new pie chart
        pieChart = new Chart(pieCanvas.getContext("2d"), {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: ["#28a745","#ffc107","#dc3545","#6c757d"]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });

    })
    .catch(error => {
        console.error("Brand stats error:", error);
    });
}

/* =========================
   SAFE AUTO LOAD
========================= */
document.addEventListener("DOMContentLoaded", function () {

    const select = document.getElementById("brandSelect");

    if (select) {
        // 🔥 Attach change event manually
        select.addEventListener("change", function () {
            loadBrandStats();
        });

        // Load default charts on page load
        loadBrandStats();
    }

    const commentInput = document.getElementById("commentInput");

    if (commentInput) {
        commentInput.addEventListener("keypress", function (e) {
        commentInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                predictRisk();
            }
        });
    }
});

