/* drvarada live editor — injected by editor.py, never part of a build.
 *
 * The rendered page is the editing surface. Hover highlights what you can
 * change; clicking text edits it in place; clicking an image or a link opens an
 * inspector panel beside it. Sections carry a small toolbar for move / duplicate
 * / delete. A tokens panel edits the design system itself.
 *
 * Every target is identified by the data address the build stamped into the
 * markup (`data-od`, `data-od-img`, `data-od-link`, `data-od-sec`), so the
 * server never has to guess which value the browser meant. Copy without an
 * address falls back to matching on its text.
 */
(() => {
  "use strict";
  if (window.__odEditor) return;
  window.__odEditor = true;

  const INLINE = new Set(["EM", "STRONG", "BR", "B", "I", "SMALL", "SUB", "SUP", "WBR"]);
  const TEXTY = new Set(["H1", "H2", "H3", "H4", "H5", "P", "LI", "A", "TD", "TH",
    "DT", "DD", "FIGCAPTION", "BLOCKQUOTE", "SUMMARY", "SPAN", "BUTTON", "CITE",
    "TIME", "EM", "STRONG", "SMALL", "DIV"]);

  const slug = location.pathname.replace(/^\/|\.html$/g, "") || "index";
  // This same script runs twice in device preview: once in the page that owns
  // the toolbar (the host) and once inside the device iframe. The frame keeps
  // every editing affordance but cedes its chrome and its live-reload duty to
  // the host, which can reach in through __odApi because both are same-origin.
  const framed = (() => {
    // parent, not top: the host is always the immediate parent, and top would
    // misidentify both pages if the editor itself ever runs inside a frame
    // (a test harness, a VS Code webview).
    try { return window.self !== window.parent && !!window.parent.__odEditor; }
    catch (e) { return false; }
  })();
  if (framed) document.documentElement.classList.add("od-in-frame");
  let mode = sessionStorage.getItem("odEditMode") === "1" ||
    location.search.indexOf("od-edit") !== -1;
  let editing = null;      // element being text-edited
  let original = "";       // its innerHTML before editing
  let target = null;       // element the inspector is bound to
  let ver = null;

  /* ---------- chrome ---------- */
  const ui = document.createElement("div");
  ui.id = "od-ui";
  ui.innerHTML =
    '<div id="od-bar">' +
      '<button id="od-toggle" type="button"></button>' +
      '<button id="od-pages" type="button" title="All pages">Pages</button>' +
      '<button id="od-device" type="button" title="Preview at a device width"></button>' +
      '<button id="od-notebtn" type="button" title="Pin a change to an element — builds into the agent prompt">Note</button>' +
      '<button id="od-fbbtn" type="button" title="Every pinned change as one prompt to paste into your agent chat">⚑ Agent</button>' +
      '<button id="od-tokens" type="button" title="Design tokens">Tokens</button>' +
      '<button id="od-site" type="button" title="Practo links, phone, WhatsApp">Site</button>' +
      '<button id="od-undo" type="button" title="Undo (Ctrl+Z)">Undo</button>' +
      '<button id="od-redo" type="button" title="Redo (Ctrl+Shift+Z)">Redo</button>' +
      '<button id="od-versions" type="button" title="Version history">Versions</button>' +
    '</div>' +
    '<div id="od-devmenu" hidden></div>' +
    '<div id="od-hl" hidden><span id="od-hl-tag"></span></div>' +
    '<div id="od-sectools" hidden></div>' +
    '<aside id="od-panel" hidden></aside>' +
    '<div id="od-toast" hidden></div>';
  document.body.appendChild(ui);
  const $ = (id) => ui.querySelector(id);
  const bar = $("#od-bar"), toggle = $("#od-toggle"), hl = $("#od-hl"),
    hlTag = $("#od-hl-tag"), sectools = $("#od-sectools"),
    panel = $("#od-panel"), toastBox = $("#od-toast");
  let toastTimer = 0;

  function paintToggle() {
    toggle.textContent = mode ? "✎ Editing" : "✎ Edit";
    toggle.classList.toggle("on", mode);
    bar.classList.toggle("open", mode);
    document.documentElement.classList.toggle("od-mode", mode);
    if (!mode) { hl.hidden = true; sectools.hidden = true; closePanel(); }
  }

  function toast(text, kind, buttons) {
    clearTimeout(toastTimer);
    toastBox.innerHTML = "";
    const msg = document.createElement("div");
    msg.className = "od-msg";
    msg.textContent = text;
    toastBox.appendChild(msg);
    (buttons || []).forEach((b) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = b.label;
      btn.onclick = () => { hideToast(); b.fn(); };
      toastBox.appendChild(btn);
    });
    toastBox.className = kind || "";
    toastBox.hidden = false;
    if (!buttons) toastTimer = setTimeout(hideToast, kind === "err" ? 12000 : 5000);
  }
  const hideToast = () => { toastBox.hidden = true; };

  // Every mutating call carries the per-run secret the server injected into this
  // page. Loopback alone is not protection: a POST like this is a "simple"
  // request, so any site the user has open could otherwise drive the editor.
  // Every mutating response carries the new history state, so the Undo and
  // Redo buttons stay truthful without a second round trip after each edit.
  // Version labels are the user's own edit text echoed back. Panels are built
  // with innerHTML, so anything from the server has to be escaped on the way
  // in — a paragraph edited to contain "<img onerror>" must not execute when
  // it shows up in the history list.
  const esc = (v) => String(v == null ? "" : v)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

  const post = (route, body) =>
    fetch(route, {
      method: "POST",
      headers: { "X-OD-Token": window.__odToken || "" },
      body: JSON.stringify(body || {}),
    }).then((r) => r.json()).then((res) => {
      if (res && res.history) showHistory(res.history);
      return res;
    });

  function saved(res, extra) {
    if (res.error) { toast(res.error, "err"); return false; }
    const where = res.file ? res.file + ":" + res.line : "";
    toast((extra || "Saved") + (where ? " → " + where : "") +
      (res.applied > 1 ? " (+" + (res.applied - 1) + " more)" : ""), "ok",
      res.file ? [{ label: "Open in code", fn: () => openInCode(res.file, res.line) }] : null);
    return true;
  }

  const openInCode = (file, line) => post("/api/open", { file: file, line: line });
  // History lives on disk now, so the buttons reflect a journal that outlived
  // the last run of the editor rather than a stack that started empty.
  function showHistory(h) {
    if (!h) return;
    const u = $("#od-undo"), r = $("#od-redo");
    u.disabled = !h.undo;
    r.disabled = !h.redo;
    u.title = h.undo ? "Undo: " + h.undo + " (Ctrl+Z)" : "Nothing to undo";
    r.title = h.redo ? "Redo: " + h.redo + " (Ctrl+Shift+Z)" : "Nothing to redo";
  }

  const step = (what) => post("/api/" + what).then((res) => {
    showHistory(res.history);
    toast(res.ok ? (what === "undo" ? "Undid: " : "Redid: ") + res.label
                 : (res.error || "Nothing to " + what), res.ok ? "ok" : "err");
  });
  const undo = () => step("undo");
  const redo = () => step("redo");

  /* ---------- target discovery ---------- */
  const onlyInline = (el) => {
    for (const c of el.querySelectorAll("*")) if (!INLINE.has(c.tagName)) return false;
    return true;
  };
  const addr = (el, kind) => el && el.getAttribute("data-od" + (kind ? "-" + kind : ""));

  function pick(start) {
    let el = start, found = null;
    while (el && el.nodeType === 1 && el !== document.body && !ui.contains(el)) {
      if (addr(el, "img") || addr(el, "link")) return el;      // whole widget
      if (!found && TEXTY.has(el.tagName) && el.textContent.trim() && onlyInline(el))
        found = el;
      else if (found && !addr(el)) break;
      if (found && addr(found)) break;
      el = el.parentElement;
    }
    return found;
  }

  const kindOf = (el) =>
    addr(el, "img") ? "image" : addr(el, "link") ? "link" :
    el.tagName === "A" ? "link" : "text";

  function highlight(el) {
    if (!el) { hl.hidden = true; return; }
    const r = el.getBoundingClientRect();
    hl.style.left = r.left + scrollX - 3 + "px";
    hl.style.top = r.top + scrollY - 3 + "px";
    hl.style.width = r.width + 6 + "px";
    hl.style.height = r.height + 6 + "px";
    const k = kindOf(el);
    hlTag.textContent = k === "image" ? "image · click to replace"
      : k === "link" ? "link · click to retarget"
      : el.tagName.toLowerCase() + (addr(el) ? " · " + addr(el) : "") + " · click to edit";
    hl.dataset.kind = k;
    hl.hidden = false;
  }

  /* ---------- section toolbar ---------- */
  let hoverSection = null;
  function showSectionTools(sec) {
    if (!sec || sec === hoverSection) return;
    hoverSection = sec;
    const i = sec.getAttribute("data-od-sec");
    const kind = sec.getAttribute("data-od-kind");
    sectools.innerHTML =
      '<span class="od-sec-label">' + kind + " · sections." + i + "</span>" +
      '<button data-op="up" title="Move up">↑</button>' +
      '<button data-op="down" title="Move down">↓</button>' +
      '<button data-op="duplicate" title="Duplicate">⧉</button>' +
      '<button data-op="delete" class="od-danger" title="Delete section">✕</button>';
    const r = sec.getBoundingClientRect();
    sectools.style.top = r.top + scrollY + 8 + "px";
    sectools.style.left = Math.max(8, r.right + scrollX - 232) + "px";
    sectools.hidden = false;
    sectools.querySelectorAll("button").forEach((b) => {
      b.onclick = (ev) => {
        ev.stopPropagation();
        const op = b.dataset.op;
        if (op === "delete" &&
            !confirm("Delete this " + kind + " section from " + slug + "?")) return;
        post("/api/structure", { slug: slug, op: op, list: "sections", index: +i })
          .then((res) => saved(res, op === "delete" ? "Section deleted" :
            op === "duplicate" ? "Section duplicated" : "Section moved"));
      };
    });
  }

  /* ---------- inspector panel ---------- */
  function closePanel() { panel.hidden = true; panel.innerHTML = ""; target = null; }

  function openPanel(title, html, place, kind) {
    panel.dataset.kind = kind || "";
    panel.innerHTML = '<header><b>' + title + '</b>' +
      '<button id="od-close" type="button" title="Close">✕</button></header>' +
      '<div class="od-body">' + html + "</div>";
    panel.hidden = false;
    panel.querySelector("#od-close").onclick = closePanel;
    // Open Design's inspector is a draggable card, and it earns it: a panel
    // that opens over the one element you needed to see has to be movable.
    panel.querySelector("header").onpointerdown = (e) => {
      if (e.target.tagName === "BUTTON") return;
      const dx = panel.offsetLeft - e.clientX, dy = panel.offsetTop - e.clientY;
      const move = (ev) => {
        panel.style.left = Math.max(4, dx + ev.clientX) + "px";
        panel.style.top = Math.max(4, dy + ev.clientY) + "px";
      };
      const up = () => {
        removeEventListener("pointermove", move);
        removeEventListener("pointerup", up);
      };
      addEventListener("pointermove", move);
      addEventListener("pointerup", up);
      e.preventDefault();
    };
    if (place) {
      const r = place.getBoundingClientRect();
      const top = Math.max(8, Math.min(r.top + scrollY, scrollY + innerHeight - 380));
      panel.style.top = top + "px";
      panel.style.left = (r.right + 16 + 360 < innerWidth
        ? r.right + scrollX + 16 : Math.max(8, r.left + scrollX - 376)) + "px";
    } else {
      panel.style.top = scrollY + 76 + "px";
      panel.style.left = Math.max(8, innerWidth - 392) + "px";
    }
  }

  const field = (label, id, value, hint) =>
    '<label class="od-f"><span>' + label + "</span>" +
    '<input id="' + id + '" value="' + (value || "").replace(/"/g, "&quot;") + '">' +
    (hint ? "<small>" + hint + "</small>" : "") + "</label>";

  /* ----- images ----- */
  function imagePanel(el) {
    target = el;
    const a = addr(el, "img");
    post("/api/inspect", { slug: slug, addr: a }).then((res) => {
      const im = (res.value && typeof res.value === "object") ? res.value : {};
      const clinical = /\.(before|after)$/.test(a);
      openPanel(im.src ? "Image" : "Add image",
        '<div id="od-drop" class="od-drop"><b>Drop an image here</b>' +
          "<span>or click to choose · JPEG, PNG, WebP, SVG</span>" +
          '<input type="file" id="od-file" accept="image/*" hidden></div>' +
        (im.src ? '<p class="od-note">Current: ' + im.src +
          (im.w ? " · " + im.w + "×" + im.h : "") + "</p>" : "") +
        field("Alt text (required)", "od-alt", im.alt || "",
          "What the image shows — read by screen readers and image search.") +
        field("Focal point", "od-focus", im.focus || "",
          "e.g. 50% 28% — which part stays visible when the box crops.") +
        (clinical ? field("Consent record (required)", "od-consent", im.consent || "",
          "How and when written patient consent was obtained. The build " +
          "refuses a patient photograph without it.") : "") +
        '<div class="od-acts">' +
          '<button id="od-save" class="od-primary">Save details</button>' +
          (im.src ? '<button id="od-clear" class="od-danger">Remove image</button>' : "") +
        "</div>", el);

      const drop = panel.querySelector("#od-drop");
      const file = panel.querySelector("#od-file");
      drop.onclick = () => file.click();
      file.onchange = () => file.files[0] && upload(file.files[0]);
      ["dragenter", "dragover"].forEach((t) => drop.addEventListener(t, (e) => {
        e.preventDefault(); drop.classList.add("over");
      }));
      ["dragleave", "drop"].forEach((t) => drop.addEventListener(t, (e) => {
        e.preventDefault(); drop.classList.remove("over");
      }));
      drop.addEventListener("drop", (e) => {
        const f = e.dataTransfer.files[0];
        if (f) upload(f);
      });

      function upload(f) {
        const alt = panel.querySelector("#od-alt").value.trim();
        const consentEl = panel.querySelector("#od-consent");
        if (!alt) { toast("Add alt text first — the build requires it.", "err"); return; }
        if (clinical && !(consentEl && consentEl.value.trim())) {
          toast("This is a patient photograph. Record the consent before uploading.",
            "err");
          return;
        }
        toast("Processing " + f.name + "…");
        const fr = new FileReader();
        fr.onload = () => post("/api/image", {
          slug: slug, addr: a, filename: f.name, dataUrl: fr.result, alt: alt,
          focus: panel.querySelector("#od-focus").value.trim(),
          consent: consentEl ? consentEl.value.trim() : "",
        }).then((res) => { if (saved(res, "Image saved")) closePanel(); });
        fr.readAsDataURL(f);
      }

      panel.querySelector("#od-save").onclick = () => {
        const body = { slug: slug, addr: a,
          alt: panel.querySelector("#od-alt").value,
          focus: panel.querySelector("#od-focus").value };
        const c = panel.querySelector("#od-consent");
        if (c) body.consent = c.value;
        post("/api/image-meta", body).then((res) => saved(res, "Details saved"));
      };
      const clear = panel.querySelector("#od-clear");
      if (clear) clear.onclick = () => {
        if (!confirm("Remove this image and show the placeholder again?")) return;
        post("/api/image-clear", { slug: slug, addr: a })
          .then((res) => { if (saved(res, "Image removed")) closePanel(); });
      };
    });
  }

  /* ----- links ----- */
  // A label made of nested markup cannot be replaced with plain text without
  // throwing the markup away. Open Design refuses that edit rather than doing
  // it silently (source-patches.ts, "This link contains nested markup"), and
  // the same reasoning holds here.
  const plainLabel = (el) => !el.querySelector("*") ||
    Array.prototype.every.call(el.querySelectorAll("*"), (c) => INLINE.has(c.tagName));

  function linkPanel(el) {
    target = el;
    const a = addr(el, "link");
    const href = el.getAttribute("href") || "";
    const editable = plainLabel(el);
    Promise.all([
      post("/api/inspect", { slug: slug, addr: a, wantSlugs: true }),
      post("/api/link-where", { href: href }),
    ]).then(([res, use]) => {
      const slugs = res.slugs || [];
      const count = use.count || 0;
      // The interesting question on a 45-page site is not "what should this
      // button point at" but "should the other 59 follow". Ask it up front.
      const scope = count > 1
        ? '<div class="od-scope">' +
            '<label><input type="radio" name="od-scope" value="one" checked> ' +
              'Just this one</label>' +
            '<label><input type="radio" name="od-scope" value="all"> ' +
              'All <b>' + count + "</b> links pointing here</label>" +
            '<p class="od-note">' +
              (use.constant
                ? "This destination is the shared <code>" + use.constant +
                  "</code> constant, so either choice updates every use."
                : (use.where || []).slice(0, 4).join(" · ") +
                  (count > 4 ? " · +" + (count - 4) + " more" : "")) +
            "</p></div>"
        : "";
      openPanel("Link",
        (editable
          ? field("Label", "od-label", el.textContent.trim())
          : '<p class="od-note">This link\'s label contains markup, so it is ' +
            'edited as text on the page rather than here.</p>') +
        field("Destination", "od-href", href,
          "A page slug for an internal link, or a full https:// URL.") +
        '<datalist id="od-slugs">' +
          slugs.map((s) => '<option value="' + s + '">').join("") + "</datalist>" +
        scope +
        '<div class="od-acts"><button id="od-save" class="od-primary">Save link</button></div>',
        el);
      panel.querySelector("#od-href").setAttribute("list", "od-slugs");
      panel.querySelector("#od-save").onclick = () => {
        const picked = panel.querySelector('input[name="od-scope"]:checked');
        const labelBox = panel.querySelector("#od-label");
        post("/api/link", { slug: slug, addr: a, oldHref: href,
          href: panel.querySelector("#od-href").value.trim(),
          scope: picked ? picked.value : "one",
          label: labelBox ? labelBox.value.trim() : undefined })
          .then((r) => {
            if (saved(r, r.everywhere ? "Retargeted " + r.applied + " links"
                                      : "Link saved")) closePanel();
          });
      };
    });
  }

  /* ----- version history ----- */
  // Ported from Open Design's version list: an append-only timeline where
  // restoring an old version writes it forward as a new one, so the version
  // you came from stays reachable. Nothing here can lose a state you have seen.
  function versionsPanel() {
    post("/api/history").then((res) => {
      if (res.error) { toast(res.error, "err"); return; }
      const rows = (res.entries || []).map((e) =>
        '<div class="od-ver' + (e.current ? " od-ver-now" : "") +
          (e.ahead ? " od-ver-ahead" : "") + '">' +
          '<div class="od-ver-head"><b>v' + e.version + "</b>" +
            '<span class="od-ver-when">' + e.when + "</span>" +
            (e.current ? '<span class="od-ver-tag">on this</span>' : "") +
          "</div>" +
          '<div class="od-ver-what">' + esc(e.prompt || e.label) + "</div>" +
          '<div class="od-ver-files">' + e.files.length + " file" +
            (e.files.length === 1 ? "" : "s") + " · " + e.source + "</div>" +
          (e.current ? "" :
            '<button class="od-ver-go" data-id="' + e.id + '">Restore</button>') +
        "</div>").join("");
      openPanel("Versions",
        '<p class="od-note">' + res.depth + ' version(s). Restoring writes that ' +
        'state forward as a new version, so where you are now stays reachable — ' +
        'nothing in this list is ever lost.</p>' +
        '<div class="od-vers">' + (rows || "<p>No history yet.</p>") + "</div>",
        null, "versions");
      panel.querySelectorAll(".od-ver-go").forEach((b) => {
        b.onclick = () => post("/api/restore", { id: b.dataset.id }).then((r) => {
          toast(r.ok ? "Restored — now " + r.label : (r.error || "Could not restore"),
            r.ok ? "ok" : "err");
          if (r.ok) versionsPanel();
        });
      });
    });
  }

  /* ----- design tokens ----- */
  function tokensPanel() {
    post("/api/tokens").then((res) => {
      if (res.error) { toast(res.error, "err"); return; }
      const rows = res.tokens.map((t, i) =>
        '<div class="od-tok">' +
          '<code>' + t.name + "</code>" +
          (t.kind === "color"
            ? '<input type="color" data-i="' + i + '" class="od-swatch" value="' +
              (/^#[0-9a-f]{6}$/i.test(t.value) ? t.value : "#888888") + '">'
            : "") +
          '<input class="od-val" data-i="' + i + '" value="' +
            t.value.replace(/"/g, "&quot;") + '">' +
        "</div>").join("");
      openPanel("Design tokens",
        '<p class="od-note">Editing a token restyles every page that uses it. ' +
        'This is offered instead of per-element styling on purpose: a one-off ' +
        'inline style would drift from the design system, a token cannot.</p>' +
        '<div class="od-toks">' + rows + "</div>", null, "tokens");
      const commit = (i, value) => {
        // paint it immediately; the rebuild that follows makes it permanent
        document.documentElement.style.setProperty(res.tokens[i].name, value);
        const fw = frameWin();
        if (fw) {
          try {
            fw.document.documentElement.style.setProperty(
              res.tokens[i].name, value);
          } catch (e) { /* the rebuild reload will carry it */ }
        }
        return post("/api/token-set", { name: res.tokens[i].name, value: value })
          .then((r) => r.error ? toast(r.error, "err")
            : toast(res.tokens[i].name + " → " + value, "ok"));
      };
      panel.querySelectorAll(".od-swatch").forEach((sw) => {
        sw.onchange = () => {
          const box = panel.querySelector('.od-val[data-i="' + sw.dataset.i + '"]');
          box.value = sw.value;
          commit(+sw.dataset.i, sw.value);
        };
      });
      panel.querySelectorAll(".od-val").forEach((inp) => {
        inp.onchange = () => commit(+inp.dataset.i, inp.value.trim());
      });
    });
  }

  /* ----- site constants ----- */
  function sitePanel() {
    post("/api/constants").then((res) => {
      if (res.error) { toast(res.error, "err"); return; }
      const mirrored = res.mirrored || [];
      const rows = Object.keys(res.values).map((n) =>
        mirrored.indexOf(n) !== -1
          ? '<label class="od-f"><span>' + n + "</span>" +
            '<input value="mirrors another constant" disabled></label>'
          : field(n, "od-c-" + n, res.values[n] || "")).join("");
      openPanel("Site details",
        '<p class="od-note">The booking, phone and WhatsApp targets used by ' +
        'every CTA, plus the medical reviewer byline. These are the ' +
        'placeholders the clinic still has to confirm.</p>' + rows +
        '<div class="od-acts"><button id="od-save" class="od-primary">Save all</button></div>',
        null, "site");
      panel.querySelector("#od-save").onclick = () => {
        const set = {};
        Object.keys(res.values).forEach((n) => {
          const el = panel.querySelector("#od-c-" + n);
          if (el && !el.disabled) set[n] = el.value.trim();
        });
        post("/api/constants", { set: set })
          .then((r) => { if (saved(r, "Site details saved")) closePanel(); });
      };
    });
  }

  /* ---------- text editing ---------- */
  function begin(el, ev) {
    editing = el;
    original = el.innerHTML;
    el.classList.add("od-editing");
    el.setAttribute("contenteditable",
      el.childElementCount === 0 ? "plaintext-only" : "true");
    el.setAttribute("spellcheck", "true");
    hl.hidden = true;
    el.focus();
    if (ev) placeCaret(ev.clientX, ev.clientY);
  }

  function placeCaret(x, y) {
    let range = null;
    if (document.caretPositionFromPoint) {
      const p = document.caretPositionFromPoint(x, y);
      if (p) { range = document.createRange(); range.setStart(p.offsetNode, p.offset); }
    } else if (document.caretRangeFromPoint) {
      range = document.caretRangeFromPoint(x, y);
    }
    if (!range) return;
    range.collapse(true);
    const sel = getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }

  function finish(save) {
    if (!editing) return;
    const el = editing;
    editing = null;
    el.removeAttribute("contenteditable");
    el.removeAttribute("spellcheck");
    el.classList.remove("od-editing");
    if (!save) { el.innerHTML = original; return; }
    const clean = sanitize(el);
    if (clean === original) return;
    el.innerHTML = clean;
    sendText(el, original, clean, false);
  }

  // contenteditable smuggles in spans and style attributes; reduce the result to
  // the same small vocabulary the source files use
  function sanitize(el) {
    const box = el.cloneNode(true);
    box.querySelectorAll("*").forEach((n) => {
      if (INLINE.has(n.tagName)) {
        [...n.attributes].forEach((a) => n.removeAttribute(a.name));
      } else if (n.tagName === "A") {
        const href = n.getAttribute("href");
        [...n.attributes].forEach((a) => n.removeAttribute(a.name));
        if (href) n.setAttribute("href", href);
      } else {
        n.replaceWith(...n.childNodes);
      }
    });
    return box.innerHTML.replace(/&nbsp;/g, " ").trim();
  }

  const textOf = (html) => {
    const d = document.createElement("div");
    d.innerHTML = html;
    return d.textContent;
  };

  function sendText(el, oldHTML, newHTML, all) {
    const body = {
      slug: slug, addr: addr(el) || null, all: all,
      oldHTML: oldHTML, oldText: textOf(oldHTML),
      newHTML: newHTML, newText: textOf(newHTML),
    };
    toast("Saving…");
    post("/api/edit", body).then((res) => {
      if (res.ok) { saved(res); return; }
      if (res.ambiguous) {
        toast("This text appears in " + res.ambiguous + " places:\n" +
          res.locations.join(", "), "",
          [{ label: "Change all " + res.ambiguous,
             fn: () => sendText(el, oldHTML, newHTML, true) },
           { label: "Cancel", fn: () => { el.innerHTML = oldHTML; } }]);
        return;
      }
      el.innerHTML = oldHTML;
      toast(res.error || "Unknown error", "err");
    }).catch((e) => {
      el.innerHTML = oldHTML;
      toast("Editor server unreachable: " + e, "err");
    });
  }

  function locate(el) {
    const html = el.innerHTML;
    post("/api/locate", { slug: slug, addr: addr(el) || addr(el, "img") ||
      addr(el, "link") || null, oldHTML: html, oldText: textOf(html) })
      .then((res) => {
        if (res.error) { toast(res.error, "err"); return; }
        const first = res.locations[0];
        openInCode(first.file, first.line);
        toast("Opened " + first.file + ":" + first.line + " in VS Code" +
          (res.locations.length > 1 ? " (of " + res.locations.length + " matches)" : ""));
      });
  }

  /* ---------- device preview ---------- */
  // Ported from Open Design's FileViewer: the page loads into an iframe laid
  // out at TRUE device pixels and only visually scaled to fit (never up), so
  // media queries, vw units and innerWidth are all honest and scrolling works
  // like on the real device. Three layers, exactly theirs: a scrolling stage,
  // a clip sized at scaled pixels (the bezel), and a shell at device pixels
  // carrying transform: scale(). The widths are not theirs though — they are
  // the widths verify.py actually tests, because those are where this
  // stylesheet makes its decisions.
  const DEVICES = [["Phone", 390, 844], ["Tablet", 768, 1024],
    ["Laptop", 1040, 800], ["Wide", 1240, 800], ["Desktop", 1440, 900]];
  const devmenu = $("#od-devmenu"), devBtn = $("#od-device");
  let device = null, stage = null, frame = null;

  const frameWin = () => {
    try { return frame && frame.contentWindow; } catch (e) { return null; }
  };

  function frameReload() {
    const fw = frameWin();
    if (!fw) return;
    // The frame's own overlay saves its scroll and open panel before
    // reloading; a bare reload is the fallback if it isn't ready yet.
    try { fw.__odApi ? fw.__odApi.reload() : fw.location.reload(); }
    catch (e) { frame.src = frame.src; }
  }

  const paintDevice = () => {
    devBtn.textContent = device ? "⛶ " + device.name : "⛶ Screen";
    devBtn.classList.toggle("on", !!device);
  };

  function layoutStage() {
    if (!device || !stage) return;
    const w = device.rot ? device.h : device.w;
    const h = device.rot ? device.w : device.h;
    // Open Design's zoom model: an auto "fit" that never upscales, and
    // discrete manual levels. Unlike theirs, a manual level may exceed fit —
    // the stage scrolls, which is what you want when reading 390px small
    // print on a laptop.
    const fit = Math.max(.3, Math.min(1, (innerWidth - 48) / w,
                                         (innerHeight - 128) / h));
    const s = (!device.zoom || device.zoom === "fit")
      ? fit : (+device.zoom) / 100;
    stage.style.setProperty("--od-vw", w + "px");
    stage.style.setProperty("--od-vh", h + "px");
    stage.style.setProperty("--od-scale", s);
    $("#od-stage-label").textContent = device.name + " · " + w + " × " + h +
      " · " + Math.round(s * 100) + "%";
  }

  // verify.py's most important measurement, live: content wider than the
  // viewport means the page scrolls sideways on this device.
  function measureFrame() {
    const chip = $("#od-stage-warn"), fw = frameWin();
    if (!chip || !fw) return;
    setTimeout(() => {
      try {
        const sw = fw.document.documentElement.scrollWidth;
        const over = sw > fw.innerWidth + 1;
        chip.hidden = !over;
        if (over) chip.textContent =
          "⚠ scrolls sideways — content is " + sw + "px wide";
      } catch (e) { /* frame was mid-navigation; next load re-measures */ }
    }, 450);
  }

  function enterDevice(d) {
    if (editing) finish(false);
    device = d;
    sessionStorage.setItem("odDevice", JSON.stringify(d));
    document.documentElement.classList.add("od-device-on");
    hl.hidden = true;
    sectools.hidden = true;
    if (!stage) {
      stage = document.createElement("div");
      stage.id = "od-stage";
      stage.innerHTML =
        '<div id="od-stage-head"><span id="od-stage-label"></span>' +
          '<span id="od-stage-page"></span>' +
          '<span id="od-stage-warn" hidden></span>' +
          '<select id="od-zoom" title="Zoom">' +
            '<option value="fit">Fit</option>' +
            ["50", "75", "100", "125", "150", "200"].map((z) =>
              '<option value="' + z + '">' + z + "%</option>").join("") +
          "</select>" +
          '<button id="od-rotate" type="button" title="Rotate device">⟳</button>' +
          '<button id="od-exit" type="button" title="Back to full width">✕</button>' +
        '</div>' +
        '<div id="od-clip"><div id="od-shell">' +
          '<iframe id="od-frame" title="device preview"></iframe></div></div>';
      ui.appendChild(stage);
      frame = stage.querySelector("#od-frame");
      frame.src = location.pathname + location.search;
      stage.querySelector("#od-rotate").onclick = () => {
        device.rot = !device.rot;
        enterDevice(device);          // resize only — the frame never reloads
      };
      stage.querySelector("#od-zoom").onchange = (ev) => {
        device.zoom = ev.target.value;
        sessionStorage.setItem("odDevice", JSON.stringify(device));
        layoutStage();
      };
      stage.querySelector("#od-exit").onclick = exitDevice;
      if (d.zoom) stage.querySelector("#od-zoom").value = d.zoom;
      frame.addEventListener("load", () => {
        const fw = frameWin();
        try {
          $("#od-stage-page").textContent =
            fw.location.pathname.replace(/^\/|\.html$/g, "") || "index";
          if (fw.__odApi) fw.__odApi.setMode(mode);
        } catch (e) { /* noop */ }
        measureFrame();
      });
    }
    stage.classList.toggle("od-stage-phone", Math.min(d.w, d.h) < 500);
    layoutStage();
    measureFrame();
    paintDevice();
  }

  function exitDevice() {
    device = null;
    sessionStorage.removeItem("odDevice");
    // The host page ignored every rebuild while the frame handled them, so
    // its own document may be stale — reload rather than reveal it.
    location.reload();
  }

  function toggleDevMenu() {
    if (!devmenu.hidden) { devmenu.hidden = true; return; }
    devmenu.innerHTML = DEVICES.map((d, i) =>
      '<button data-i="' + i + '"' +
        (device && device.name === d[0] ? ' class="on"' : "") + ">" + d[0] +
        " <span>" + d[1] + " × " + d[2] + "</span></button>").join("") +
      '<button data-i="-1"' + (device ? "" : ' class="on"') +
        '>Full width <span>this window</span></button>';
    devmenu.hidden = false;
    devmenu.querySelectorAll("button").forEach((b) => {
      b.onclick = () => {
        devmenu.hidden = true;
        const i = +b.dataset.i;
        if (i < 0) { if (device) exitDevice(); return; }
        enterDevice({ name: DEVICES[i][0], w: DEVICES[i][1], h: DEVICES[i][2],
          rot: device && device.name === DEVICES[i][0] ? device.rot : false });
      };
    });
  }

  /* ---------- pages ---------- */
  function pagesPanel() {
    post("/api/inspect", { slug: slug, wantSlugs: true }).then((res) => {
      if (res.error) { toast(res.error, "err"); return; }
      let current = slug;
      const fw = frameWin();
      if (device && fw) {
        try {
          current = fw.location.pathname.replace(/^\/|\.html$/g, "") || "index";
        } catch (e) { /* noop */ }
      }
      const rows = (res.slugs || []).map((s) =>
        '<button class="od-page' + (s === current ? " on" : "") +
        '" data-s="' + esc(s) + '">' + esc(s) + "</button>").join("");
      openPanel("Pages",
        '<p class="od-note">' + (res.slugs || []).length + " pages. " +
          (device ? "Opens inside the device preview." : "") + "</p>" +
        '<div class="od-pages">' + rows + "</div>", null, "pages");
      panel.querySelectorAll(".od-page").forEach((b) => {
        b.onclick = () => {
          const url = "/" + (b.dataset.s === "index" ? "" : b.dataset.s + ".html");
          if (device && frame) { frame.src = url; closePanel(); }
          else location.href = url;
        };
      });
    });
  }

  /* ---------- feedback for the agent ----------
   * Two gestures, one destination. Right-click any element to copy a reference
   * to it — page, data address, source file and line — straight into a chat.
   * Note pins "change this to that" to an element; the ⚑ Agent panel turns
   * every pinned note into a single prompt covering all of them.
   *
   * Mark and Shot used to live here. Drawing on the page only fed the
   * screenshot, and the screenshot only recreated something the user can
   * capture themselves. Neither could say which value in which file a pixel
   * came from, which is the one thing the agent cannot work out on its own. */
  let noting = false;
  const noteBtn = $("#od-notebtn"), fbBtn = $("#od-fbbtn");

  const noteCount = (n) => {
    fbBtn.textContent = n ? "⚑ Agent (" + n + ")" : "⚑ Agent";
    fbBtn.classList.toggle("has", !!n);
  };

  /* Clipboard, three ways down.
   * VS Code's Simple Browser — the pane this editor usually runs in — refuses
   * navigator.clipboard.writeText outright. execCommand("copy") over a
   * selected textarea still works there. When even that is blocked the text is
   * left on screen, selected, for a manual Ctrl+C: a copy button that silently
   * copies nothing is worse than one that hands you the text. */
  function copyText(text, host, onOk) {
    const done = () => { if (onOk) onOk(true); };
    const fallback = () => {
      let ta = host.querySelector(".od-copybox");
      if (!ta) {
        ta = document.createElement("textarea");
        ta.className = "od-ta od-copybox";
        ta.rows = Math.min(14, text.split("\n").length + 1);
        ta.readOnly = true;
        host.appendChild(ta);
      }
      ta.value = text;
      ta.focus();
      ta.select();
      let ok = false;
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
      // The box exists to be copied from by hand. Once execCommand has taken
      // the text it has no job left, and leaving it up next to a "Copied"
      // toast reads as though the copy did not happen.
      if (ok) { ta.remove(); done(); } else if (onOk) onOk(false);
    };
    if (navigator.clipboard && navigator.clipboard.writeText)
      navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  }

  function fbPanel() {
    post("/api/notes", {}).then((res) => {
      if (!res.ok) return;
      noteCount(res.count);
      const rows = res.notes.map((n, i) => {
        const where = n.addr || n.sel || "";
        const src = n.file ? n.file + ":" + n.line : "";
        return '<div class="od-fb-item" data-id="' + esc(n.id) + '">' +
          '<div class="od-fb-meta"><b>' + (i + 1) + "</b> " + esc(n.slug) +
          " · <code>" + esc(where) + "</code>" +
          (src ? ' · <code>' + esc(src) + "</code>" : "") +
          " · " + esc(n.ts) + "</div>" +
          '<div class="od-ver-what">' + esc(n.text) + "</div>" +
          '<div class="od-acts"><button class="od-fb-res" type="button">' +
          "Resolve</button></div></div>";
      }).join("");
      openPanel("Queued for your agent",
        (res.count
          ? '<p class="od-note">' + res.count + " pinned change(s). Copy the " +
            "prompt and paste it into your agent chat — it names the page, the " +
            "data address and the source line for every one.<br>" +
            "<b>Claude Code</b> also sees them automatically with your next " +
            "prompt.</p>" +
            '<div class="od-acts"><button id="od-fb-copy" class="od-primary" ' +
            'type="button">Copy prompt for all ' + res.count + "</button>" +
            '<button id="od-fb-show" type="button">Show</button></div>'
          : '<p class="od-note">Nothing pinned. Press <b>Note</b>, then click ' +
            "any element to say what should change there. Right-click any " +
            "element to copy a reference to it without pinning anything.</p>") +
        rows, null, "feedback");
      const copyBtn = panel.querySelector("#od-fb-copy");
      if (copyBtn) {
        copyBtn.onclick = () => {
          const host = copyBtn.parentElement;
          copyText(res.prompt, host, (ok) => {
            copyBtn.textContent = ok ? "Copied — paste it into the chat"
              : "Select the text below and press Ctrl+C";
            setTimeout(() => {
              copyBtn.textContent = "Copy prompt for all " + res.count;
            }, 3000);
          });
        };
        panel.querySelector("#od-fb-show").onclick = (e) => {
          const host = e.target.parentElement;
          let ta = host.querySelector(".od-copybox");
          if (ta) { ta.remove(); return; }
          ta = document.createElement("textarea");
          ta.className = "od-ta od-copybox";
          ta.rows = 14;
          ta.readOnly = true;
          ta.value = res.prompt;
          host.appendChild(ta);
        };
      }
      panel.querySelectorAll(".od-fb-res").forEach((b) => {
        b.onclick = () =>
          post("/api/note-done",
            { id: b.closest(".od-fb-item").dataset.id }).then((r2) => {
            if (r2.error) { toast(r2.error, "err"); return; }
            renderPins();
            fbPanel();
          });
      });
    });
  }
  fbBtn.onclick = fbPanel;

  /* Right-click → a reference to this element, on the clipboard.
   * Left-click is already taken by editing, and this has to work whether or
   * not edit mode is on: wanting to talk to the agent about an element is not
   * the same as wanting to change it here. */
  function refPanel(el) {
    const a = addr(el) || addr(el, "img") || addr(el, "link") || "";
    post("/api/ref", { slug: slug, addr: a, sel: cssPath(el),
      kind: kindOf(el),
      context: (el.textContent || "").trim().slice(0, 120) }).then((res) => {
      if (res.error) { toast(res.error, "err"); return; }
      openPanel("Reference for your agent",
        '<p class="od-note">Paste this into the chat. It names the page, the ' +
        "data address and the source line, so the agent does not have to " +
        "search for what you meant.</p>" +
        '<pre class="od-ref">' + esc(res.ref) + "</pre>" +
        '<div class="od-acts"><button id="od-ref-copy" class="od-primary" ' +
        'type="button">Copy</button>' +
        (res.target && res.target.file
          ? '<button id="od-ref-open" type="button">Open in code</button>'
          : "") + "</div>", el, "note");
      const btn = panel.querySelector("#od-ref-copy");
      btn.onclick = () => copyText(res.ref, btn.parentElement, (ok) => {
        btn.textContent = ok ? "Copied" : "Select below, Ctrl+C";
        setTimeout(() => { btn.textContent = "Copy"; }, 2500);
      });
      const open = panel.querySelector("#od-ref-open");
      if (open) open.onclick = () =>
        openInCode(res.target.file, res.target.line);
      // Copy on open, so the common case is right-click then paste. The panel
      // is the fallback for when the browser refuses the clipboard.
      copyText(res.ref, panel, (ok) => {
        if (ok) toast("Reference copied — paste it into the chat.", "ok");
      });
    });
  }

  document.addEventListener("contextmenu", (e) => {
    if (ui.contains(e.target)) return;
    const el = pick(e.target) || (e.target.nodeType === 1 ? e.target : null);
    if (!el) return;
    e.preventDefault();
    refPanel(el);
  });

  function cssPath(el) {
    const parts = [];
    for (let n = el; n && n.nodeType === 1 && parts.length < 5
         && n !== document.body; n = n.parentElement) {
      let bit = n.tagName.toLowerCase();
      const cls = (typeof n.className === "string" &&
        n.className.trim().split(/\s+/)[0]) || "";
      if (cls) bit += "." + cls;
      const sibs = n.parentElement
        ? [...n.parentElement.children].filter((c) => c.tagName === n.tagName)
        : [];
      if (sibs.length > 1) bit += ":nth-of-type(" + (sibs.indexOf(n) + 1) + ")";
      parts.unshift(bit);
      if (n.id) { parts[0] = "#" + n.id; break; }
    }
    return parts.join(" > ");
  }

  function notePanel(el) {
    const a = addr(el) || addr(el, "img") || addr(el, "link") || "";
    openPanel("What should change here?",
      '<p class="od-note">Pinned to <code>' + esc(a || cssPath(el)) +
      "</code></p>" +
      '<textarea id="od-note-text" class="od-ta" rows="4" ' +
      'placeholder="e.g. shorten this to one line and drop the dash"></textarea>' +
      '<div class="od-acts"><button id="od-note-save" class="od-primary">' +
      "Pin it</button></div>" +
      '<p class="od-note">Pin as many as you like, then <b>⚑ Agent</b> turns ' +
      "them into one prompt — every element and its change together.</p>",
      el, "note");
    panel.querySelector("#od-note-text").focus();
    panel.querySelector("#od-note-save").onclick = () => {
      post("/api/note", { slug: slug, addr: a, sel: cssPath(el),
        kind: kindOf(el),
        context: (el.textContent || "").trim().slice(0, 120),
        text: panel.querySelector("#od-note-text").value })
        .then((res) => {
          if (res.error) { toast(res.error, "err"); return; }
          noteCount(res.open);
          closePanel();
          renderPins();
          const where = res.note && res.note.file
            ? " → " + res.note.file + ":" + res.note.line : "";
          toast("Pinned" + where + " · " + res.open + " waiting. ⚑ Agent to "
            + "copy the prompt.", "ok");
        });
    };
  }

  function renderPins() {
    ui.querySelectorAll(".od-pin").forEach((p) => p.remove());
    // Every open note, not just this page's: the pin number has to be the
    // number the copied prompt gives that item, and the prompt is numbered
    // across the whole site. Asking for one page's notes made pin 1 here
    // item 4 in the prompt, which is a confusing way to discuss a change.
    post("/api/notes", {}).then((res) => {
      if (!res.ok) return;
      noteCount(res.count);
      res.notes.forEach((n, i) => {
        if (n.slug !== slug) return;
        let el = null;
        if (n.addr) {
          el = document.querySelector(
            '[data-od="' + n.addr + '"],[data-od-img="' + n.addr +
            '"],[data-od-link="' + n.addr + '"]');
        }
        if (!el && n.sel) { try { el = document.querySelector(n.sel); } catch (e) {} }
        if (!el) return;
        const r = el.getBoundingClientRect();
        const pin = document.createElement("button");
        pin.className = "od-pin";
        pin.textContent = i + 1;
        pin.style.left = (r.right + scrollX - 9) + "px";
        pin.style.top = (r.top + scrollY - 9) + "px";
        pin.onclick = () => {
          openPanel("Pinned change " + (i + 1),
            '<p class="od-note">' + esc(n.ts) +
            (n.file ? " · <code>" + esc(n.file) + ":" + esc(n.line) + "</code>"
              : "") + "</p>" +
            '<div class="od-ver-what">' + esc(n.text) + "</div>" +
            '<div class="od-acts"><button id="od-note-res" class="od-primary">' +
            "Resolve</button>" +
            (n.file ? '<button id="od-note-open" type="button">Open in code' +
              "</button>" : "") + "</div>", el, "note");
          panel.querySelector("#od-note-res").onclick = () =>
            post("/api/note-done", { id: n.id }).then((r2) => {
              if (r2.error) { toast(r2.error, "err"); return; }
              noteCount(r2.open);
              closePanel();
              renderPins();
            });
          const open = panel.querySelector("#od-note-open");
          if (open) open.onclick = () => openInCode(n.file, n.line);
        };
        ui.appendChild(pin);
      });
    });
  }

  noteBtn.onclick = () => {
    noting = noteBtn.classList.toggle("on");
    if (noting) toast("Click any element to say what should change there. Esc to stop.");
  };

  // Registered before the edit-mode click handler, so a note click never
  // falls through into text editing.
  document.addEventListener("click", (e) => {
    if (!noting || ui.contains(e.target)) return;
    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();
    notePanel(pick(e.target) || e.target);
  }, true);

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && noting) {
      noting = false;
      noteBtn.classList.remove("on");
    }
  }, true);

  /* ---------- events ---------- */
  toggle.onclick = () => {
    mode = !mode;
    sessionStorage.setItem("odEditMode", mode ? "1" : "0");
    if (!mode) finish(false);
    paintToggle();
    const fw = frameWin();
    if (fw && fw.__odApi) {
      try { fw.__odApi.setMode(mode); } catch (e) { /* noop */ }
    }
  };
  $("#od-pages").onclick = pagesPanel;
  devBtn.onclick = toggleDevMenu;
  paintDevice();
  addEventListener("resize", layoutStage);
  document.addEventListener("click", (e) => {
    if (!devmenu.hidden && !devmenu.contains(e.target) && e.target !== devBtn)
      devmenu.hidden = true;
  });
  $("#od-tokens").onclick = () => { if (!mode) toggle.click(); tokensPanel(); };
  $("#od-site").onclick = () => { if (!mode) toggle.click(); sitePanel(); };
  $("#od-undo").onclick = undo;
  $("#od-redo").onclick = redo;
  $("#od-versions").onclick = versionsPanel;
  post("/api/history").then(showHistory);

  document.addEventListener("mousemove", (e) => {
    if (!mode || editing || ui.contains(e.target)) return;
    highlight(pick(e.target));
    const sec = e.target.closest ? e.target.closest("[data-od-sec]") : null;
    if (sec) showSectionTools(sec);
    else if (hoverSection && !sectools.contains(e.target)) {
      hoverSection = null;
      sectools.hidden = true;
    }
  });

  document.addEventListener("click", (e) => {
    if (!mode || ui.contains(e.target)) return;
    const el = pick(e.target);
    if (e.target.closest("a") || el) { e.preventDefault(); e.stopPropagation(); }
    if (!el || el === editing) return;
    if (editing) finish(true);
    if (e.altKey) { locate(el); return; }
    const k = kindOf(el);
    if (k === "image") { imagePanel(el); return; }
    // Open Design opens its inspector on ANY anchor, inferred from the tag.
    // Ours used to need a data address, which meant every nav and footer link
    // fell through to text editing and could not be retargeted at all.
    if (k === "link") { linkPanel(el); return; }
    begin(el, e);
  }, true);

  document.addEventListener("keydown", (e) => {
    if (editing) {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); finish(true); }
      if (e.key === "Escape") finish(false);
      return;
    }
    if (e.key === "Escape" && !devmenu.hidden) { devmenu.hidden = true; return; }
    if (!mode) return;
    if (e.key === "Escape") closePanel();
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "z" &&
        !/^(INPUT|TEXTAREA)$/.test(document.activeElement.tagName)) {
      e.preventDefault();
      (e.shiftKey ? redo : undo)();
    }
  }, true);

  // Losing focus is NOT a save. Clicking the toolbar, alt-tabbing to VS Code or
  // opening devtools would otherwise commit a half-typed value and rebuild the
  // site. The session stays open until Enter, Esc, or another target is picked.
  document.addEventListener("focusout", (e) => {
    if (editing && e.target === editing) setTimeout(() => {
      if (editing && document.activeElement !== editing) {
        editing.classList.add("od-pending");
        toast("Still editing — press Enter to save or Esc to discard.");
      }
    }, 0);
  });

  /* ---------- live reload ---------- */
  const reload = () => {
    sessionStorage.setItem("odScroll", String(scrollY));
    if (!panel.hidden && panel.dataset.kind)
      sessionStorage.setItem("odPanel", panel.dataset.kind);
    location.reload();
  };

  if (framed) {
    // The frame owns no reload stream — the host page holds the single SSE
    // connection and reaches in here when a rebuild lands. What the frame
    // offers back is exactly what the host needs: a reload that preserves
    // scroll and panel state, and a switch for edit mode.
    window.__odApi = {
      reload: reload,
      editing: () => !!editing,
      setMode: (m) => {
        if (mode === !!m) return;
        if (!m && editing) finish(false);
        mode = !!m;
        paintToggle();
      },
    };
  } else {
    const es = new EventSource("/api/events");
    es.onmessage = (ev) => {
      const d = JSON.parse(ev.data);
      if (ver === null) { ver = d.version; return; }
      if (d.version === ver) return;
      ver = d.version;
      if (d.error) { toast("Build failed:\n" + d.error, "err"); return; }
      if (device && frame) {
        // Edits made inside the device frame come back through here: reload
        // the frame, not the (hidden, deliberately stale) host document — and
        // keep the host's Undo/Redo buttons truthful, since the responses
        // that carried the new history state went to the frame.
        post("/api/history").then(showHistory);
        const fw = frameWin();
        if (fw && fw.__odApi && fw.__odApi.editing && fw.__odApi.editing()) {
          // Same rule as below: never reload over someone's typing.
          toast("The site was rebuilt while you were editing in the preview — "
            + "finish or press Esc, then reload.", "",
            [{ label: "Reload preview", fn: frameReload }]);
          return;
        }
        frameReload();
        return;
      }
      // Never reload over someone's typing. A rebuild triggered by the agent
      // editing code, or by a token change, would otherwise wipe an in-progress
      // edit with no warning and no way to get the text back.
      if (editing) {
        toast("The page was rebuilt while you were editing. Your text is still "
          + "here — finish or press Esc, then reload.", "",
          [{ label: "Reload now", fn: () => { finish(false); reload(); } }]);
        return;
      }
      setTimeout(reload, toastBox.hidden ? 0 : 600);
    };
  }

  // The workspace shell (hub.py) embeds this editor in a cross-origin iframe
  // (different port), where it deliberately keeps its full chrome — but the
  // shell's page list still needs to know which page is showing. postMessage
  // is the only channel that crosses that origin line; announcing the slug
  // costs nothing when nobody is listening.
  if (!framed && window.parent !== window) {
    try {
      window.parent.postMessage(
        { od: "page", slug: slug, title: document.title }, "*");
    } catch (e) { /* noop */ }
  }

  // A chosen device outlives reloads: the whole point of previewing at 390px
  // is to keep working there while edits rebuild the site underneath.
  if (!framed) {
    const savedDev = sessionStorage.getItem("odDevice");
    if (savedDev) {
      try { enterDevice(JSON.parse(savedDev)); }
      catch (e) { sessionStorage.removeItem("odDevice"); }
    }
  }

  const reopen = sessionStorage.getItem("odPanel");
  if (reopen) {
    sessionStorage.removeItem("odPanel");
    setTimeout(() => { if (reopen === "tokens") tokensPanel();
                       else if (reopen === "site") sitePanel(); }, 60);
  }

  const savedScroll = sessionStorage.getItem("odScroll");
  if (savedScroll !== null) {
    sessionStorage.removeItem("odScroll");
    requestAnimationFrame(() => scrollTo(0, +savedScroll));
  }
  paintToggle();
  renderPins();
})();
