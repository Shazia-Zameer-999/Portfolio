document.addEventListener("DOMContentLoaded", () => {

    const nav = document.querySelector(".nav");

    window.addEventListener("scroll", () => {

        if(window.scrollY > 40){
            nav.classList.add("nav--scrolled");
        }else{
            nav.classList.remove("nav--scrolled");
        }

    });

    document.querySelectorAll('a[href^="#"]').forEach(link=>{

        link.addEventListener("click",function(e){

            e.preventDefault();

            const target=document.querySelector(this.getAttribute("href"));

            if(target){

                target.scrollIntoView({

                    behavior:"smooth"

                });

            }

        });

    });

});