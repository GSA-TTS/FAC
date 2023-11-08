(function () {
  const toggleBtn = document.getElementById('orientation-toggle');
  const dismissBtn = document.querySelector('.dismiss-orientation-modal');

  function showModal() {
    const modalIsHidden = !document.body.classList.contains(
      'usa-js-modal--active'
    );

    if (modalIsHidden) toggleBtn.click();
  }

  function dismissModal() {
    const modalIsVisible = document.body.classList.contains(
      'usa-js-modal--active'
    );

    if (modalIsVisible) {
      dismissBtn.click();
      clearEventHandlers();
    }
  }

  function checkPortrait() {
    const isPortrait = screen.orientation.type.includes('portrait');

    if (isPortrait) {
      showModal();
    } else {
      dismissModal();
    }
  }

  function clearEventHandlers() {
    // if the modal is dismissed, we shouldn't show it again
    window.removeEventListener('load', checkPortrait);
    window.removeEventListener('orientationchange', checkPortrait);
  }

  dismissBtn.addEventListener('click', dismissModal);

  window.addEventListener('load', checkPortrait);
  window.addEventListener('orientationchange', checkPortrait);
})();
