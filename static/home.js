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



        fetch('/expenses/category')
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
        .catch(error => console.error('Error fetching data:', error));


        fetch('/goalsummary')
    .then(response => response.json())
    .then(goalsummary => {
        // Prepare data for the progress bar
        let statusElement = document.getElementById('statusss');
        let status = goalsummary.status;

        // Set the status color
        if (status === "Over budget") {
            statusElement.style.color = "red";
        } else if (status === "Under budget") {
            statusElement.style.color = "green";
        }

        // Set the status text
        statusElement.textContent = goalsummary.message;

        // Calculate percentage
        let goal = goalsummary.budget || 1; // Avoid division by 0
        let total = goalsummary.total_expenses || 0;
        let percentage = Math.min((total / goal) * 100, 100); // Cap at 100%

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


    

