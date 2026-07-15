const GREEN = "#2f6b4f";
const PALETTE = ["#2f6b4f", "#1c3d5a", "#c77d3a", "#5b8a72", "#8a5b8a"];

const TMACharts = {
    popularTreks(canvas, stats) {
        return new Chart(canvas, {
            type: "bar",
            data: {
                labels: stats.popular_treks.map(t => t.name),
                datasets: [{
                    label: "Bookings",
                    data: stats.popular_treks.map(t => t.bookings),
                    backgroundColor: GREEN,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    },

    difficulty(canvas, stats) {
        const d = stats.difficulty;
        return new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: Object.keys(d),
                datasets: [{ data: Object.values(d), backgroundColor: PALETTE }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    },

    monthlyTrend(canvas, stats) {
        return new Chart(canvas, {
            type: "line",
            data: {
                labels: stats.monthly_trend.labels,
                datasets: [{
                    label: "Bookings",
                    data: stats.monthly_trend.counts,
                    borderColor: GREEN, backgroundColor: "rgba(47,107,79,.15)",
                    fill: true, tension: 0.3,
                }],
            },
            options: {
                responsive: true, maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { y: { beginAtZero: true, ticks: { precision: 0 } } },
            },
        });
    },

    statusBreakdown(canvas, stats) {
        const s = stats.status_breakdown;
        return new Chart(canvas, {
            type: "doughnut",
            data: {
                labels: Object.keys(s),
                datasets: [{ data: Object.values(s), backgroundColor: PALETTE }],
            },
            options: { responsive: true, maintainAspectRatio: false },
        });
    },
};
