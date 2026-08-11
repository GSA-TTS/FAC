const copyReportIdButton = document.getElementById("copy-report-id");
const reportId = document.getElementById("report-id");
const copyMessage = document.getElementById("copy-report-id-message");

if (copyReportIdButton && reportId && copyMessage) {
  copyReportIdButton.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(reportId.textContent.trim());

      copyMessage.hidden = false;
      copyReportIdButton.setAttribute("aria-label", "Report ID copied");

      setTimeout(() => {
        copyMessage.hidden = true;
        copyReportIdButton.setAttribute("aria-label", "Copy report ID");
      }, 2000);
    } catch (error) {
      console.error("Unable to copy report ID", error);
    }
  });
}
