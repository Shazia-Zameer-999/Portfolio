document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".project-card").forEach((card) => {
        card.addEventListener("mouseenter", () => {
            card.classList.add("active");
        });

        card.addEventListener("mouseleave", () => {
            card.classList.remove("active");
        });
    });

    document.querySelectorAll(".project-card__expand").forEach((button) => {
        button.addEventListener("click", () => {
            const projectId = button.dataset.project;
            const caseStudy = document.getElementById(`case-${projectId}`);

            if (!caseStudy) {
                return;
            }

            const isExpanded = button.getAttribute("aria-expanded") === "true";
            button.setAttribute("aria-expanded", String(!isExpanded));
            caseStudy.hidden = isExpanded;
        });
    });
});