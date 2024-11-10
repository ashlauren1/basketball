// Format x-axis labels with opponent and date on separate lines
function formatLabel(data) {
    const opponentText = data.location === 'home' ? 'vs' : '@';
    const date = new Date(data.date);
    const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(date.getFullYear()).slice(-2)}`;
    
    // Return an array to create multiline label
    return [`${opponentText} ${data.opponent}`, formattedDate];
}

// Function to create consistent chart options
function getChartOptions(line, stat) {
    return {
        plugins: {
            legend: { 
				display: false 
			},
            title: { 
				display: true, 
				text: stat, 
				font: { 
					size: 14,
					family: 'Verdana'
				},
				color: '#333333',
				padding: 4
			},
            annotation: {
                annotations: {
                    line1: {
                        type: 'line',
                        yMin: line,
                        yMax: line,
                        borderColor: '#333333',
                        borderWidth: 1.5
                    }
                }
            }
        },
        scales: {
            y: { 
                grid: { 
                    display: true,
					color: '#dfe1e2'
                },
				ticks: {
					font: {
						size: 10,
						family: 'Verdana'
					},
					color: '#333333',
					padding: 0 
				},
				beginAtZero: true, 
                stepSize: 1.0 
            },
            x: { 
                grid: { 
                    display: false 
                },
                ticks: {
                    autoSkip: true,
                    maxRotation: 0,
                    minRotation: 0,
					font: {
						size: 9,
						family: 'Verdana'
					},
					color: '#333333',
					padding: 0 
                }
            }
        }
    };
}

// Initialize chart, storing unfiltered data globally and setting chart options
function initializeChart(stat, gameId, bettingLineId, chartData, bettingLine) {
    const chartId = `${stat}_${gameId}_${bettingLineId}_chart`;
    const lineSliderId = `${stat}_${gameId}_${bettingLineId}_lineSlider`;
    const lineValueId = `${stat}_${gameId}_${bettingLineId}_lineValue`;

    // Store the original data in window scope for filtering
	window[`allData_${stat}_${gameId}_${bettingLineId}`] = chartData;
    window[`originalLine_${stat}_${gameId}_${bettingLineId}`] = bettingLine; // Store initial betting line
    window[`Line_${stat}_${gameId}_${bettingLineId}`] = bettingLine; // Track current line

    const ctx = document.getElementById(chartId).getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.map(d => formatLabel(d)),  // Use multiline label format
            datasets: [{
                label: stat,
                data: chartData.map(d => d.stat || 0.02),
                backgroundColor: chartData.map(d => d.stat === 0 ? '#c01616' : (d.stat >= bettingLine ? '#16c049' : '#c01616')),
                borderColor: chartData.map(d => d.stat === 0 ? '#421f1f' : (d.stat >= bettingLine ? '#304f3a' : '#421f1f')),
                borderWidth: 0.5,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: getChartOptions(bettingLine, stat)
    });

    window[`chart_${stat}_${gameId}_${bettingLineId}`] = chart;

    // Attach line update event to slider
    document.getElementById(lineSliderId).addEventListener('input', function (event) {
        updateLine(stat, gameId, bettingLineId, parseFloat(event.target.value));
    });
}

// Update line and adjust colors based on new line value
function updateLine(stat, gameId, bettingLineId, newLine) {
    const chart = window[`chart_${stat}_${gameId}_${bettingLineId}`];
    const data = chart.data.datasets[0].data;
    const lineValueId = `${stat}_${gameId}_${bettingLineId}_lineValue`;

    window[`Line_${stat}_${gameId}_${bettingLineId}`] = newLine;
    document.getElementById(lineValueId).innerText = newLine;

    chart.options.plugins.annotation.annotations.line1.yMin = newLine;
    chart.options.plugins.annotation.annotations.line1.yMax = newLine;
    chart.data.datasets[0].backgroundColor = data.map(value => (value >= newLine ? '#16c049' : '#c01616'));
    chart.update();
}

// Apply filters and update chart with filtered data
function applyFilters(stat, gameId, bettingLineId) {
    const chart = window[`chart_${stat}_${gameId}_${bettingLineId}`];
    const originalData = window[`allData_${stat}_${gameId}_${bettingLineId}`];
    const teamFilter = document.getElementById(`${stat}_${gameId}_${bettingLineId}_teamFilter`).value;
    const homeAwayFilter = document.getElementById(`${stat}_${gameId}_${bettingLineId}_homeAwayFilter`).value;
    const startDate = document.getElementById(`${stat}_${gameId}_${bettingLineId}_startDate`).value;
    const endDate = document.getElementById(`${stat}_${gameId}_${bettingLineId}_endDate`).value;
    const line = window[`Line_${stat}_${gameId}_${bettingLineId}`];

    // Filter data based on selected criteria
    const filteredData = originalData.filter(d => {
        const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
        const isLocationMatch = (homeAwayFilter === 'all') || 
                                (homeAwayFilter === 'home' && d.location === 'home') || 
                                (homeAwayFilter === 'away' && d.location === 'away');
        const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                              (!endDate || new Date(d.date) <= new Date(endDate));
        return isTeamMatch && isLocationMatch && isDateInRange;
    });

    // Update chart data and colors with filtered data
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d.stat || 0.02);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d.stat >= line ? '#16c049' : '#c01616'));
    chart.update();
}

// Clear filters and reset chart to original data
function clearFilters(stat, gameId, bettingLineId) {
    document.getElementById(`${stat}_${gameId}_${bettingLineId}_teamFilter`).value = "all";
    document.getElementById(`${stat}_${gameId}_${bettingLineId}_homeAwayFilter`).value = "all";
    document.getElementById(`${stat}_${gameId}_${bettingLineId}_startDate`).value = "";
    document.getElementById(`${stat}_${gameId}_${bettingLineId}_endDate`).value = "";

    const line = window[`Line_${stat}_${gameId}_${bettingLineId}`];
    applyFilters(stat, gameId, bettingLineId); // Reset filtered data to original
    updateLine(stat, gameId, bettingLineId, line); // Reset betting line to default
}

// Reset the line to the original betting line
function resetLine(stat, gameId, bettingLineId) {
    const originalLine = window[`originalLine_${stat}_${gameId}_${bettingLineId}`];  // Retrieve stored initial line
    const lineSlider = document.getElementById(`${stat}_${gameId}_${bettingLineId}_lineSlider`);
    const lineValue = document.getElementById(`${stat}_${gameId}_${bettingLineId}_lineValue`);

    // Reset slider and displayed line value to the original line
    lineSlider.value = originalLine;
    lineValue.innerText = originalLine;

    // Reset the current line and update the chart
    updateLine(stat, gameId, bettingLineId, originalLine);
}

function filterGames(stat, gameId, bettingLineId, numGames) {
    const chart = window[`chart_${stat}_${gameId}_${bettingLineId}`];
    const originalData = window[`allData_${stat}_${gameId}_${bettingLineId}`];

    const filteredData = originalData.slice(-numGames);
    const line = window[`Line_${stat}_${gameId}_${bettingLineId}`];

    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d.stat || 0.02);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d.stat >= line ? '#16c049' : '#c01616'));
    chart.update();
}

function filterBySeason(stat, gameId, bettingLineId, season) {
    const chart = window[`chart_${stat}_${gameId}_${bettingLineId}`];
    const originalData = window[`allData_${stat}_${gameId}_${bettingLineId}`];

    const filteredData = originalData.filter(d => d.season === season);
    const line = window[`Line_${stat}_${gameId}_${bettingLineId}`];

    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d.stat || 0.02);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d.stat >= line ? '#16c049' : '#c01616'));
    chart.update();
}
