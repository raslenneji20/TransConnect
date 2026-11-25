document.addEventListener("DOMContentLoaded", () => {
    const bubbleField = document.querySelector(".bubble-field");

    if (bubbleField) {
        const bubbleCount = window.innerWidth < 700 ? 14 : 26;

        for (let index = 0; index < bubbleCount; index += 1) {
            const bubble = document.createElement("span");
            const size = 36 + Math.random() * 100;
            bubble.className = "bubble";
            bubble.style.setProperty("--bubble-left", `${Math.random() * 100}%`);
            bubble.style.setProperty("--bubble-size", `${size.toFixed(0)}px`);
            bubble.style.setProperty("--bubble-duration", `${14 + Math.random() * 18}s`);
            bubble.style.setProperty("--bubble-delay", `${-Math.random() * 24}s`);
            bubble.style.setProperty("--bubble-sway", `${4 + Math.random() * 5}s`);
            bubble.style.setProperty("--bubble-travel", `${-70 + Math.random() * 140}px`);
            bubble.style.setProperty("--bubble-border", `${(.22 + Math.random() * .24).toFixed(2)}`);
            bubbleField.appendChild(bubble);
        }
    }

    const toggle = document.querySelector(".nav-toggle");
    const navigation = document.querySelector("#primary-navigation");

    if (!toggle || !navigation) {
        return;
    }

    toggle.addEventListener("click", () => {
        const isOpen = toggle.getAttribute("aria-expanded") === "true";
        toggle.setAttribute("aria-expanded", String(!isOpen));
        navigation.classList.toggle("is-open", !isOpen);
    });
});
