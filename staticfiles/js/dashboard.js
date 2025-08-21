
    // Chart data
    document.addEventListener("DOMContentLoaded", function () {
     
        const chartDataElement = document.getElementById('chart-data');
        if (!chartDataElement) {
            console.error("Chart data not found in DOM.");
            return;
        }
    
        let chartData;
        try {
            chartData = JSON.parse(chartDataElement.textContent);
        } catch (e) {
            console.error("Failed to parse chart data:", e);
            return;
        }
    
        // User Growth Chart
        new Chart(document.getElementById('userGrowthChart'), {
            type: 'line',
            data: {
                labels: chartData.dates,
                datasets: [{
                    label: 'Total Users',
                    data: chartData.totalUsers,
                    borderColor: 'rgb(59, 130, 246)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });

        // Revenue Chart
        new Chart(document.getElementById('revenueChart'), {
            type: 'line',
            data: {
                labels: chartData.dates,
                datasets: [{
                    label: 'Total Revenue',
                    data: chartData.revenue,
                    borderColor: 'rgb(16, 185, 129)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function (value) {
                                return '₹ ' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });

    // Kundli Reports Chart
    new Chart(document.getElementById('kundliReportsChart'), {
        type: 'bar',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Total Kundli Reports',
                data: chartData.kundliReports,
                backgroundColor: 'rgb(139, 92, 246)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            }
        }
    });

    // Subscription Reports Chart
    new Chart(document.getElementById('subscriptionsChart'), {
        type: 'bar',
        data: {
            labels: chartData.dates,
            datasets: [{
                label: 'Total Subscriptions',
                data: chartData.totalSubscription,
                backgroundColor: 'rgb(139, 92, 246)'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                position: 'top'
                }
            }
        }
    });
});



