/**
 * ========================================================
 * CONTACT SECTION LOGIC
 * Handles scroll reveals and terminal success animation
 * ========================================================
 */
console.log("contact.js loaded");
document.addEventListener('DOMContentLoaded', () => {
    initScrollReveals();
    initContactForm();
});

/**
 * Initializes Intersection Observer for smooth scrolling reveal animations.
 */
function initScrollReveals() {
    const revealElements = document.querySelectorAll('.reveal-up');

    const revealObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('active');
                // Unobserve after revealing so it only animates once
                observer.unobserve(entry.target);
            }
        });
    }, {
        root: null,
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    });

    revealElements.forEach(el => revealObserver.observe(el));
}

/**
 * Intercepts form submission to trigger the cinematic terminal UI
 */
function initContactForm() {
    const form = document.getElementById('premium-contact-form');
    const terminal = document.getElementById('terminal-success');
    const terminalBody = document.getElementById('terminal-output');
    const isMobileView = () => window.matchMedia('(max-width: 768px)').matches;

    if (!form || !terminal) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const formData = new FormData(form)
        const data = {
            name: formData.get("name"),
            email: formData.get("email"),
            subject: formData.get("subject"),
            message: formData.get("message")
        }

        const response = await fetch("/api/contact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)

        })
        const result = await response.json()
        console.log(result)

        // 1. You would normally handle your actual fetch/API call here.
        // Example: await fetch('/api/contact', { method: 'POST', body: new FormData(form) });

        // 2. Hide form and show terminal frame
        if (response.ok && result.success) {

            form.style.display = "none";

            terminal.classList.remove("hidden");

            await runTerminalSequence(terminalBody);

            if (isMobileView()) {
                await new Promise(resolve => setTimeout(resolve, 3000));
            } else {
                await new Promise(resolve => {

                    function handler() {

                        document.removeEventListener("keydown", handler);

                        resolve();

                    }

                    document.addEventListener("keydown", handler);

                });
            }

            terminal.classList.add("hidden");

            form.reset();

            form.style.display = "block";
            form.querySelector("input").focus();

        } else {

            alert(result.message || "Something went wrong.");

        }
    });
}

/**
 * Generates the terminal typing effect asynchronously
 * @param {HTMLElement} container - The wrapper for the terminal output
 */
async function runTerminalSequence(container) {
    // Helper to pause execution
    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // The script we want the terminal to output
    const sequence = [
        { text: "sending...", prompt: "$", class: "term-text" },

        { text: "Message delivered successfully.", prompt: "✓", class: "term-success" },

        { text: "Thanks for reaching out!", prompt: ">", class: "term-text" },

        { text: "I'll get back to you as soon as I can.", prompt: ">", class: "term-text" },

        { text: "Press any key to return to the contact form...", prompt: "$", class: "term-muted" }
    ];

    container.innerHTML = ''; // Clear container

    for (let i = 0; i < sequence.length; i++) {
        const line = sequence[i];

        // Create line container
        const lineWrapper = document.createElement('div');
        lineWrapper.className = 'term-line';

        // Add prompt ($, ✓, >)
        const promptSpan = document.createElement('span');
        promptSpan.className = line.prompt === '✓' ? 'term-success term-prompt' : 'term-prompt';
        promptSpan.textContent = line.prompt;

        // Add content text
        const textSpan = document.createElement('span');
        textSpan.className = line.class;

        lineWrapper.appendChild(promptSpan);
        lineWrapper.appendChild(textSpan);

        // Append cursor to current line
        const cursor = document.createElement('span');
        cursor.className = 'term-cursor';
        lineWrapper.appendChild(cursor);

        container.appendChild(lineWrapper);

        // Simulate typing effect letter by letter
        for (let char of line.text) {
            textSpan.textContent += char;
            await sleep(40); // typing speed
        }

        // Remove cursor from this line before moving to the next
        cursor.remove();

        // Pause between lines
        await sleep(400);
    }

    // Add final blinking cursor at the end
    const finalCursorLine = document.createElement('div');
    finalCursorLine.innerHTML = `<span class="term-prompt">$</span><span class="term-cursor"></span>`;
    container.appendChild(finalCursorLine);
}