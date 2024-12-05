document.addEventListener("DOMContentLoaded", function () {
	const table = document.getElementById("team-table");
	const headerRow = table.querySelector("thead tr:first-child");
	const filterRow = document.querySelector("#filter-row");
	const rows = Array.from(table.querySelectorAll("tbody tr"));
	const toggleSelectionBtn = document.getElementById("toggle-selection-btn");
	const clearAllButton = document.getElementById("clear-all-btn");
	const clearButton = document.getElementById("clear-filters-btn");
	let showSelectedOnly = false;
	let isDragging = false;

	// Add filters and sorting
	addFilters(table);
	addSortToHeaders(table);

	clearButton.addEventListener("click", () => {
		document.querySelectorAll(".filter-select").forEach(select => select.value = "");
		filterTable();
	});

	clearAllButton.addEventListener("click", () => {
		rows.forEach(row => {
			row.classList.remove("selected-row");
			row.style.display = "";
		});
		document.querySelectorAll(".filter-select").forEach(select => select.value = "");
		toggleSelectionBtn.textContent = "Show Selected Only";
		showSelectedOnly = false;
		filterTable();
	});

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
			toggleSelectionBtn.textContent = "Show All";
		} else {
			rows.forEach(row => (row.style.display = ""));
			toggleSelectionBtn.textContent = "Show Selected Only";
		}
	});

	function addFilters(table) {
		const headerRow = table.querySelector("thead tr:first-child");
		const filterRow = document.querySelector("#filter-row");

		Array.from(headerRow.cells).forEach((header, index) => {
			const filterCell = document.createElement("td");
			const filterSelect = document.createElement("select");
			filterSelect.classList.add("filter-select");

			filterSelect.innerHTML = '<option value="">All</option>';
			const values = Array.from(new Set(
				Array.from(table.querySelectorAll("tbody tr td:nth-child(" + (index + 1) + ")"))
				.map(cell => cell.textContent.trim())
			)).sort();

			values.forEach(value => {
				const option = document.createElement("option");
				option.value = value;
				option.textContent = value;
				filterSelect.appendChild(option);
			});

			filterSelect.addEventListener("change", filterTable);
			filterCell.appendChild(filterSelect);
			filterRow.appendChild(filterCell);
		});
	}

	function filterTable() {
		const filters = Array.from(document.querySelectorAll(".filter-select")).map(select => select.value);
		rows.forEach(row => {
			const cells = Array.from(row.cells);
			const matchesFilter = filters.every((filter, i) => !filter || cells[i].textContent.trim() === filter);
			row.style.display = matchesFilter ? "" : "none";
		});
	}

	function addSortToHeaders(table) {
		const headers = table.querySelectorAll("thead th");
		headers.forEach((header, index) => {
			header.style.cursor = "pointer";
			header.addEventListener("click", function () {
				sortTable(table, index);
			});
		});
	}

	function sortTable(table, columnIndex) {
		const rows = Array.from(table.querySelectorAll("tbody tr"));
		const direction = table.dataset.sortDirection === "asc" ? "desc" : "asc";
		table.dataset.sortDirection = direction;
		
		// Detect data type
		let isNumeric = true;
		let isDate = true;
		for (let row of rows) {
			const cellText = row.cells[columnIndex].textContent.trim();
			if (cellText === '') continue; // Skip empty cells
			if (isNumeric && isNaN(cellText)) {
				isNumeric = false;
			}
			if (isDate && isNaN(Date.parse(cellText))) {
				isDate = false;
			}
			if (!isNumeric && !isDate) break;
		}

		rows.sort((a, b) => {
			const cellA = a.cells[columnIndex].textContent.trim();
			const cellB = b.cells[columnIndex].textContent.trim();

			let valA, valB;

			if (isNumeric) {
				valA = parseFloat(cellA);
				valB = parseFloat(cellB);
			} else if (isDate) {
				valA = new Date(cellA);
				valB = new Date(cellB);
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

	const tbody = table.querySelector("tbody");
	rows.forEach(row => tbody.appendChild(row));
}});
document.addEventListener("DOMContentLoaded", async function () {
	const searchBar = document.getElementById("search-bar");
	const searchResults = document.getElementById("search-results");
	const searchButton = document.getElementById("search-button");

	let playerLinks = {};
	let teamLinks = {};

	// Load players and teams data from JSON files
	async function loadLinks() {
		playerLinks = await fetch('players.json').then(response => response.json());
		teamLinks = await fetch('teams.json').then(response => response.json());
	}

	await loadLinks();  // Ensure links are loaded before searching

	// Filter data and show suggestions based on input
	function updateSuggestions() {
		const query = searchBar.value.trim().toLowerCase();
		searchResults.innerHTML = ""; // Clear previous results

		if (query === "") return;

		// Combine players and teams for search
		const combinedLinks = { ...playerLinks, ...teamLinks };
		const matchingEntries = Object.entries(combinedLinks)
			.filter(([name]) => name.toLowerCase().includes(query))  // Matches on both name and ID
			.slice(0, 10); // Limit to top 10


		matchingEntries.forEach(([name, url]) => {
			const resultItem = document.createElement("div");
			resultItem.classList.add("suggestion");

			// Proper case for names
			resultItem.textContent = name;

			resultItem.addEventListener("click", () => {
				window.open(url, "_self");
			});
			searchResults.appendChild(resultItem);
		});

		if (matchingEntries.length > 0) {
			searchResults.style.display = "block"; // Show results if matches are found
		} else {
			const noResultItem = document.createElement("div");
			noResultItem.classList.add("no-result");
			noResultItem.textContent = "No results found.";
			searchResults.appendChild(noResultItem);
			searchResults.style.display = "block";
		}
	}

	document.addEventListener("click", function(event) {
		if (!searchResults.contains(event.target) && event.target !== searchBar) {
			searchResults.style.display = "none";
		}
	});

	// Add event listener to search bar
	searchBar.addEventListener("input", updateSuggestions);

	function redirectToSearchResults() {
		const query = searchBar.value.trim().toLowerCase();;
		if (query) {
			window.location.href = `/hockey/search_results.html?query=${encodeURIComponent(query)}`;
		}
	}

	// Add event listeners for search
	searchBar.addEventListener("keypress", function (e) {
		if (e.key === "Enter") {
			redirectToSearchResults();
		}
	});

	searchButton.addEventListener("click", redirectToSearchResults);
});

document.addEventListener("DOMContentLoaded", function () {
	const headers = document.querySelectorAll("thead th[data-tip]");

	headers.forEach(header => {
		const tooltip = document.createElement("span");
		tooltip.className = "tooltip inactive"; // Add both classes initially
		tooltip.textContent = header.getAttribute("data-tip");
		document.body.appendChild(tooltip);

		// Show tooltip on mouseover
		header.addEventListener("mouseover", () => {
			tooltip.classList.add("active");
			tooltip.classList.remove("inactive");

			const rect = header.getBoundingClientRect();
			tooltip.style.left = rect.left + "px"; // Align with header
			tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight + 6) + "px"; // Above header, add a small gap
		});

		// Hide tooltip on mouseout
		header.addEventListener("mouseout", () => {
			tooltip.classList.remove("active");
			tooltip.classList.add("inactive");
		});
	});
});
