const API_BASE = window.GEEKO_API_BASE || "";

// Relative to the current document location (no leading slash) when API_BASE is empty,
// so it keeps working under any path prefix the page is served behind (e.g. Rancher's
// built-in Service "proxy" view, which nests the app under /k8s/clusters/.../proxy/).
// A root-relative "/api/..." would instead resolve against the domain root and miss
// that prefix entirely.
function apiUrl(path) {
  if (API_BASE) {
    return `${API_BASE.replace(/\/$/, "")}/${path}`;
  }
  return path;
}

async function pollGeeko() {
  try {
    const response = await fetch(apiUrl("api/geeko"));
    const state = await response.json();
    const geeko = document.getElementById("geeko");
    geeko.style.left = `${state.x}%`;
    geeko.style.top = `${state.y}%`;
    geeko.style.filter = `drop-shadow(0 0 12px ${state.color})`;
    document.getElementById("mood").textContent = `Geeko est ${state.mood} (étape ${state.step})`;
  } catch (err) {
    document.getElementById("mood").textContent = "Geeko a disparu... (API injoignable)";
  }
}

async function pollSage() {
  const banner = document.getElementById("sage");
  try {
    const response = await fetch(apiUrl("api/sage"));
    const data = await response.json();
    if (!data.available) {
      banner.textContent = "Le Sage de Geeko est indisponible.";
      banner.className = "sage unavailable";
      return;
    }
    banner.textContent = `Le Sage dit : "${data.message}"`;
    banner.className = data.patched ? "sage patched" : "sage unpatched";
  } catch (err) {
    banner.textContent = "Le Sage de Geeko est indisponible.";
    banner.className = "sage unavailable";
  }
}

pollGeeko();
pollSage();
setInterval(pollGeeko, 2000);
setInterval(pollSage, 5000);
