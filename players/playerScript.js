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

document.addEventListener("DOMContentLoaded", function () {{
	const images = document.querySelectorAll(".playerPicture");
	let validImageFound = false;

	images.forEach((img) => {{
		img.onload = function () {{
			if (!validImageFound) {{
				validImageFound = true;
			}} else {{
				img.style.display = "none"; 
			}}
		}};

		img.onerror = function () {{
			img.style.display = "none";
		}};
	}});
}});