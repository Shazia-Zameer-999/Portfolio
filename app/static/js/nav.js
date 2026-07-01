document.addEventListener("DOMContentLoaded", () => {
    const nav = document.querySelector(".nav");
    // const hamburger = document.getElementById("navHamburger");
    const mobileMenu = document.getElementById("navMobile");
    const mobileClose = document.getElementById("navMobileClose");
    const menuIcon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
        xmlns="http://www.w3.org/2000/svg">

        <path d="M3 6H21"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"/>

        <path d="M3 12H21"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"/>

        <path d="M3 18H21"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"/>

    </svg>
    `;

    const closeIcon = `
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
        xmlns="http://www.w3.org/2000/svg">

        <path d="M6 6L18 18"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"/>

        <path d="M18 6L6 18"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"/>

    </svg>
    `;
    const menuToggle=document.getElementById("menuToggle");
    menuToggle.innerHTML = menuIcon;
    let menuOpen = false;

    menuToggle.addEventListener("click",() =>{
        menuOpen=!menuOpen
        if (menuOpen){
            menuToggle.innerHTML=closeIcon
            mobileMenu.classList.add("is-open")

        }else{
            menuToggle.innerHTML=menuIcon
            mobileMenu.classList.remove("is-open")


        }
    }
    )

    const openMobileMenu = () => {
        // hamburger.classList.add("is-open");
        mobileMenu.classList.add("is-open");
        // hamburger.setAttribute("aria-expanded", "true");
        mobileMenu.setAttribute("aria-hidden", "false");
        document.body.classList.add("nav-open");
    };

    const closeMobileMenu = () => {
        // hamburger.classList.remove("is-open");
        mobileMenu.classList.remove("is-open");
        // hamburger.setAttribute("aria-expanded", "false");
        mobileMenu.setAttribute("aria-hidden", "true");
        document.body.classList.remove("nav-open");
    };

    window.addEventListener("scroll", () => {
        if (window.scrollY > 40) {
            nav.classList.add("nav--scrolled");
        } else {
            nav.classList.remove("nav--scrolled");
        }
    });

    // hamburger.addEventListener("click", () => {
    //     if (mobileMenu.classList.contains("is-open")) {
    //         closeMobileMenu();
    //         return;
    //     }

    //     openMobileMenu();
    // });

    if (mobileClose) {
        mobileClose.addEventListener("click", closeMobileMenu);
    }

    document.querySelectorAll('a[href^="#"]').forEach((link) => {
        link.addEventListener("click", function (e) {
            e.preventDefault();

            const target = document.querySelector(this.getAttribute("href"));

            if (target) {
                target.scrollIntoView({
                    behavior: "smooth",
                });
            }

            closeMobileMenu();
        });
    });

    // document.addEventListener("click", (e) => {
    //     if (!mobileMenu.contains(e.target) && !hamburger.contains(e.target)) {
    //         closeMobileMenu();
    //     }
    // });

    // document.addEventListener("keydown", (e) => {
    //     if (e.key === "Escape") {
    //         closeMobileMenu();
    //     }
    // });
});