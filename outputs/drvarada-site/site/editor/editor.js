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
      '<button id="od-tokens" type="button" title="Design tokens">Tokens</button>' +
      '<button id="od-site" type="button" title="Practo links, phone, WhatsApp">Site</button>' +
      '<button id="od-undo" type="button" title="Undo (Ctrl+Z)">Undo</button>' +
      '<button id="od-redo" type="button" title="Redo (Ctrl+Shift+Z)">Redo</button>' +
    '</div>' +
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
  function linkPanel(el) {
    target = el;
    const a = addr(el, "link");
    const href = el.getAttribute("href") || "";
    post("/api/inspect", { slug: slug, addr: a, wantSlugs: true }).then((res) => {
      const slugs = res.slugs || [];
      openPanel("Link",
        field("Label", "od-label", el.textContent.trim()) +
        field("Destination", "od-href", href,
          "A page slug for an internal link, or a full https:// URL.") +
        '<datalist id="od-slugs">' +
          slugs.map((s) => '<option value="' + s + '">').join("") + "</datalist>" +
        '<p class="od-note">Practo, phone and WhatsApp targets are shared ' +
          'constants — changing one here updates every CTA on the site. Use ' +
          '<b>Site</b> in the toolbar to edit them as a form.</p>' +
        '<div class="od-acts"><button id="od-save" class="od-primary">Save link</button></div>',
        el);
      panel.querySelector("#od-href").setAttribute("list", "od-slugs");
      panel.querySelector("#od-save").onclick = () =>
        post("/api/link", { slug: slug, addr: a, oldHref: href,
          href: panel.querySelector("#od-href").value.trim(),
          label: panel.querySelector("#od-label").value.trim() })
          .then((r) => { if (saved(r, "Link saved")) closePanel(); });
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

  /* ---------- events ---------- */
  toggle.onclick = () => {
    mode = !mode;
    sessionStorage.setItem("odEditMode", mode ? "1" : "0");
    if (!mode) finish(false);
    paintToggle();
  };
  $("#od-tokens").onclick = () => { if (!mode) toggle.click(); tokensPanel(); };
  $("#od-site").onclick = () => { if (!mode) toggle.click(); sitePanel(); };
  $("#od-undo").onclick = undo;
  $("#od-redo").onclick = redo;
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
    if (k === "link" && addr(el, "link")) { linkPanel(el); return; }
    begin(el, e);
  }, true);

  document.addEventListener("keydown", (e) => {
    if (editing) {
      if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); finish(true); }
      if (e.key === "Escape") finish(false);
      return;
    }
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

  const es = new EventSource("/api/events");
  es.onmessage = (ev) => {
    const d = JSON.parse(ev.data);
    if (ver === null) { ver = d.version; return; }
    if (d.version === ver) return;
    ver = d.version;
    if (d.error) { toast("Build failed:\n" + d.error, "err"); return; }
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
})();
