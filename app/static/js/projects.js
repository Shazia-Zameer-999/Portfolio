document.addEventListener("DOMContentLoaded",()=>{

    document.querySelectorAll(".project-card").forEach(card=>{

        card.addEventListener("mouseenter",()=>{

            card.classList.add("active");

        });

        card.addEventListener("mouseleave",()=>{

            card.classList.remove("active");

        });

    });

});