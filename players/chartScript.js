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
                categoryPercentage: 1.0,
				yAxisID: 'y',
				stack: 'combined'
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
					family: 'Montserrat'
				},
				color: '#000',
				padding: 4
            },
            annotation: {
                annotations: {
                    line1: {
                        type: 'line',
                        yMin: line,
                        yMax: line,
                        borderColor: '#333',
                        borderWidth: 1.5
                    }
                }
            }
        },
        scales: {
            y: { 
				grid: { 
                    display: true,
					color: '#ededed'
                },
				ticks: {
					font: {
						size: 10,
						family: 'Inter'
					},
					color: '#000',
					padding: 6 
				},
				beginAtZero: true, 
                stepSize: 1.0 
            },
            y1: { 
				display: false,
                position: 'right',
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Mins'
                },
                grid: {
                    drawOnChartArea: false // Avoids overlapping grid lines
                }
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
						size: 8,
						family: 'Inter'
					},
					color: '#000',
					padding: 0 
                }
            }
        }
    };
}

function getBackgroundColors(data, stat, line, playerId) {
    return data.map(d => (d[stat] === 0 ? '#c01616' : (d[stat] >= line ? '#16c049' : '#c01616')));
}

function getBorderColors(data, stat, line, playerId) {
    return data.map(d => (d[stat] === 0 ? '#421f1f' : (d[stat] >= line ? '#304f3a' : '#421f1f')));
}

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

function updateLine(playerId, newLine) {
    const chart = window[`chart_${playerId}`];
    const data = chart.data.datasets[0].data;

    window[`Line_${playerId}`] = parseFloat(newLine);

    document.getElementById(`lineValue_${playerId}`).innerText = newLine;

    chart.options.plugins.annotation.annotations.line1.yMin = newLine;
    chart.options.plugins.annotation.annotations.line1.yMax = newLine;
    chart.data.datasets[0].backgroundColor = data.map(value => (value >= newLine ? '#16c049' : '#c01616'));
    chart.update();
}

function applyFilters(playerId) {
    const originalData = window[`allData_${playerId}`]; // Use the original data as the base
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    const teamFilter = document.getElementById(`teamFilter_${playerId}`).value;
    const homeAwayFilter = document.getElementById(`homeAwayFilter_${playerId}`).value;
    const startDate = document.getElementById(`startDate_${playerId}`).value;
    const endDate = document.getElementById(`endDate_${playerId}`).value;

    const recentGamesFilter = window[`recentGames_${playerId}`] || null;
    const seasonFilter = window[`seasonFilter_${playerId}`] || null;

    let filteredData = originalData.filter(d => {
        const isTeamMatch = (teamFilter === 'all') || (d.opponent === teamFilter);
        const isLocationMatch = (homeAwayFilter === 'all') || 
                                (homeAwayFilter === 'home' && d.location === 'home') || 
                                (homeAwayFilter === 'away' && d.location === 'away');
        const isDateInRange = (!startDate || new Date(d.date) >= new Date(startDate)) &&
                              (!endDate || new Date(d.date) <= new Date(endDate));
        return isTeamMatch && isLocationMatch && isDateInRange;
    });

    if (recentGamesFilter) {
        filteredData = filteredData.slice(-recentGamesFilter);
    } else if (seasonFilter) {
        filteredData = filteredData.filter(d => d.season === seasonFilter);
    }
	
    const chart = window[`chart_${playerId}`];
    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = filteredData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

function showRecentGames(playerId, numGames) {
    window[`recentGames_${playerId}`] = numGames;
	window[`seasonFilter_${playerId}`] = null;
    applyFilters(playerId);
}

function filterBySeason(playerId, season) {
    window[`seasonFilter_${playerId}`] = season;
	window[`recentGames_${playerId}`] = null;
    applyFilters(playerId);
}

function showAllGames(playerId) {
    window[`recentGames_${playerId}`] = null;
    window[`seasonFilter_${playerId}`] = null;
    applyFilters(playerId);
}

function clearFilters(playerId) {
    document.getElementById(`teamFilter_${playerId}`).value = "all";
    document.getElementById(`homeAwayFilter_${playerId}`).value = "all";
    document.getElementById(`startDate_${playerId}`).value = "";
    document.getElementById(`endDate_${playerId}`).value = "";

    const originalData = window[`allData_${playerId}`];
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    const chart = window[`chart_${playerId}`];
    chart.data.labels = originalData.map(d => formatLabel(d));
    chart.data.datasets[0].data = originalData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = originalData.map(d => (d[stat] >= line ? '#16c049' : '#c01616'));
    chart.update();
}

function updateChart(playerId, filteredData, stat, line) {
    const chart = window[`chart_${playerId}`];
    if (!chart) return;

    chart.data.labels = filteredData.map(d => formatLabel(d));
    chart.data.datasets[0].data = filteredData.map(d => d[stat] || 0.0);
    chart.data.datasets[0].backgroundColor = getBackgroundColors(filteredData, stat, line, playerId);
    chart.update();
}

function applyFilter(playerId, filterType, filterValue = null) {
    const originalData = window[`allData_${playerId}`];
    const stat = window[`currentStat_${playerId}`];
    const line = window[`Line_${playerId}`];

    let filteredData = [...originalData];

    if (filterType === "recent" && filterValue) {
        filteredData = filteredData.slice(-filterValue);
    } else if (filterType === "season" && filterValue) {
        filteredData = filteredData.filter(d => d.season === filterValue);
    } else if (filterType === "all") {
        filteredData = originalData;
    }

    updateChart(playerId, filteredData, stat, line);
}

function resetLine(playerId, defaultLine) {
    updateLine(playerId, defaultLine);
    
    document.getElementById(`lineSlider_${playerId}`).value = defaultLine;
}

function toggleMPOverlay(playerId) {
    const chart = window[`chart_${playerId}`];
    const data = window[`allData_${playerId}`];

    const mpDatasetIndex = chart.data.datasets.findIndex(dataset => dataset.label === "MP Overlay");

    if (mpDatasetIndex === -1) {
        chart.data.datasets.push({
            label: "MP Overlay",
            data: data.map(d => d.MP || 0),
            type: 'bar',
            backgroundColor: "rgba(128, 128, 128, 0.1)",
            borderColor: "rgba(128, 128, 128, 0.4)",
            pointRadius: 0,
            fill: true, 
            yAxisID: 'y1',
            order: 0,
			borderWidth: 0.15,
            barPercentage: 1.0,
            categoryPercentage: 1.0,
			stack: 'combined'
        });
        chart.options.scales.y1.display = true;
        console.log("MP overlay added as a transparent line for player", playerId);
    } else {
        chart.data.datasets.splice(mpDatasetIndex, 1);
        chart.options.scales.y1.display = false;
        console.log("MP overlay removed for player", playerId);
    }

    chart.update();
}