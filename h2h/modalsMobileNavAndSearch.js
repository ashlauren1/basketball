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

document.addEventListener("DOMContentLoaded", function () {
    var glossaryModal = document.getElementById("glossaryModal");
    var glossaryModalButton = document.getElementById("glossaryButton");
    var glossaryModalContent = document.getElementById("glossary-modal-content");
    var closeGlossaryModal = document.getElementsByClassName("closeGlossary")[0];

    glossaryModalButton.onclick = function() {
        glossaryModal.classList.add("open");
        glossaryModal.style.display = "block";
    }

    closeGlossaryModal.onclick = function() {
        glossaryModal.classList.remove("open");
        glossaryModal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target === glossaryModal) {
            glossaryModal.style.display = "none";
        }
    }
})
        
document.addEventListener("DOMContentLoaded", function () {
    const glossaryButton = document.getElementById("glossaryButton");

    function setupModal(modalId, buttonId, closeClass) {
        const modal = document.getElementById(modalId);
        const button = document.getElementById(buttonId);
        const closeButton = modal.querySelector(`.${closeClass}`);

        // Toggle modal visibility when button is clicked
        button.onclick = function () {
            const isOpen = modal.classList.contains("open");
				modal.style.display = isOpen ? "none" : "block";
				modal.classList.toggle("open", !isOpen);
        };

        // Close modal when the close button is clicked
        closeButton.onclick = function () {
            modal.style.display = "none";
            modal.classList.remove("open");
        };

        // Close modal when clicking outside the modal content
        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        };
    }

    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
});

function myFunction() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "block") {
        x.style.display = "none";
    } else {
        x.style.display = "block";
    }
};