if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/service-worker.js").catch(() => {
      // Non-fatal — app still works as a normal web page without it.
    });
  });
}

// Capture the browser's install prompt so pages can offer an explicit
// "Install app" button instead of relying on Chrome's own UI timing.
window.deferredPwaInstallPrompt = null;
window.addEventListener("beforeinstallprompt", (e) => {
  e.preventDefault();
  window.deferredPwaInstallPrompt = e;
  document.querySelectorAll(".pwa-install-btn").forEach((btn) => (btn.style.display = "inline-flex"));
});

async function triggerPwaInstall() {
  const promptEvent = window.deferredPwaInstallPrompt;
  if (!promptEvent) return;
  promptEvent.prompt();
  await promptEvent.userChoice;
  window.deferredPwaInstallPrompt = null;
  document.querySelectorAll(".pwa-install-btn").forEach((btn) => (btn.style.display = "none"));
}

window.addEventListener("appinstalled", () => {
  document.querySelectorAll(".pwa-install-btn").forEach((btn) => (btn.style.display = "none"));
});
