
function initDownloadLoading() {
  const download_controls = document.querySelectorAll(".download-loading");

  download_controls.forEach((control) => {
    control.addEventListener("click", () => {
      if (control.dataset.downloadLoading === "true") {
        return;
      }

      control.dataset.downloadLoading = "true";
      control.setAttribute("aria-disabled", "true");
      control.style.pointerEvents = "none";
      control.style.opacity = "0.6";
      control.style.cursor = "not-allowed";

      const label = control.querySelector("p");
      const original_label = label.textContent;

      label.textContent = "Downloading..";

      const spinner = document.createElement("img");
      spinner.src = control.dataset.spinnerSrc;
      spinner.alt = "";
      spinner.className = "width-3 height-3 margin-right-1";
      control.insertBefore(spinner, label);

      // Disable submit buttons after their normal form action is triggered.
      if (control.tagName === "BUTTON") {
        setTimeout(() => {
          control.disabled = true;
        }, 0);
      }

      // Restore the control so the user can retry if necessary.
      setTimeout(() => {
        control.dataset.downloadLoading = "false";
        control.removeAttribute("aria-disabled");
        control.style.pointerEvents = "";
        control.style.opacity = "";
        control.style.cursor = "";

        if (control.tagName === "BUTTON") {
          control.disabled = false;
        }

        spinner.remove();
        label.textContent = original_label;
      }, 2000);
    });
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initDownloadLoading);
} else {
  initDownloadLoading();
}
