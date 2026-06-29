document.addEventListener("DOMContentLoaded",()=>{

    const timeline=document.querySelectorAll(".timeline__item");

    const observer=new IntersectionObserver(entries=>{

        entries.forEach(entry=>{

            if(entry.isIntersecting){

                entry.target.classList.add("is-visible");

            }

        });

    },{

        threshold:0.2

    });

    timeline.forEach(item=>observer.observe(item));

});