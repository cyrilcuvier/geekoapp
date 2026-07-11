const API_BASE = window.GEEKO_API_BASE || "";

async function pollGeeko() {
  try {
    const response = await fetch(`${API_BASE}/api/geeko`);
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

async function pollOracle() {
  const banner = document.getElementById("oracle");
  try {
    const response = await fetch(`${API_BASE}/api/oracle`);
    const data = await response.json();
    if (!data.available) {
      banner.textContent = "L'Oracle de Geeko est indisponible.";
      banner.className = "oracle unavailable";
      return;
    }
    banner.textContent = `L'Oracle dit : "${data.message}"`;
    banner.className = data.patched ? "oracle patched" : "oracle unpatched";
  } catch (err) {
    banner.textContent = "L'Oracle de Geeko est indisponible.";
    banner.className = "oracle unavailable";
  }
}

pollGeeko();
pollOracle();
setInterval(pollGeeko, 2000);
setInterval(pollOracle, 5000);
