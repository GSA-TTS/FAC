document.addEventListener("DOMContentLoaded", function () {

    const modalTrigger = document.createElement("a");
    modalTrigger.setAttribute("href", `#session-expired-modal`);
    modalTrigger.setAttribute("data-open-modal", "");
    modalTrigger.setAttribute("aria-controls", 'session-expired-modal');
    modalTrigger.setAttribute("role", "button");
    modalTrigger.className = "sign-in display-flex flex-row";
    document.body.appendChild(modalTrigger);

    setTimeout(() => {
        modalTrigger.click();
        modalTrigger.remove();
    }, 100);
});
