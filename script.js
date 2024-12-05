let sortDirection = {};
const gradientColumns = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]; // Define gradient columns

// Function to detect if a column is numeric
function isNumericColumn(columnIndex, rows) {
    for (let row of rows) {
        let cellValue = row.cells[columnIndex].innerText.trim();
        if (cellValue && isNaN(cellValue)) {
            return false;  // If any cell is not a number, it's a text column
        }
    }
    return true;  // If all cells are numbers, it's a numeric column
}

// General sort function for any table and column
function sortTable(tableId, columnIndex) {
    let table = document.getElementById(tableId);
    let rows = Array.from(table.rows).slice(1);  // Skip the header row
    let dir = sortDirection[tableId + columnIndex] === "asc" ? "desc" : "asc";  // Track sorting direction

    // Determine if the column is numeric
    let isNumeric = isNumericColumn(columnIndex, rows);

    rows.sort((a, b) => {
        let x = a.cells[columnIndex].innerText.trim();
        let y = b.cells[columnIndex].innerText.trim();

        if (isNumeric) {
            x = parseFloat(x);
            y = parseFloat(y);
        } else {
            x = x.toLowerCase();
            y = y.toLowerCase();
        }

        return dir === "asc" ? (x > y ? 1 : -1) : (x < y ? 1 : -1);
    });

    rows.forEach(row => table.tBodies[0].appendChild(row));
    sortDirection[tableId + columnIndex] = dir;

    // Apply gradient colors to specified columns after sorting
    applyGradientColors(table, gradientColumns);
}

// Function to apply gradient colors
function applyGradientColors(table, columns) {
    columns.forEach(columnIndex => {
        const values = Array.from(table.querySelectorAll(`tbody tr`))
                            .map(row => parseFloat(row.cells[columnIndex].innerText.trim()) || 0);
        const min = Math.min(...values);
        const max = Math.max(...values);

        table.querySelectorAll(`tbody tr`).forEach(row => {
            const cell = row.cells[columnIndex];
            const value = parseFloat(cell.innerText.trim()) || 0;

            // Calculate percentage within the range for the color gradient
            const percentage = (value - min) / (max - min);
            cell.style.backgroundColor = getGradientColor(percentage);
            cell.classList.remove("no-gradient"); // Ensure gradient cells don’t have the hover effect
        });
    });

    // Mark cells in non-gradient columns as `.no-gradient` for hover effect
    table.querySelectorAll("tbody tr").forEach(row => {
        row.querySelectorAll("td").forEach((cell, columnIndex) => {
            if (!columns.includes(columnIndex)) {
                cell.classList.add("no-gradient");
            }
        });
    });
}

// Function to calculate HSL gradient color from dark red to dark green via white
function getGradientColor(percentage) {
    if (percentage < 0.5) {
        // Transition from red to white
        const redHue = 0, redSaturation = 100, redLightness = 45;
        const whiteHue = 0, whiteSaturation = 0, whiteLightness = 100;
        
        const hue = redHue + (whiteHue - redHue) * (percentage * 2);
        const saturation = redSaturation + (whiteSaturation - redSaturation) * (percentage * 2);
        const lightness = redLightness + (whiteLightness - redLightness) * (percentage * 2);

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    } else {
        // Transition from white to green
        const greenHue = 145, greenSaturation = 90, greenLightness = 45;
        const whiteHue = 0, whiteSaturation = 0, whiteLightness = 100;
        
        const hue = whiteHue + (greenHue - whiteHue) * ((percentage - 0.5) * 2);
        const saturation = whiteSaturation + (greenSaturation - whiteSaturation) * ((percentage - 0.5) * 2);
        const lightness = whiteLightness + (greenLightness - whiteLightness) * ((percentage - 0.5) * 2);

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }
}

document.addEventListener("DOMContentLoaded", function () {
    // Filter dropdowns
    const gameFilter = document.getElementById("game-filter");
    const playerFilter = document.getElementById("player-filter");
    const teamFilter = document.getElementById("team-filter");
    const typeFilter = document.getElementById("type-filter");
    const statFilter = document.getElementById("stat-filter");

    // Populate dropdowns with unique values from the table
    populateDropdowns();

    // Event listeners for dropdown filters
    [gameFilter, playerFilter, teamFilter, typeFilter, statFilter].forEach(dropdown => {
        dropdown.addEventListener("change", filterTable);
    });

    // Apply gradient colors on page load
    const table = document.getElementById("data-table");
    applyGradientColors(table, gradientColumns);

    // Function to populate dropdowns with unique values
    function populateDropdowns() {
        const rows = document.querySelectorAll("#data-table tbody tr");

        const games = new Set();
        const players = new Set();
        const teams = new Set();
        const types = new Set();

        rows.forEach(row => {
            games.add(row.cells[0].innerText);
            players.add(row.cells[2].innerText);
            teams.add(row.cells[3].innerText);
            types.add(row.cells[8].innerText);
        });

        populateDropdown(gameFilter, games);
        populateDropdown(playerFilter, players);
        populateDropdown(teamFilter, teams);
        populateDropdown(typeFilter, types);
    }

    // Helper function to populate a dropdown
    function populateDropdown(dropdown, values) {
        dropdown.innerHTML = '<option value="">All</option>'; // Default option
        values.forEach(value => {
            const option = document.createElement("option");
            option.value = value;
            option.textContent = value;
            dropdown.appendChild(option);
        });
    }

    // Function to filter the table based on selected dropdown values
    function filterTable() {
        const gameValue = gameFilter.value;
        const playerValue = playerFilter.value;
        const teamValue = teamFilter.value;
        const typeValue = typeFilter.value;
        const statValues = Array.from(statFilter.selectedOptions).map(option => option.value);

        const rows = document.querySelectorAll("#data-table tbody tr");

        rows.forEach(row => {
            const gameText = row.cells[0].innerText;
            const playerText = row.cells[2].innerText;
            const teamText = row.cells[3].innerText;
            const typeText = row.cells[8].innerText;
            const statText = row.cells[7].innerText;

            const gameMatch = !gameValue || gameText === gameValue;
            const playerMatch = !playerValue || playerText === playerValue;
            const teamMatch = !teamValue || teamText === teamValue;
            const typeMatch = !typeValue || typeText === typeValue;
            const statMatch = !statValues.length || statValues.includes(statText);

            // Show row only if it matches all selected filters
            row.style.display = gameMatch && playerMatch && teamMatch && typeMatch && statMatch ? "" : "none";
        });
    }
});

// Reset filters function
function resetFilters() {
    document.getElementById("game-filter").value = "";
    document.getElementById("player-filter").value = "";
    document.getElementById("team-filter").value = "";
    document.getElementById("type-filter").value = "";
    document.getElementById("stat-filter").value = "";

    // Trigger filtering to reset the table
    filterTable();
}

// Function to apply gradient colors
function applyGradientColors(table, columns) {
    columns.forEach(columnIndex => {
        const values = Array.from(table.querySelectorAll(`tbody tr`))
                            .map(row => parseFloat(row.cells[columnIndex].innerText.trim()) || 0);
        const min = Math.min(...values);
        const max = Math.max(...values);

        table.querySelectorAll(`tbody tr`).forEach(row => {
            const cell = row.cells[columnIndex];
            const value = parseFloat(cell.innerText.trim()) || 0;

            // Calculate percentage within the range for the color gradient
            const percentage = (value - min) / (max - min);
            cell.style.backgroundColor = getGradientColor(percentage);
            cell.classList.remove("no-gradient"); // Ensure gradient cells don’t have the hover effect
        });
    });

    // Mark cells in non-gradient columns as `.no-gradient` for hover effect
    table.querySelectorAll("tbody tr").forEach(row => {
        row.querySelectorAll("td").forEach((cell, columnIndex) => {
            if (!columns.includes(columnIndex)) {
                cell.classList.add("no-gradient");
            }
        });
    });
}

// Function to calculate HSL gradient color from dark red to dark green via white
function getGradientColor(percentage) {
    if (percentage < 0.5) {
        // Transition from red to white
        const redHue = 0, redSaturation = 100, redLightness = 45;
        const whiteHue = 0, whiteSaturation = 0, whiteLightness = 100;
        
        const hue = redHue + (whiteHue - redHue) * (percentage * 2);
        const saturation = redSaturation + (whiteSaturation - redSaturation) * (percentage * 2);
        const lightness = redLightness + (whiteLightness - redLightness) * (percentage * 2);

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    } else {
        // Transition from white to green
        const greenHue = 145, greenSaturation = 90, greenLightness = 45;
        const whiteHue = 0, whiteSaturation = 0, whiteLightness = 100;
        
        const hue = whiteHue + (greenHue - whiteHue) * ((percentage - 0.5) * 2);
        const saturation = whiteSaturation + (greenSaturation - whiteSaturation) * ((percentage - 0.5) * 2);
        const lightness = whiteLightness + (greenLightness - whiteLightness) * ((percentage - 0.5) * 2);

        return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
    }
}
