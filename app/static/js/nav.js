document.addEventListener("DOMContentLoaded", () => {

    const nav = document.getElementById("nav");
    const menuToggle = document.getElementById("menuToggle");
    const mobileMenu = document.getElementById("navMobile");

    if (!nav || !menuToggle || !mobileMenu) return;

    const menuIcon = `
<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M3 6H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M3 12H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M3 18H21" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
`;

    const closeIcon = `
<svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
    <path d="M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
</svg>
`;

    let menuOpen = false;

    menuToggle.innerHTML = menuIcon;

    function openMenu() {

        menuOpen = true;

        menuToggle.innerHTML = closeIcon;

        mobileMenu.classList.add("is-open");

        document.body.classList.add("nav-open");

        menuToggle.setAttribute("aria-expanded", "true");

        mobileMenu.setAttribute("aria-hidden", "false");

    }

    function closeMenu() {

        menuOpen = false;

        menuToggle.innerHTML = menuIcon;

        mobileMenu.classList.remove("is-open");

        document.body.classList.remove("nav-open");

        menuToggle.setAttribute("aria-expanded", "false");

        mobileMenu.setAttribute("aria-hidden", "true");

    }

    function toggleMenu() {

        if (menuOpen) {

            closeMenu();

        } else {

            openMenu();

        }

    }

    menuToggle.addEventListener("click", toggleMenu);

    window.addEventListener("scroll", () => {

        if (window.scrollY > 40) {

            nav.classList.add("nav--scrolled");

        } else {

            nav.classList.remove("nav--scrolled");

        }

    });

    document.querySelectorAll(".nav__mobile-link").forEach(link => {

        link.addEventListener("click", () => {

            closeMenu();

        });

    });

    document.addEventListener("keydown", e => {

        if (e.key === "Escape") {

            closeMenu();

        }

    });

    mobileMenu.addEventListener("click", (e) => {
        if (e.target === mobileMenu) {
            closeMenu();
        }
    });

});