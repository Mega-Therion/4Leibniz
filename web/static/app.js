const runBtn = document.getElementById("run-btn");
const runStatus = document.getElementById("run-status");
const oracleResult = document.getElementById("oracle-result");
const receipt = document.getElementById("receipt");
const buildOutput = document.getElementById("build-output");
const moduleGrid = document.getElementById("module-grid");

const MODULE_LABELS = {
  Characteristica: "Dyadica: Nihil \u2194 Ens",
  SpatiumRelativum: "Relational Spacetime",
  VisViva: "Active Energy",
  LexContinuitatis: "Invariant Band",
  Harmonia: "Anti-Drift Theorem",
  Calculemus: "Master Evaluation",
};

async function loadModules() {
  try {
    const res = await fetch("/api/modules");
    const data = await res.json();
    moduleGrid.innerHTML = "";
    data.modules.forEach((m, i) => {
      const card = document.createElement("div");
      card.className = "module-card";
      const thItems = m.theorems.map((t) => `<li>${t}</li>`).join("");
      card.innerHTML = `
        <div class="num">MODULE ${String(i + 1).padStart(2, "0")}</div>
        <h3>${m.title}</h3>
        <div class="origin">${m.origin}</div>
        <div class="subtitle">${m.subtitle}</div>
        <div class="stats">
          <span><b>${m.theorems.length}</b> theorems</span>
          <span><b>${m.definitions.length}</b> definitions</span>
          <span><b>${m.line_count}</b> lines</span>
        </div>
        ${thItems ? `<ul>${thItems}</ul>` : ""}
      `;
      moduleGrid.appendChild(card);
    });
  } catch (e) {
    moduleGrid.innerHTML = "<p class='loading-modules'>Failed to load modules.</p>";
  }
}

function renderReceipt(b) {
  const ok = b.status === "done" && b.exit_code === 0;
  const cls = ok ? "ok" : "fail";
  const verdict = ok
    ? "\u2713 CALCULEMUS COMPLETE"
    : b.status === "running"
      ? "\u23f3 VERIFYING\u2026"
      : "\u2717 VERIFICATION FAILED";
  receipt.innerHTML = `
    <div class="row"><span class="label">Verdict</span><span class="${cls}">${verdict}</span></div>
    <div class="row"><span class="label">Status</span><span>${b.status}</span></div>
    <div class="row"><span class="label">Exit code</span><span>${b.exit_code ?? "\u2014"}</span></div>
    <div class="row"><span class="label">Elapsed</span><span>${b.elapsed != null ? b.elapsed + "s" : "\u2014"}</span></div>
  `;
  buildOutput.textContent = b.output || "(no output yet)";
}

function setStatus(b) {
  runStatus.className = "run-status " + (b.status === "done" ? (b.exit_code === 0 ? "done" : "error") : b.status);
  runStatus.textContent = b.status;
  runBtn.disabled = b.status === "running";
  if (b.status === "running" || b.status === "done" || b.status === "error" || b.status === "timeout") {
    oracleResult.classList.remove("hidden");
    renderReceipt(b);
  }
}

let pollTimer = null;
function pollBuild() {
  if (pollTimer) return;
  pollTimer = setInterval(async () => {
    try {
      const res = await fetch("/api/build");
      const b = await res.json();
      setStatus(b);
      if (b.status !== "running") {
        clearInterval(pollTimer);
        pollTimer = null;
      }
    } catch (e) { /* ignore */ }
  }, 1200);
}

runBtn.addEventListener("click", async () => {
  try {
    await fetch("/api/build/run", { method: "POST" });
  } catch (e) { /* ignore */ }
  pollBuild();
});

loadModules();
pollBuild();
