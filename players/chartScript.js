// Function to initialize a player's chart
function initializeChart(playerId, chartData, bettingLine, defaultStat) {
	const processedData = chartData.map(d => ({
        ...d,
        [defaultStat]: d[defaultStat] === 0 ? 0.02 : d[defaultStat]
    }));
	
    window[`allData_${playerId}`] = processedData;
    window[`currentStat_${playerId}`] = defaultStat;
    window[`Line_${playerId}`] = bettingLine;
    window[`chart_${playerId}`] = null;

    const ctx = document.getElementById(`chart_${playerId}`).getContext('2d');
    window[`chart_${playerId}`] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: processedData.map(d => formatLabel(d)),
            datasets: [{
                label: defaultStat,
                data: processedData.map(d => d[defaultStat] || 0.0),
                backgroundColor: getBackgroundColors(processedData, defaultStat, bettingLine, playerId),
                borderColor: getBorderColors(processedData, defaultStat, bettingLine, playerId),
                borderWidth: 0.15,
                barPercentage: 1.0,
                categoryPercentage: 1.0
            }]
        },
        options: getChartOptions(playerId, bettingLine, defaultStat)
    });
}

function formatLabel(data) {
    const opponentText = data.location === 'home' ? 'vs' : '@';
    const date = new Date(data.date);
    const formattedDate = `${date.getMonth() + 1}/${date.getDate()}/${String(date.getFullYear()).slice(-2)}`;
    
    // Return an array to create a multiline label
    return [`${opponentText} ${data.opponent}`, formattedDate];
}

// Chart options with multiline labels enabled
function getChartOptions(playerId, line, stat) {
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
					padding: 6 
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



// Get background colors for the chart bars based on stats
function getBackgroundColors(data, stat, line, playerId) {
    return data.map(d => (d[stat] === 0 ? '#c01616' : (d[stat] >= line ? '#16c049' : '#c01616')));
}

// Get border colors for the chart bars
function getBorderColors(data, stat, line, playerId) {
    return data.map(d => (d[stat] === 0 ? '#421f1f' : (d[stat] >= line ? '#304f3a' : '#421f1f')));
}


// Update the selected stat in the chart
function updateStat(playerId, selectedStat) {
    const chart = window[`chart_${playerId}`];
    const data = window[`allData_${playerId}`];
    const line = window[`Line_${playerId}`];

    window[`currentStat_${playerId}`] = selectedStat;
    chart.data.datasets[0].data = data.map(d => d[selectedStat] || 0.0);
    chart.data.datasets[0].label = selectedStat;
    chart.options.plugins.title.text = selectedStat;
    chart.data.datasets[0].backgroundColor = getBackgroundColors(data, selectedStat, line, playerId);
    chart.update();
}

// Update the betting line and adjust the chart annotation
function updateLine(playerId, newLine) {
    const chart = window[`chart_${playerId}`];
    const data = chart.data.datasets[0].data; // Use the current dataset without altering the original

    // Update the global line value
    window[`Line_${playerId}`] = parseFloat(newLine);

    // Update the displayed line value text
    document.getElementById(`lineValue_${playerId}`).innerText = newLine;

    // Update the annotation line on the chart
    chart.options.plugins.annotation.annotations.line1.yMin = newLine;
    chart.options.plugins.annotation.annotations.line1.yMax = newLine;

    // Update bar colors based on the new line value
    chart.data.datasets[0].backgroundColor = data.map(value => (value >= newLine ? '#16c049' : '#c01616'));
    chart.update();
}

// Apply filters (team, home/away, date range) to the chart
function applyFilters(playerId) {
    const originalData = window[`allData_${playerId}`]; // Always use the original data for filtering
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    const teamFilter = document.getElementById(`teamFilter_${playerId}`).value;
    const homeAwayFilter = document.getElementById(`homeAwayFilter_${playerId}`).value;
    const startDate = document.getElementById(`startDate_${playerId}`).value;
    const endDate = document.getElementById(`endDate_${playerId}`).value;

    // Filter the data based on the selected criteria without modifying the original
    const filteredData = originalData.filter(d => {
        const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
        const isLocationMatch = (homeAwayFilter === 'all') || 
                                (homeAwayFilter === 'home' && d.location === 'home') || 
                                (homeAwayFilter === 'away' && d.location === 'away');
        const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                              (!endDate || new Date(d.date) <= new Date(endDate));
        return isTeamMatch && isLocationMatch && isDateInRange;
    });

    // Update the chart with the filtered data and reset the colors
    const chart = window[`chart_${playerId}`];
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

// Reset the filters and the betting line
function clearFilters(playerId) {
    // Reset filter inputs to default values
    document.getElementById(`teamFilter_${playerId}`).value = "all";
    document.getElementById(`homeAwayFilter_${playerId}`).value = "all";
    document.getElementById(`startDate_${playerId}`).value = "";
    document.getElementById(`endDate_${playerId}`).value = "";

    // Use original unfiltered data to reset chart
    const originalData = window[`allData_${playerId}`];
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    const chart = window[`chart_${playerId}`];
    chart.data.labels = originalData.map(d => formatLabel(d));
    chart.data.datasets[0].data = originalData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = originalData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

// Update the chart display with new filtered data
function updateChart(playerId, filteredData, stat, line) {
    const chart = window[`chart_${playerId}`];
    if (!chart) return; // Exit if the chart does not exist

    // Update chart data and labels with filtered data
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = getBackgroundColors(filteredData, stat, line, playerId);

    // Refresh the chart to reflect changes
    chart.update();
}


function applyFilter(playerId, filterType, filterValue = null) {
    const originalData = window[`allData_${playerId}`];
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    let filteredData = [...originalData];

    if (filterType === "recent" && filterValue) {
        // Only slice if filterValue is provided
        filteredData = filteredData.slice(-filterValue);
    } else if (filterType === "season" && filterValue) {
        // Filter by season
        filteredData = filteredData.filter(d => d.season === filterValue);
    } else if (filterType === "all") {
        // No filtering; show all games
        filteredData = originalData;
    }

    // Call updateChart with filtered data
    updateChart(playerId, filteredData, stat, line);
}

// Button functions to filter data
function showRecentGames(playerId, numGames) {
    applyFilter(playerId, "recent", numGames);
}

function filterBySeason(playerId, season) {
    applyFilter(playerId, "season", season);
}

function showAllGames(playerId) {
    applyFilter(playerId, "all");
}

// Function to reset the betting line and move the slider to the default value
function resetLine(playerId, defaultLine) {
    updateLine(playerId, defaultLine); // Update displayed line value and chart annotation
    
    // Set the slider's position to the default value
    document.getElementById(`lineSlider_${playerId}`).value = defaultLine;
}
