document.addEventListener("DOMContentLoaded", () => {

    const items = document.querySelectorAll(

        ".reveal-up, .reveal-fade, .reveal-scale, .reveal-timeline"

    );

    const observer = new IntersectionObserver((entries)=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.classList.add("is-visible");

                observer.unobserve(entry.target);

            }

        });

    },{

        threshold:0.15

    });

    items.forEach(item=>observer.observe(item));

});