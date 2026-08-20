// ===============================
// Person 2 - Landslide Chart
// ===============================

async function loadHazardChart() {
    try {
        const response = await fetch("http://localhost:8001/api/mock-hazards");

        if (!response.ok) {
            throw new Error("API request failed");
        }

        const data = await response.json();

        console.log("Hazard API response:", data);

        // Backend returns: { hazards: ... }
        const hazards = data.hazards;

        if (!hazards || !Array.isArray(hazards)) {
            console.error("Hazard data is not an array:", hazards);
            return;
        }

        // Get risk values from the Hazard Agent output
        const risks = hazards.map(item =>
            Number(
                item.risk_score ??
                item.risk ??
                item.score ??
                item.riskScore
            )
        );

        console.log("Risk scores:", risks);

        if (risks.some(value => isNaN(value))) {
            console.error("Risk score not found in API response");
            return;
        }

        updateChart(risks);

    } catch (error) {
        console.error("Could not load hazard data:", error);
    }
}


// ===============================
// Update existing SVG chart
// ===============================

function updateChart(risks) {

    const svg = document.querySelector(".main-chart-svg");

    if (!svg) {
        console.error("Chart SVG not found");
        return;
    }

    // Existing chart line
    const line = svg.querySelector('path[fill="none"]');

    if (!line) {
        console.error("Chart line not found");
        return;
    }

    // Chart dimensions
    const startX = 50;
    const endX = 870;
    const topY = 30;
    const bottomY = 180;

    const step = risks.length > 1
        ? (endX - startX) / (risks.length - 1)
        : 0;

    // Convert risk percentage to SVG Y position
    function getY(risk) {
        risk = Math.max(0, Math.min(100, risk));

        return bottomY -
            (risk / 100) * (bottomY - topY);
    }

    // Create points
    const points = risks.map((risk, index) => {
        return {
            x: startX + index * step,
            y: getY(risk),
            risk: risk
        };
    });

    // Create SVG line path
    let pathData = "";

    points.forEach((point, index) => {

        if (index === 0) {
            pathData += `M ${point.x},${point.y}`;
        } else {
            pathData += ` L ${point.x},${point.y}`;
        }

    });

    // Replace hardcoded line
    line.setAttribute("d", pathData);


    // ===============================
    // Update data point circles
    // ===============================

    const circles = svg.querySelectorAll("circle");

    circles.forEach((circle, index) => {

        if (points[index]) {

            circle.setAttribute("cx", points[index].x);
            circle.setAttribute("cy", points[index].y);

        }

    });


    // ===============================
    // Update current score
    // ===============================

    const scoreText = document.querySelector(".live-update-text strong");

    if (scoreText && risks.length > 0) {

        const latestRisk = risks[risks.length - 1];

        scoreText.textContent = latestRisk.toFixed(1) + "%";

    }

}


// Load chart when page opens
document.addEventListener("DOMContentLoaded", loadHazardChart);