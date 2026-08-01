"""Version history for the site — a port of Open Design's project file versions.

Ported from `apps/daemon/src/project-file-versions.ts` in the Open Design repo
(Apache-2.0). What is taken from there is the *model*, which is the part worth
copying:

  APPEND-ONLY.        Versions are numbered from 1 and never renumbered,
                      reordered or deleted. There is no branch and no rewrite.

  RESTORE IS A WRITE. Going back to version 3 does not rewind the timeline — it
                      writes v3's content and appends it as a NEW version,
                      carrying `restore_from` and the label
                      "Version 9 · restored from v3" (upstream `nextLabel`).
                      This is the whole reason the model is safe: there is no
                      operation that can lose a state you have seen.

  SEED THE CURRENT.   `ensure_current()` captures whatever is on disk as v1 when
                      the store is empty (upstream `ensureCurrentProjectFileVersion`).
                      Without it, a file edited outside the editor has its
                      pre-history silently replaced by the first edit made
                      inside it.

  DEFENSIVE READS.    A manifest entry that does not parse is skipped, not
                      thrown on (upstream `normalizeManifestEntry` returns
                      null). History is a convenience; a corrupt journal must
                      never stop someone editing their site.

Two deliberate differences from upstream:

  * Upstream versions ONE html artifact. An edit here can touch several source
    files at once — a copy change plus a token change plus an upload — so the
    unit is the whole tracked set, not a file. Entries therefore list files.
  * Upstream stores a full copy of the artifact per version. Our tracked set is
    ~540 KB, so 200 full copies would be 100 MB for a site where most edits
    touch one file. Content is stored in a content-addressed blob store
    instead: unchanged files cost nothing and `read()` is still a direct
    lookup, with no chain of diffs to replay.
"""

from __future__ import annotations

import hashlib
import json
import re
import threading
import time
import uuid
from pathlib import Path

SCHEMA_VERSION = 1
ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
SOURCES = ("edit", "manual", "restore", "seed")
MAX_ENTRIES = 300           # ~a month of heavy editing; blobs are shared


class VersionError(Exception):
    pass


class Versions:
    """The site's version timeline, persisted under `.versions/`.

        .versions/manifest.json      the timeline
        .versions/blobs/<sha256>     file contents, shared across versions
    """

    def __init__(self, root: Path, store: Path):
        self.root = root                 # the site directory paths are relative to
        self.store = store
        self.blobs = store / "blobs"
        self.manifest = store / "manifest.json"
        self._lock = threading.RLock()
        self.entries: list[dict] = []
        self.cursor = -1                 # index of the entry whose content is on disk
        self._load()

    # ── manifest ─────────────────────────────────────────────────────────
    def _load(self) -> None:
        try:
            raw = json.loads(self.manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.entries, self.cursor = [], -1
            return
        entries = raw.get("entries") if isinstance(raw, dict) else None
        self.entries = []
        for i, item in enumerate(entries or []):
            norm = self._normalize(item, i)
            if norm:
                self.entries.append(norm)
        cursor = raw.get("cursor") if isinstance(raw, dict) else None
        self.cursor = (cursor if isinstance(cursor, int) and -1 <= cursor < len(self.entries)
                       else len(self.entries) - 1)

    @staticmethod
    def _normalize(raw, index: int) -> dict | None:
        """Coerce one manifest entry, or drop it.

        Upstream returns null for an entry it cannot read rather than raising,
        so one bad record cannot take the whole history down. Same here: this
        file is hand-inspectable and lives in a working tree, so it WILL get
        truncated by a crash or a merge at some point.
        """
        if not isinstance(raw, dict):
            return None
        vid = raw.get("id")
        if not isinstance(vid, str) or not ID_RE.match(vid):
            return None
        files = raw.get("files")
        if not isinstance(files, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in files.items()):
            return None
        version = raw.get("version")
        source = raw.get("source")
        restore_from = raw.get("restore_from")
        parent = raw.get("parent")
        return {
            "id": vid,
            "parent": parent if isinstance(parent, str) and ID_RE.match(parent) else None,
            "version": version if isinstance(version, int) else index + 1,
            "label": (raw["label"] if isinstance(raw.get("label"), str) and raw["label"].strip()
                      else f"Version {version if isinstance(version, int) else index + 1}"),
            "created_at": (raw["created_at"] if isinstance(raw.get("created_at"), (int, float))
                           else time.time()),
            "source": source if source in SOURCES else "edit",
            "prompt": raw["prompt"] if isinstance(raw.get("prompt"), str) else None,
            **({"restore_from": restore_from}
               if isinstance(restore_from, str) and ID_RE.match(restore_from) else {}),
            "files": files,
            "size": raw["size"] if isinstance(raw.get("size"), int) else 0,
        }

    def _save(self) -> None:
        self.store.mkdir(parents=True, exist_ok=True)
        tmp = self.manifest.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({
            "schemaVersion": SCHEMA_VERSION,
            "cursor": self.cursor,
            "entries": self.entries,
        }, indent=1), encoding="utf-8")
        tmp.replace(self.manifest)       # never leave a half-written manifest

    # ── blobs ────────────────────────────────────────────────────────────
    def _put(self, text: str) -> str:
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        path = self.blobs / digest[:2] / digest
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return digest

    def _get(self, digest: str) -> str | None:
        path = self.blobs / digest[:2] / digest
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    # ── the timeline ─────────────────────────────────────────────────────
    def _label(self, version: int, restored: dict | None) -> str:
        """Upstream `nextLabel` — the restore provenance is in the label itself,
        so the timeline reads correctly even with no UI to expand it."""
        if not restored:
            return f"Version {version}"
        return f"Version {version} · restored from v{restored['version']}"

    def _snapshot(self, files: dict[Path, str]) -> tuple[dict[str, str], int]:
        out, size = {}, 0
        for path, text in files.items():
            rel = path.relative_to(self.root).as_posix()
            out[rel] = self._put(text)
            size += len(text.encode("utf-8"))
        return out, size

    def create(self, files: dict[Path, str], *, prompt: str | None = None,
               source: str = "edit", restore_from: str | None = None) -> dict:
        """Append the current state of `files` as a new version."""
        with self._lock:
            restored = self.find(restore_from) if restore_from else None
            version = max((e["version"] for e in self.entries), default=0) + 1
            blobs, size = self._snapshot(files)
            entry = {
                "id": uuid.uuid4().hex,
                # Where this version was made FROM. Upstream has no parent link
                # because it has no undo — every move is a restore. We do have
                # undo, and undo has to follow the lineage rather than the array
                # index, or an edit made after an undo leaves earlier presses of
                # Ctrl+Z walking into a branch the user abandoned.
                "parent": (self.entries[self.cursor]["id"]
                           if 0 <= self.cursor < len(self.entries) else None),
                "version": version,
                "label": self._label(version, restored),
                "created_at": time.time(),
                "source": source if source in SOURCES else "edit",
                "prompt": (prompt or None) and prompt[:120],
                **({"restore_from": restore_from} if restored else {}),
                "files": blobs,
                "size": size,
            }
            self.entries.append(entry)
            self.cursor = len(self.entries) - 1
            self._prune()
            self._save()
            return entry

    def ensure_current(self, files: dict[Path, str]) -> dict | None:
        """Seed v1 from disk when the store is empty, or when disk has drifted.

        Upstream compares the newest stored content with what is on disk and
        only writes when they differ. That second case is the one that matters
        in a git working tree: pull a branch, and the first edit you make would
        otherwise bury the pulled state with no version recording it.
        """
        with self._lock:
            if self.entries and self.cursor >= 0:
                current = self.entries[self.cursor]["files"]
                now, _ = {}, None
                for path, text in files.items():
                    now[path.relative_to(self.root).as_posix()] = hashlib.sha256(
                        text.encode("utf-8")).hexdigest()
                if now == current:
                    return None
            return self.create(files, source="seed",
                               prompt="state found on disk")

    def _prune(self) -> None:
        while len(self.entries) > MAX_ENTRIES:
            gone = self.entries.pop(0)
            self.cursor = max(-1, self.cursor - 1)
            # Re-parent the orphans onto their grandparent. Without this an
            # entry keeps pointing at a version that has been pruned away, and
            # undo silently dead-ends at a link that resolves to nothing.
            for e in self.entries:
                if e.get("parent") == gone["id"]:
                    e["parent"] = gone.get("parent")
        # Blobs are shared, so a blob is only garbage once no entry names it.
        if len(self.entries) % 25 == 0:
            self.gc()

    def gc(self) -> int:
        live = {sha for e in self.entries for sha in e["files"].values()}
        removed = 0
        if not self.blobs.is_dir():
            return 0
        for shard in self.blobs.iterdir():
            if not shard.is_dir():
                continue
            for blob in shard.iterdir():
                if blob.name not in live:
                    blob.unlink(missing_ok=True)
                    removed += 1
            if not any(shard.iterdir()):
                shard.rmdir()
        return removed

    # ── reading ──────────────────────────────────────────────────────────
    def find(self, version_id: str | None) -> dict | None:
        if not version_id:
            return None
        return next((e for e in self.entries if e["id"] == version_id), None)

    def content(self, entry: dict) -> dict[str, str]:
        """Every file's text at that version, keyed by repo-relative path."""
        out = {}
        for rel, digest in entry["files"].items():
            text = self._get(digest)
            if text is None:
                raise VersionError(
                    f"{entry['label']}: the stored copy of {rel} is missing, so "
                    "this version cannot be restored.")
            out[rel] = text
        return out

    def timeline(self, limit: int = 60) -> list[dict]:
        out = []
        for i, e in enumerate(reversed(self.entries[-limit:])):
            idx = len(self.entries) - 1 - i
            out.append({
                "id": e["id"],
                "version": e["version"],
                "label": e["label"],
                "when": time.strftime("%d %b %H:%M", time.localtime(e["created_at"])),
                "source": e["source"],
                "prompt": e["prompt"],
                "files": sorted(e["files"]),
                "size": e["size"],
                "current": idx == self.cursor,
                # "ahead" means: made after where you are standing. Those are
                # still reachable — by redo when they are on this lineage, by
                # restore when they are on a branch you left.
                "ahead": idx > self.cursor,
            })
        return out

    def _index(self, version_id: str | None) -> int:
        return next((i for i, e in enumerate(self.entries)
                     if e["id"] == version_id), -1)

    def _back(self) -> int:
        """The version the current one was made from."""
        if not 0 <= self.cursor < len(self.entries):
            return -1
        return self._index(self.entries[self.cursor].get("parent"))

    def _forward(self) -> int:
        """The newest version made from the current one.

        Newest rather than first: after undoing and editing again, redo should
        offer the work you just did, not the branch you walked away from. Both
        stay in the timeline and both stay reachable from the Versions panel —
        this only decides which one the keyboard reaches.
        """
        if not 0 <= self.cursor < len(self.entries):
            return -1
        here = self.entries[self.cursor]["id"]
        kids = [i for i, e in enumerate(self.entries) if e.get("parent") == here]
        return kids[-1] if kids else -1

    def state(self) -> dict:
        b, f = self._back(), self._forward()
        prev = self.entries[b] if b >= 0 else None
        nxt = self.entries[f] if f >= 0 else None
        return {
            "undo": prev["label"] if prev else None,
            "redo": nxt["label"] if nxt else None,
            "depth": len(self.entries),
            "version": (self.entries[self.cursor]["version"]
                        if 0 <= self.cursor < len(self.entries) else 0),
        }

    # ── moving ───────────────────────────────────────────────────────────
    def step(self, delta: int) -> dict:
        """Undo (-1) / redo (+1): move along the lineage and hand back the content.

        Stepping does NOT append. Upstream has no undo at all — every move is a
        restore — but a keyboard undo that grew the timeline on every press
        would make the timeline useless for its actual job, which is answering
        "what did this page look like on Tuesday".

        It walks parent links rather than array positions. With a flat array,
        editing after an undo leaves the abandoned states sitting between you
        and your earlier work, so the next Ctrl+Z jumps into a branch you
        walked away from. Following the lineage makes undo mean what it says
        while the abandoned branch stays in the timeline, reachable by restore.
        """
        with self._lock:
            target = self._back() if delta < 0 else self._forward()
            if not 0 <= target < len(self.entries):
                return {"error": "Nothing to undo." if delta < 0 else "Nothing to redo."}
            entry = self.entries[target]
            files = self.content(entry)
            self.cursor = target
            self._save()
            return {"ok": True, "label": entry["label"], "files": files,
                    "entry": entry}

    def restore(self, version_id: str) -> dict:
        """Write an arbitrary version's content back — and append it as a new one.

        This is upstream's restore route, and the reason to copy it rather than
        rewind: after restoring v3 you can still reach v9, because v9 is still
        in the timeline. A rewind would have deleted it.
        """
        with self._lock:
            entry = self.find(version_id)
            if not entry:
                return {"error": "That version is no longer in the timeline."}
            return {"ok": True, "label": entry["label"],
                    "files": self.content(entry), "entry": entry}

    def note_restored(self, files: dict[Path, str], restored: dict,
                      prompt: str | None = None) -> dict:
        """Record that `files` came from an earlier version.

        Takes either the entry itself or the whole result of `restore()`. The
        two look nearly identical — both carry `label` — so the obvious call
        `note_restored(files, restore(id))` used to raise KeyError on `id` and
        lose the provenance of the restore it was recording. Accepting both
        costs one line and removes a trap.
        """
        entry = restored.get("entry", restored)
        return self.create(files, source="restore", restore_from=entry["id"],
                           prompt=prompt or f"restored {entry['label']}")


# ── recovery from the command line ───────────────────────────────────────────
#
# WHY THIS EXISTS
#   On 2026-07-30 a test restored the oldest entry in a store that still held a
#   version from the previous session, and an hour of source edits went back to
#   how they had been that morning. The model did its job — the newer state was
#   still in the timeline, exactly as append-only promises — but getting it back
#   meant hand-writing a script against `Versions` internals while the working
#   tree sat wrong. That is the wrong thing to be composing under pressure.
#
#   So: recovery is a command. `python versions.py list` shows what is holdable
#   and `python versions.py restore <n>` puts it back. Neither needs the editor
#   to be running, which matters because the usual reason you want this is that
#   something about the editor has gone wrong.

def _store_root(start: Path) -> tuple[Path, Path]:
    """Locate the store. It lives beside the site, and its paths are relative
    to the site's PARENT — a distinction that has already cost one incident, so
    it is resolved in one place and never re-derived by a caller."""
    site = start.resolve()
    store = site / ".versions"
    if not store.exists():
        raise SystemExit(f"no version store at {store}")
    return site.parent, store


def _cli(argv: list[str]) -> int:
    import argparse                                 # noqa: PLC0415

    ap = argparse.ArgumentParser(
        prog="versions.py", description="Inspect and recover site versions.")
    ap.add_argument("--site", default=".", help="site directory (default: cwd)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("where", help="where the store is and what it tracks")
    sub.add_parser("list", help="every version, newest first")
    p = sub.add_parser("show", help="what one version holds")
    p.add_argument("version", type=int)
    p = sub.add_parser("restore", help="write a version's files back to disk")
    p.add_argument("version", type=int)
    p.add_argument("--dry-run", action="store_true",
                   help="report which files would change, and change nothing")
    p = sub.add_parser("export", help="copy a version's files to a directory")
    p.add_argument("version", type=int)
    p.add_argument("dest")
    args = ap.parse_args(argv)

    project, store = _store_root(Path(args.site))
    v = Versions(project, store)
    if not v.entries:
        print("the store is empty")
        return 0

    def pick(n: int) -> dict:
        hit = next((e for e in v.entries if e["version"] == n), None)
        if hit is None:
            raise SystemExit(f"no version {n} — try `list`")
        return hit

    if args.cmd == "where":
        print(f"store    {store}")
        print(f"paths in it are relative to  {project}")
        print(f"versions {len(v.entries)}, standing on "
              f"v{v.entries[v.cursor]['version'] if 0 <= v.cursor < len(v.entries) else '?'}")
        print(f"tracked  {len(v.entries[-1]['files'])} files")
        return 0

    if args.cmd == "list":
        for e in reversed(v.entries):
            here = "→" if v.entries.index(e) == v.cursor else " "
            when = time.strftime("%d %b %H:%M", time.localtime(e["created_at"]))
            print(f" {here} v{e['version']:<4} {when}  {e['source']:<8} "
                  f"{(e['prompt'] or e['label'])[:58]}")
        return 0

    entry = pick(args.version)

    if args.cmd == "show":
        print(f"v{entry['version']}  {entry['label']}")
        print(f"  {entry['prompt'] or ''}")
        for rel in sorted(entry["files"]):
            print(f"  {rel}")
        return 0

    files = v.content(entry)

    if args.cmd == "export":
        dest = Path(args.dest)
        for rel, text in files.items():
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text, encoding="utf-8")
        print(f"v{entry['version']} → {dest}  ({len(files)} files)")
        return 0

    # restore: say what will change before changing it, because the operation
    # that made this command necessary was one that changed more than expected.
    changed = [rel for rel, text in files.items()
               if not (project / rel).exists()
               or (project / rel).read_text(encoding="utf-8") != text]
    if not changed:
        print(f"v{entry['version']} is already what is on disk")
        return 0
    print(f"v{entry['version']}  {entry['label']}")
    for rel in sorted(changed):
        print(f"  would rewrite  {rel}" if args.dry_run else f"  rewrote  {rel}")
    if args.dry_run:
        return 0
    for rel in changed:
        out = project / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(files[rel], encoding="utf-8")
    print(f"{len(changed)} file(s) restored — rebuild to see it")
    return 0


if __name__ == "__main__":
    import sys                                      # noqa: PLC0415
    raise SystemExit(_cli(sys.argv[1:]))
