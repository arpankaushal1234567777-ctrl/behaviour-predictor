const API_URL = "http://127.0.0.1:8000";
const form = document.getElementById("logForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const sleep = parseFloat(document.getElementById("sleep").value);
    const study = parseFloat(document.getElementById("study").value);
    const screen = parseFloat(document.getElementById("screen").value);
    const exercise = parseFloat(document.getElementById("exercise").value);

    const resultDiv = document.getElementById("result");
    resultDiv.innerText = "Analyzing...";

    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                sleep_hours: sleep,
                study_hours: study,
                screen_time: screen,
                exercise_minutes: exercise
            })
        });

        const data = await response.json();

        if (!response.ok) {
            resultDiv.innerText = "Error: " + (data.detail || "Something went wrong");
            return;
        }

        const score = data.predicted_productivity;

        let level = "";
        let color = "";

        if (score < 40) {
            level = "Low Productivity";
            color = "red";
        } else if (score < 70) {
            level = "Medium Productivity";
            color = "orange";
        } else {
            level = "High Productivity";
            color = "green";
        }

        resultDiv.innerHTML = `
            <div style="color:${color}; font-size:20px;">
                Productivity Score: ${score.toFixed(2)}
                <br/>
                Level: ${level}
                <br/>
                Insight: ${data.insight}
            </div>
        `;

    } catch (error) {
        resultDiv.innerText = "Error connecting to backend";
    }
});