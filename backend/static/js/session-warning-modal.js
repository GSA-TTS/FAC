document.addEventListener("DOMContentLoaded", function () {
    const modalTrigger = document.createElement("a");
    modalTrigger.setAttribute("href", `#session-warning-modal`);
    modalTrigger.setAttribute("data-open-modal", "");
    modalTrigger.setAttribute("aria-controls", 'session-warning-modal');
    modalTrigger.setAttribute("role", "button");
    modalTrigger.className = "sign-in display-flex flex-row";
    document.body.appendChild(modalTrigger);

    setTimeout(() => {
        modalTrigger.click();
        modalTrigger.remove();
    }, 100); 
});