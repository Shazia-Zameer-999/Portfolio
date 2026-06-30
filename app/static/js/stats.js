document.addEventListener("DOMContentLoaded", () => {

    const counters = document.querySelectorAll(".about__stat-number");

    const observer = new IntersectionObserver((entries) => {

        entries.forEach(entry => {

            if (!entry.isIntersecting) return;

            const counter = entry.target;

            const target = parseInt(counter.dataset.count);

            let current = 0;

            const duration = 1800;

            const step = Math.ceil(target / (duration / 16));

            const update = () => {

                current += step;

                if (current >= target) {
                    counter.textContent = target;
                    return;
                }

                counter.textContent = current;

                requestAnimationFrame(update);

            };

            update();

            observer.unobserve(counter);

        });

    }, {
        threshold: 0.5
    });

    counters.forEach(counter => observer.observe(counter));

});