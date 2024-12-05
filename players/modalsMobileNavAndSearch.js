document.addEventListener("DOMContentLoaded", async function () {
	const searchBar = document.getElementById("search-bar");
	const searchResults = document.getElementById("search-results");
	const searchButton = document.getElementById("search-button");

	let playerLinks = {};
	let teamLinks = {};

	async function loadLinks() {
		playerLinks = await fetch('players.json').then(response => response.json());
		teamLinks = await fetch('teams.json').then(response => response.json());
	}

	await loadLinks();

	function updateSuggestions() {
		const query = searchBar.value.trim().toLowerCase();
		searchResults.innerHTML = "";

		if (query === "") return;

		const combinedLinks = { ...playerLinks, ...teamLinks };
		const matchingEntries = Object.entries(combinedLinks)
			.filter(([name]) => name.toLowerCase().includes(query))
			.slice(0, 10);

		matchingEntries.forEach(([name, url]) => {
			const resultItem = document.createElement("div");
			resultItem.classList.add("suggestion");

			resultItem.textContent = name;

			resultItem.addEventListener("click", () => {
				window.open(url, "_self");
			});
			searchResults.appendChild(resultItem);
		});

		if (matchingEntries.length > 0) {
			searchResults.style.display = "block";
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

	searchBar.addEventListener("input", updateSuggestions);
	
	function redirectToSearchResults() {
	const query = searchBar.value.trim().toLowerCase();;
	if (query) {
		window.location.href = `/hockey/search_results.html?query=${encodeURIComponent(query)}`;
	}
}

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
        tooltip.className = "tooltip inactive";
        tooltip.textContent = header.getAttribute("data-tip");
        document.body.appendChild(tooltip);

        header.addEventListener("mouseover", () => {
            tooltip.classList.add("active");
            tooltip.classList.remove("inactive");

            const rect = header.getBoundingClientRect();
            tooltip.style.left = rect.left + "px"; 
            tooltip.style.top = (rect.top + window.scrollY - tooltip.offsetHeight + 6) + "px";
        });

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

        button.onclick = function () {
            const isOpen = modal.classList.contains("open");
				modal.style.display = isOpen ? "none" : "block";
				modal.classList.toggle("open", !isOpen);
        };

        closeButton.onclick = function () {
            modal.style.display = "none";
            modal.classList.remove("open");
        };

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        };
    }

    setupModal("glossaryModal", "glossaryButton", "closeGlossary");
});

document.addEventListener("DOMContentLoaded", function () {
    var modal = document.getElementById("tiebreakerModal");
    var modalButton = document.getElementById("tiebreakerInfoButton");
    var modalContent = document.querySelector("modal-content");
    var closeModal = document.getElementsByClassName("close")[0];

    modalButton.onclick = function() {
        modal.classList.add("open");
        modal.style.display = "block";
    }

    closeModal.onclick = function() {
        modal.classList.remove("open");
        modal.style.display = "none";
    }
    
    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const tiebreakerButton = document.getElementById("tiebreakerInfoButton");

    function setupModal(modalId, buttonId, closeClass) {
        const modal = document.getElementById(modalId);
        const button = document.getElementById(buttonId);
        const closeButton = modal.querySelector(`.${closeClass}`);

        button.onclick = function () {
            const isOpen = modal.classList.contains("open");
				modal.style.display = isOpen ? "none" : "block";
				modal.classList.toggle("open", !isOpen);
        };

        closeButton.onclick = function () {
            modal.style.display = "none";
            modal.classList.remove("open");
        };

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
                modal.classList.remove("open");
            }
        };
    }
	setupModal("tiebreakerModal", "tiebreakerInfoButton", "close");
});


function myFunction() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "block") {
        x.style.display = "none";
    } else {
        x.style.display = "block";
    }
};
