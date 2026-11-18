/* Founder Plus: small helpers shared by every page (mobile menu, FAQ search). */
(function () {
  "use strict";
  const btn = document.querySelector(".menu-btn"), menu = document.getElementById("mnav");
  if (btn && menu) {
    btn.addEventListener("click", () => {
      const open = btn.getAttribute("aria-expanded") !== "true";
      btn.setAttribute("aria-expanded", String(open)); menu.hidden = !open;
      btn.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
    menu.addEventListener("click", e => { if (e.target.closest("a")) { menu.hidden = true; btn.setAttribute("aria-expanded", "false"); } });
  }
  const q = document.getElementById("q");
  if (q) {
    const items = [...document.querySelectorAll(".faq-group details")], none = document.getElementById("faq-none");
    const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, " ");
    q.addEventListener("input", () => {
      const words = norm(q.value).split(/\s+/).filter(Boolean);
      let shown = 0;
      items.forEach(d => { const hit = words.every(w => norm(d.textContent).includes(w)); d.hidden = !hit; if (hit) shown++; d.open = words.length > 0 && hit && shown <= 3; });
      document.querySelectorAll(".faq-group").forEach(g => { g.hidden = ![...g.querySelectorAll("details")].some(d => !d.hidden); });
      if (none) none.hidden = shown > 0;
    });
  }
})();
