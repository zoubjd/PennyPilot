//const ProgressBar = require('progressbar.js');

function random_rgba(datalenght) {
    colors = [];
    for (let i = 0; i < datalenght; i++) {
        let o = Math.round, r = Math.random, s = 255;
        colors.push('rgba(' + o(r()*s) + ',' + o(r()*s) + ',' + o(r()*s) + ',' + r().toFixed(1) + ')');
    }
    return colors
}



    fetch('/expenses/daily')
        .then(response => response.json())
        .then(dailySpendData => {
            // Prepare data for the chart
            const labels = dailySpendData.map(entry => entry.day);
            const dataPoints = dailySpendData.map(entry => entry.total_spent);

            // Create the chart
            const ctx = document.getElementById('lineChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Daily Expenses',
                        data: dataPoints,
                        borderColor: 'rgba(40, 167, 69, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderWidth: 2,
                        fill: false,
                        tension: 0.1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching data:', error));



       /* fetch('/expenses/category')
        .then(response => response.json())
        .then(dailySpendData => {
            // Prepare data for the chart
            const labels = dailySpendData.map(entry => entry.category);
            const dataPoints = dailySpendData.map(entry => entry.total_spent);

            // Create the chart
            const ctx = document.getElementById('pieChart').getContext('2d');
            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Expenses by Category',
                        data: dataPoints,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: random_rgba(labels.length),
                        borderWidth: 2
                    }]
                },
            });
        })
        .catch(error => console.error('Error fetching data:', error));*/


        fetch('/goalsummary')
    .then(response => response.json())
    .then(goalsummary => {
        // Prepare data for the progress bar
        let statusElement = document.getElementById('statusss');


        // Set the status text
        statusElement.textContent = goalsummary.message;

        // Calculate percentage
        let goal = goalsummary.budget || 1; // Avoid division by 0
        let total = goalsummary.total_expenses || 0;
        let percentage = Math.min((total / goal) * 100, 100); // Cap at 100%

        if (percentage > 80) {
            statusElement.style.color = "Red";
            statusElement.textContent = "Gotta minimize spendings more";
        } else if (percentage > 50) {
            statusElement.style.color = "orange";
            statusElement.textContent = "Be carful you're halfway through";
        }

        // Initialize and animate the progress bar
        let bar = new ProgressBar.Line('#progressbar', {
            strokeWidth: 4,
            color: '#3498db',
            trailColor: '#eee',
            trailWidth: 2,
            easing: 'easeInOut',
            duration: 1400,
            text: {
                style: {
                    color: '#333',
                    position: 'absolute',
                    right: '0',
                    top: '-30px',
                    padding: '0',
                    margin: '0',
                    transform: null
                },
                autoStyleContainer: false
            },
            from: { color: '#3498db' },
            to: { color: '#2ecc71' },
            step: (state, bar) => {
                bar.setText(Math.round(bar.value() * 100) + '%');
            }
        });

        bar.animate(percentage / 100); // Value from 0.0 to 1.0
    })
    .catch(error => console.error('Error fetching data:', error));


    google.charts.load('current', { packages: ['sankey'] });
google.charts.setOnLoadCallback(drawChart);
function normalizeData(data) {
    return data.map(entry => ({
        ...entry,
        total_spent: Math.sqrt(entry.total_spent) // Use square root scaling
    }));
}

function drawChart() {
    fetch('/expenses/category')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched data:", data);
            // Store original and scaled values
            const scaledData = data.map(entry => ({
                ...entry,
                scaled_spent: Math.sqrt(entry.total_spent) // Scale value for visualization
            }));

            // Convert data into Sankey format using scaled values
            const sankeyData = [["From", "To", "Value", { role: "tooltip", type: "string" }]];
            scaledData.forEach(entry => {
                const tooltipValue = entry.total_spent ? `$${entry.total_spent.toFixed(2)}` : "No data";
                sankeyData.push([
                    entry.from,
                    entry.category,
                    entry.scaled_spent,
                    `${entry.category}: ${tooltipValue}`
                ]);
            });

            // Map colors for nodes
            const nodeColors = {};
            scaledData.forEach(entry => {
                nodeColors[entry.category] = entry.category === "Savings" ? '#4CAF50'  : '#F44336';
            });

            const chartData = google.visualization.arrayToDataTable(sankeyData);

            const options = {
                width: 600,
                height: 400,
                sankey: {
                    node: {
                        colors: Object.values(nodeColors),
                        label: {
                            fontSize: 14
                        }
                    },
                    link: {
                        colorMode: 'gradient'
                    }
                }
            };

            const chart = new google.visualization.Sankey(document.getElementById('sankey_chart'));
            chart.draw(chartData, options);
        })
        .catch(error => console.error('Error fetching Sankey data:', error));
}
