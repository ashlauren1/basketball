document.addEventListener("DOMContentLoaded", function () {
	setupTableInteractions("home-boxscore");
	setupTableInteractions("away-boxscore");

	function setupTableInteractions(tableId) {
		const table = document.getElementById(tableId);
		const rows = Array.from(table.querySelectorAll("tbody tr"));
		
		addSortToHeaders(table);

		function addSortToHeaders(table) {
			const headers = table.querySelectorAll("thead th");
			headers.forEach((header, index) => {
				header.style.cursor = "pointer";
				header.addEventListener("click", () => sortTable(table, index));
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
			rows.forEach(row => table.querySelector("tbody").appendChild(row));
		}
	}
});


