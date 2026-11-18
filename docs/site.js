/* Shared site helpers: menus, phone menu, full-screen slides, slide decks, 3D tilt, FAQ search,
   feedback forms that open a pre-filled GitHub issue, and live GitHub project stats. No libraries. */
(function () {
  "use strict";
  const $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Instagram login comes back to the site address; the app lives on start.html. */
  const appPage = document.body.dataset.app;
  if (appPage && /^#(ig|error)=/.test(location.hash) && !location.pathname.endsWith(appPage)) { location.replace(appPage + location.hash); return; }

  /* ---------- desktop dropdown menus ---------- */
  const dds = $$(".dd");
  const closeAll = except => dds.forEach(d => { if (d !== except) { d.classList.remove("open"); const b = d.querySelector(".dd-btn"); if (b) b.setAttribute("aria-expanded", "false"); } });
  dds.forEach(d => {
    const b = d.querySelector(".dd-btn");
    b.addEventListener("click", e => { e.stopPropagation(); const open = !d.classList.contains("open"); closeAll(d); d.classList.toggle("open", open); b.setAttribute("aria-expanded", String(open)); });
  });
  document.addEventListener("click", e => { if (!e.target.closest(".dd")) closeAll(); });

  /* ---------- phone menu sheet ---------- */
  const sheet = document.getElementById("sheet");
  const setSheet = open => { if (!sheet) return; sheet.hidden = !open; document.body.classList.toggle("no-scroll", open); $$("[data-sheet-open]").forEach(b => b.setAttribute("aria-expanded", String(open))); if (open) { const f = sheet.querySelector("a, button"); if (f) f.focus(); } };
  $$("[data-sheet-open]").forEach(b => b.addEventListener("click", () => setSheet(true)));
  $$("[data-sheet-close]").forEach(b => b.addEventListener("click", () => setSheet(false)));
  if (sheet) sheet.addEventListener("click", e => { if (e.target === sheet || e.target.closest("a")) setSheet(false); });
  document.addEventListener("keydown", e => { if (e.key === "Escape") { closeAll(); setSheet(false); } });

  /* ---------- full-screen slides (home pages) ---------- */
  const slides = $$(".slide");
  if (slides.length) {
    document.documentElement.classList.add("snap");
    const dots = document.createElement("nav"); dots.className = "slide-dots"; dots.setAttribute("aria-label", "Slides");
    dots.innerHTML = slides.map((s, i) => `<a href="#${s.id}" aria-label="${i + 1}. ${s.dataset.title}"><span class="lbl">${s.dataset.title}</span><i></i></a>`).join("");
    document.body.appendChild(dots);
    const count = document.createElement("div"); count.className = "slide-count"; count.setAttribute("aria-hidden", "true"); document.body.appendChild(count);
    const set = i => { $$("a", dots).forEach((a, j) => a.classList.toggle("on", j === i)); count.textContent = `${i + 1} / ${slides.length}`; document.body.classList.toggle("on-dark", slides[i].classList.contains("dark")); };
    const io = new IntersectionObserver(es => { es.forEach(e => { if (e.isIntersecting) set(slides.indexOf(e.target)); }); }, { threshold: 0.55 });
    slides.forEach(s => io.observe(s)); set(0);
    $$("[data-next]").forEach(b => b.addEventListener("click", () => { const s = b.closest(".slide"), n = slides[slides.indexOf(s) + 1]; if (n) n.scrollIntoView({ behavior: reduce ? "auto" : "smooth" }); }));
  }

  /* ---------- horizontal slide decks (feature tour, beginner's guide) ---------- */
  $$(".deck").forEach(deck => {
    const track = deck.querySelector(".deck-track"), items = $$(".deck-slide", deck), prevs = $$(".deck-prev", deck), nexts = $$(".deck-next", deck), dones = $$(".deck-done", deck), dotsEl = deck.querySelector(".deck-dots"), countEl = deck.querySelector(".deck-count");
    let cur = 0;
    if (dotsEl) dotsEl.innerHTML = items.map((it, i) => `<button type="button" aria-label="Go to ${i + 1}: ${it.dataset.title || ""}"></button>`).join("");
    const go = (i, fromBtn) => { i = Math.max(0, Math.min(items.length - 1, i)); track.scrollTo({ left: i * track.clientWidth, behavior: reduce ? "auto" : "smooth" }); set(i);
      if (fromBtn) { const bar = deck.querySelector(".deck-bar"), head = document.querySelector(".top"), off = (head ? head.offsetHeight : 0) + (bar ? bar.offsetHeight : 0) + 24; if (track.getBoundingClientRect().top < off) window.scrollTo({ top: deck.getBoundingClientRect().top + scrollY - (head ? head.offsetHeight : 0) - 12, behavior: reduce ? "auto" : "smooth" }); } };
    const set = i => { if (i === cur && deck.dataset.ready) return; cur = i; deck.dataset.ready = 1;
      if (dotsEl) $$("button", dotsEl).forEach((b, j) => { b.classList.toggle("on", j === i); b.setAttribute("aria-current", j === i ? "step" : "false"); });
      if (countEl) countEl.textContent = `${i + 1} of ${items.length}`;
      const last = i === items.length - 1;
      prevs.forEach(b => { b.disabled = i === 0; }); nexts.forEach(b => { b.hidden = last && dones.length > 0; b.disabled = last; }); dones.forEach(b => { b.hidden = !last; });
      items.forEach((it, j) => { it.setAttribute("aria-hidden", String(j !== i)); it.inert = j !== i; });
      $$("[data-deck-label]", deck).forEach(el => { el.textContent = items[i].dataset.title || ""; });
      if (items[i].id && deck.dataset.ready === "2") history.replaceState(null, "", "#" + items[i].id); deck.dataset.ready = 2; };
    prevs.forEach(b => b.addEventListener("click", () => go(cur - 1, true)));
    nexts.forEach(b => b.addEventListener("click", () => go(cur + 1, true)));
    if (dotsEl) dotsEl.addEventListener("click", e => { const b = e.target.closest("button"); if (b) go($$("button", dotsEl).indexOf(b)); });
    let t; track.addEventListener("scroll", () => { clearTimeout(t); t = setTimeout(() => { set(Math.round(track.scrollLeft / track.clientWidth)); }, 80); }, { passive: true });
    deck.addEventListener("keydown", e => { if (e.target.closest("input, textarea, select")) return; if (e.key === "ArrowRight") { go(cur + 1); e.preventDefault(); } if (e.key === "ArrowLeft") { go(cur - 1); e.preventDefault(); } });
    window.addEventListener("resize", () => { track.scrollTo({ left: cur * track.clientWidth }); });
    const start = Math.max(0, items.findIndex(it => "#" + it.id === location.hash));
    set(start); if (start > 0) requestAnimationFrame(() => track.scrollTo({ left: start * track.clientWidth }));
  });

  /* ---------- 3D tilt on hero visuals ---------- */
  if (!reduce && window.matchMedia("(pointer: fine)").matches) {
    $$(".tilt").forEach(el => {
      const host = el.closest(".slide, section") || document.body;
      host.addEventListener("pointermove", e => { const r = host.getBoundingClientRect(), x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5; el.style.transform = `perspective(1400px) rotateY(${-8 + x * 10}deg) rotateX(${4 - y * 8}deg)`; });
      host.addEventListener("pointerleave", () => { el.style.transform = ""; });
    });
  }

  /* ---------- FAQ search ---------- */
  const q = document.getElementById("q");
  if (q) {
    const pre = new URLSearchParams(location.search).get("q");
    const items = $$(".faq-group details"), none = document.getElementById("faq-none");
    const norm = s => s.toLowerCase().replace(/[^a-z0-9 ]/g, " ");
    q.addEventListener("input", () => {
      const words = norm(q.value).split(/\s+/).filter(Boolean); let shown = 0;
      items.forEach(d => { const hit = words.every(w => norm(d.textContent).includes(w)); d.hidden = !hit; if (hit) shown++; d.open = words.length > 0 && hit && shown <= 3; });
      $$(".faq-group").forEach(g => { g.hidden = !$$("details", g).some(d => !d.hidden); });
      if (none) none.hidden = shown > 0;
    });
    if (pre) { q.value = pre; q.dispatchEvent(new Event("input")); }
  }

  /* ---------- feedback and problem forms: open a pre-filled GitHub issue ---------- */
  $$("form[data-gh-issue]").forEach(f => f.addEventListener("submit", e => {
    e.preventDefault();
    const d = new FormData(f), kind = f.dataset.kind || "Feedback";
    const lines = [...d.entries()].filter(([k, v]) => k !== "title" && String(v).trim()).map(([k, v]) => `**${k}:** ${v}`);
    lines.push("", `_Sent from ${location.href.split("#")[0]} on ${new Date().toDateString()}_`);
    const title = `${kind}: ${String(d.get("title") || "").trim() || "from the website"}`;
    const url = `${f.dataset.ghIssue}?` + new URLSearchParams({ title, body: lines.join("\n") }).toString();
    const w = window.open(url, "_blank", "noopener"); if (!w) location.href = url;
    const ok = f.querySelector(".form-ok"); if (ok) ok.hidden = false;
  }));

  /* ---------- live GitHub project stats ---------- */
  $$("[data-gh-repo]").forEach(async box => {
    try {
      const r = await fetch("https://api.github.com/repos/" + box.dataset.ghRepo); if (!r.ok) throw 0; const j = await r.json();
      const set = (k, v) => $$(`[data-gh="${k}"]`, box).forEach(el => { el.textContent = v; });
      set("stars", j.stargazers_count.toLocaleString("en-IN")); set("forks", j.forks_count.toLocaleString("en-IN")); set("issues", j.open_issues_count.toLocaleString("en-IN"));
      set("updated", new Date(j.pushed_at).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })); set("license", (j.license && j.license.spdx_id && j.license.spdx_id !== "NOASSERTION" && j.license.spdx_id) || "MIT");
    } catch (e) { $$("[data-gh]", box).forEach(el => { if (el.textContent === "…") el.textContent = "–"; }); }
  });
})();
