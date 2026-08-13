const copyReportIdButtons = document.querySelectorAll(".copy-report-id");

copyReportIdButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const container = button.parentElement;
    const reportId = container.querySelector(".report-id");
    const copyMessage = container.querySelector(".copy-report-id-message");

    if (!reportId || !copyMessage) {
      return;
    }

    try {
      await navigator.clipboard.writeText(reportId.textContent.trim());

      copyMessage.hidden = false;
      button.setAttribute("aria-label", "Report ID copied");

      setTimeout(() => {
        copyMessage.hidden = true;
        button.setAttribute("aria-label", "Copy report ID");
      }, 2000);
    } catch (error) {
      console.error("Unable to copy report ID", error);
    }
  });
});
