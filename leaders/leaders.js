document.addEventListener("DOMContentLoaded", function () {
	const seasonTable = document.getElementById("seasonLeaders");
	const headerRow = seasonTable.querySelector("thead tr:first-child");
    const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
    const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
    const clearAllButton = document.getElementById("clear-all-btn");
    const clearButton = document.getElementById("clear-filters-btn");
    let showSelectedOnly = false;
    let isDragging = false;
	
    rows.forEach(row => {
        row.addEventListener("mousedown", function () {
            isDragging = true;
            toggleRowSelection(row);
        });

        row.addEventListener("mouseenter", function () {
            if (isDragging) toggleRowSelection(row);
        });

        row.addEventListener("mouseup", () => isDragging = false);
    });

    document.addEventListener("mouseup", () => isDragging = false);

    function toggleRowSelection(row) {
        row.classList.toggle("selected-row");
    }

    toggleSelectionBtn.addEventListener("click", () => {
        showSelectedOnly = !showSelectedOnly;
        if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
    });
	
	addSortToHeaders(seasonTable);
	
	function addSortToHeaders(seasonTable) {
		const headers = seasonTable.querySelectorAll("thead th");
		headers.forEach((header, index) => {
			header.style.cursor = "pointer";
			header.addEventListener("click", function () {
				sortTable(seasonTable, index);
			});
		});
	}
	
	function sortTable(seasonTable, columnIndex) {
		const rows = Array.from(seasonTable.querySelectorAll("tbody tr"));
		
		// TESTING DEFAULT DESC SORT DIRECTION
		let asc = false;
		const direction = seasonTable.dataset.sortDirection === "desc" ? "asc" : "desc";
		
		seasonTable.dataset.sortDirection = direction;

		rows.sort((a, b) => {
			let cellA = a.cells[columnIndex].textContent.trim();
			let cellB = b.cells[columnIndex].textContent.trim();

			let valA, valB;
			
			const isPercentage = cellA.includes('%') && cellB.includes('%');
			if (isPercentage) {
				valA = parseFloat(cellA.replace('%', ''));
				valB = parseFloat(cellB.replace('%', ''));
			} else if (!isNaN(cellA) && !isNaN(cellB)) {
				valA = parseFloat(cellA);
				valB = parseFloat(cellB);
			} else {
				valA = cellA.toLowerCase();
				valB = cellB.toLowerCase();
			}

			if (valA < valB) {
				return direction === "asc" ? -1 : 1;
			} else if (valA > valB) {
				return direction === "asc" ? 1 : -1;
			} else {
				return 0;
			}
		});

		const tbody = seasonTable.querySelector("tbody");
		rows.forEach(row => tbody.appendChild(row));
	}
	
	const teamSelect = document.getElementById("teams");
    const positionSelect = document.getElementById("pos");
    const positionGroups = {
        f: ["lw", "rw", "w", "c", "f"],
        w: ["lw", "rw", "w"],
        c: ["c"],
        lw: ["lw"],
        rw: ["rw"],
        d: ["d"],
    };
    
    teamSelect.addEventListener("change", filterTable);
    positionSelect.addEventListener("change", filterTable);

    function filterTable() {
        const teamFilter = teamSelect.value.trim().toLowerCase();
        const positionFilter = positionSelect.value.trim().toLowerCase();
        const positionGroup = positionGroups[positionFilter] || []; 
        
        rows.forEach(row => {
            const cells = row.cells;
            const teamCell = cells[2]?.textContent.trim().toLowerCase(); // Assuming team is in column 2
            const positionCell = cells[3]?.textContent.trim().toLowerCase();
            
            const matchesTeam = !teamFilter || teamCell === teamFilter;
            const matchesPosition =
                !positionFilter || positionGroup.includes(positionCell);
			const isFiltered = (!positionSelect.value === "") || (!teamSelect.value === "");
			
			!showSelectedOnly ? (row.style.display = matchesTeam && matchesPosition ? "" : "none") : (row.style.display = row.classList.contains("selected-row") && matchesTeam && matchesPosition ? "" : "none")
        });
    }
	
	clearButton.addEventListener("click", () => {
		document.querySelectorAll("select").forEach(select => select.value = "");
		filterTable();
		if (showSelectedOnly) {
            rows.forEach(row => {
                row.style.display = row.classList.contains("selected-row") ? "" : "none";
            });
            toggleSelectionBtn.textContent = "Show All Rows";
        } else {
            rows.forEach(row => (row.style.display = ""));
            toggleSelectionBtn.textContent = "Show Selected Only";
        }
	});

    clearAllButton.addEventListener("click", () => {
        document.querySelectorAll("select").forEach(select => select.value = "");

        rows.forEach(row => {
            row.classList.remove("selected-row");
            row.style.display = "";
        });
        toggleSelectionBtn.textContent = "Show Selected Only";
        showSelectedOnly = false;
        
        filterTable();
    });
});