#!/usr/bin/env python3
"""Push-after-change sync for the sotd-catalog backup repos.

Two repos, one rule:
  - martha-muse-bot/sotd-catalog (PUBLIC): code, docs, knowledge,
    precedents, crons, hook script, this sync script, AND a scrubbed
    public catalogue (catalog/catalog_public.json) -- just what the
    products in the catalogue are, with all match data stripped (no
    aliases, no attestation examples/provenance, no unverified
    clusters, no decisions/match_notes -- the audit trail stays
    private by Jim's 2026-11-18 decision; evidence prose has Reddit
    author names, u/ handles, thread ids, and quoted alias strings
    that are not the product/brand name redacted to [redacted]).
    What a public face for the match data might look like is a later
    decision (Jim, 2026-11-17).
  - martha-muse-bot/sotd-catalog-data (PRIVATE): the match data --
    the full catalog DB (gzipped) + its JSON exports, i.e. everything
    about what strings match to which catalog items, plus the queue
    and attestation provenance. It holds all the Reddit-derived
    content, so it stays private by design.

Publishes via the GitHub API, using the same connector credential as
the nmrs PR work and the wetshaving-knowledge vault pushes (imported
github.py call function) -- no token value is ever handled here.

THE RULE (Jim, 2026-11-17): push after every validated change. Every
time a change is made that is validated as working, run this script
and push it -- `push` for the public repo, `push-data` for the
private data repo. There are NO periodic or occasional syncs and NO
sync cron -- this script is run by hand after each validated change,
nothing more. The data push REFUSES to run unless the data repo
verifies as private (see _assert_repo_private); if that check ever
fails, stop and report it -- never push catalog data to a public repo.

These two repos are the go-forward WORKING DIRECTORIES (Jim,
2026-11-18), not a periodic snapshot artifact: the live workspace is
mirrored to them on every validated change via this script (refresh
+ push), never on a timer. The trigger is explicit: after any
validated catalog change, code change, or knowledge change, run
refresh + push so the repos reflect it the same turn. The staging
trees are the push source, not a snapshot product. There is no sync
cadence, no scheduled sync, and no "produce the artifact on a
schedule" anywhere in this script.

Merged-catalog shards (Jim, 2026-11-18 -- instead of gzipping the
48 MB single file, which would make diffs unreadable): the merged
catalog is stored as one file per category under
catalog/catalog_merged/<category>.json (8 files: aftershave, blade,
brush, fragrance, handle, knot, razor, soap), written by sotd_db.export_json
and read by match_all.py's shard loader. No single
catalog_merged.json exists anywhere anymore.

API size limits (measured 2026-11-18, both below the documented
numbers): Git Data API create-blob rejects files above ~10 MB (9.8 MB
ok, 18.3 MB -> 422 "input too large"); Contents API accepts 28.6 MB
but rejects 48.5 MB (422 "file is too large"). Largest shard is
~13 MB, so shards fit the Contents API. Any staging file over
BLOB_SIZE_LIMIT is uploaded via the Contents API (one commit each,
BEFORE the Data-API tree push -- see _push_large_files_via_contents);
everything smaller goes through the normal Data-API blob path.

Subcommands:
  refresh  rebuild both staging trees from the live workspace
           (fresh DB export, re-gzip catalog.db, copy code/docs/knowledge/
           crons/hook script into the public tree, copy the DB + JSON
           exports -- merged catalog as 8 per-category shards -- into
           the data tree), verify the .gz round-trips,
           write both manifests
  push     refresh, then upload the public staging tree as one commit
           on main (incremental blob diff vs the parent tree, full
           tree-build fallback -- same pattern as
           wetshaving-vault/push.py)
  push-data  refresh, then upload the data staging tree the same way
           -- after verifying the data repo is private
  create   POST /user/repos for sotd-catalog (public, no auto-init)
  create-data  POST /user/repos for sotd-catalog-data (private)
  seed     first commit via the Contents API (the Git Database API
           refuses blob creation on a completely empty repo)
  seed-data  same, for the data repo
  verify   GET repo + branch head + file listing, check README renders
  verify-data  same, for the data repo (plus blob-SHA comparison)

Never use `git push` or any git CLI remote operation for these repos --
verified 2026-10-28 to fail with GitHub 401 for this credential. All
remote writes go through the GitHub API via the helper below. Local
git operations on a staging dir are fine.

Layout: this script lives in tools/ at the public repo root. The
public repo root IS the public staging tree; the data staging tree
lives at ~/workspace/sotd-catalog-data-staging. refresh() rebuilds
both from the live workspace, so the trees on disk are always what
gets pushed.
"""
import base64
import gzip
import hashlib
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import unicodedata
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

OWNER = "martha-muse-bot"
REPO = "sotd-catalog"
DATA_REPO = "sotd-catalog-data"
API = "https://api.github.com"

ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = Path.home() / "workspace" / "sotd-catalog-data-staging"
HOME = Path.home()
SOTD = HOME / "workspace" / "sotd"
CATALOG = SOTD / "catalog"
KNOWLEDGE = SOTD / "knowledge"
GOAL = HOME / "workspace" / "goals" / "sotd-canonical-product-catalog"
HOOK_SCRIPT = HOME / "hooks" / "scripts" / "sotd_validator_loop.sh"

spec = importlib.util.spec_from_file_location(
    "gh", HOME / "workspace" / "custom-connectors" /
    "custom.github-nmrs" / "bin" / "github.py")
gh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gh)

# Long-timeout API calls (same credential machinery as github.py) for
# multi-MB Contents API uploads; gh.call's 30 s default cannot be
# assumed to cover a ~17 MB base64 body.
sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
from dynamic_credentials import add_surrogate_to_request, read_json_response

# Git Data API create-blob rejects files above ~10 MB (9.8 MB ok,
# 18.3 MB -> 422, measured 2026-11-18). Files over this limit are
# uploaded via the Contents API instead (see
# _push_large_files_via_contents). The Contents API itself rejects
# 48.5 MB (422) while accepting 28.6 MB -- hence the merged catalog
# is sharded by category, largest shard ~13 MB.
BLOB_SIZE_LIMIT = 10_000_000

EXCLUDE_FILES = {".DS_Store", ".catalog.lock"}
EXCLUDE_DIRS = {".git", "__pycache__"}

# (live source, repo-relative destination) for the PUBLIC repo.
# The catalog data (DB + JSON exports) does NOT go here -- it lives in
# the private data repo; see DATA_COPIES. The catalog DB is handled
# separately (gzipped, round-trip verified) in refresh().
COPIES = [
    (SOTD / "sotd_parser.py", "sotd_parser.py"),
    (SOTD / "build_2026.py", "build_2026.py"),
    (SOTD / "build_year.py", "build_year.py"),
    (SOTD / "fill_gaps.py", "fill_gaps.py"),
    (SOTD / "fill_gaps_year.py", "fill_gaps_year.py"),
    (SOTD / "lg_sweep.py", "lg_sweep.py"),
    (CATALOG / "sotd_db.py", "catalog/sotd_db.py"),
    (CATALOG / "match_all.py", "catalog/match_all.py"),
    (CATALOG / "work" / "l1_proposer.py", "catalog/work/l1_proposer.py"),
    (CATALOG / "validation_README.md", "catalog/validation_README.md"),
    (CATALOG / "precedents.md", "catalog/precedents.md"),
    (CATALOG / "discuss_consolidated.md", "catalog/discuss_consolidated.md"),
    (CATALOG / "multi_item_field_analysis_2026-11-16.md",
     "catalog/multi_item_field_analysis_2026-11-16.md"),
    (CATALOG / "comma_carveout_scoping_2026-11-17.md",
     "catalog/comma_carveout_scoping_2026-11-17.md"),
    (CATALOG / "handle_knot_parsing_analysis_2026-11-18.md",
     "catalog/handle_knot_parsing_analysis_2026-11-18.md"),
    (CATALOG / "ikon_bulk_harvest_2026-11-08.md",
     "catalog/ikon_bulk_harvest_2026-11-08.md"),
    (CATALOG / "tech_attribute_fold.md", "catalog/tech_attribute_fold.md"),
    (CATALOG / "long_tail_segmentation.md",
     "catalog/long_tail_segmentation.md"),
    (CATALOG / "long_tail_segmentation.csv",
     "catalog/long_tail_segmentation.csv"),
    (GOAL / "GOAL.md", "GOAL.md"),
    (HOOK_SCRIPT, "hooks/sotd_validator_loop.sh"),
]

# (live source, repo-relative destination) for the PRIVATE data repo.
# The JSON exports are regenerated from the DB first, then copied
# here; the DB itself is gzipped into DATA_ROOT/catalog/ in refresh().
# The merged catalog goes over as 8 per-category shards (see the
# shard copy in cmd_refresh), not the retired single file.
DATA_COPIES = [
    (CATALOG / "validation_queue.json", "catalog/validation_queue.json"),
    (CATALOG / "candidate_aliases.json", "catalog/candidate_aliases.json"),
    (CATALOG / "brands.json", "catalog/brands.json"),
]

# knowledge/ is copied whole EXCEPT the derived string index
# (string_index.pkl, ~124 MB, regenerable via tools/build_string_index.py)
# and __pycache__.
KNOWLEDGE_EXCLUDE = {"string_index.pkl", "__pycache__"}


def call(method, url, payload=None):
    status, out = gh.call(method, url, payload)
    if status >= 400:
        print(f"ERROR {method} {url} -> {status}: {json.dumps(out)[:500]}",
              file=sys.stderr)
        raise SystemExit(1)
    return out


def _call_long(method, url, payload=None, timeout=600):
    """gh.call with a long socket timeout, for multi-MB Contents API
    uploads. Same credential machinery and hosts; returns the raw
    (status, body) tuple so the caller can handle failures."""
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "Martha-nmrs-prs")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    add_surrogate_to_request(req, gh.CRED, allowed_hosts=gh.HOSTS)
    try:
        with urllib.request.build_opener(gh.NoRedirect()).open(
                req, timeout=timeout) as resp:
            return resp.status, read_json_response(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed


def _contents_put(repo, branch, rel, raw, message):
    """Upload one file via the Contents API. Returns the blob SHA.
    Creates one commit per file -- callers must run this BEFORE any
    Data-API tree push, since it moves the branch head (the later
    incremental diff then sees the file as already in sync and skips
    it). Only used for files over BLOB_SIZE_LIMIT."""
    status, out = gh.call(
        "GET", f"{API}/repos/{OWNER}/{repo}/contents/{rel}?ref={branch}")
    payload = {"message": message,
               "content": base64.b64encode(raw).decode(),
               "branch": branch}
    if status == 200 and out.get("sha"):
        payload["sha"] = out["sha"]
    status, out = _call_long(
        "PUT", f"{API}/repos/{OWNER}/{repo}/contents/{rel}", payload)
    if status >= 400:
        print(f"ERROR PUT {API}/repos/{OWNER}/{repo}/contents/{rel} -> "
              f"{status}: {json.dumps(out)[:300]}", file=sys.stderr)
        raise SystemExit(1)
    print(f"  contents: {rel} ({len(raw)} bytes) -> "
          f"commit {out['commit']['sha'][:7]}")
    return out["content"]["sha"]


def _push_large_files_via_contents(source, repo, branch):
    """Upload every staging file over BLOB_SIZE_LIMIT via the Contents
    API (one commit each), skipping files whose remote blob already
    matches. Idempotent -- safe to call before every push. Must run
    BEFORE the Data-API tree work: it moves the branch head, and the
    later incremental diff fetches the new head and sees these files
    as already in sync."""
    for p in sorted(iter_source_files(source)):
        if p.stat().st_size <= BLOB_SIZE_LIMIT:
            continue
        rel, sha, _mode, raw = _local_blob_info(p, source)
        status, out = gh.call(
            "GET", f"{API}/repos/{OWNER}/{repo}/contents/{rel}?ref={branch}")
        if status == 200 and out.get("sha") == sha:
            print(f"  contents: {rel} already in sync, skipping")
            continue
        print(f"  contents: {rel} ({p.stat().st_size} bytes) over "
              f"Data-API blob limit, uploading via Contents API")
        blob_sha = _contents_put(repo, branch, rel, raw,
                                 f"Sync {repo}: {rel}")
        if blob_sha != sha:
            raise RuntimeError(f"contents blob sha mismatch for {rel}")


def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _gzip_db(db_path, out_path):
    """Deterministic gzip (mtime=0) so an unchanged DB produces identical
    bytes and the incremental push can skip re-uploading it."""
    with open(db_path, "rb") as f_in, open(out_path, "wb") as f_out:
        with gzip.GzipFile(filename="", mode="wb", compresslevel=9,
                           fileobj=f_out, mtime=0) as gz:
            shutil.copyfileobj(f_in, gz, length=1 << 20)


def _verify_gz(gz_path, expect_counts):
    """Round-trip check: gunzip to temp, sqlite integrity + counts must
    match the live DB's counts."""
    with tempfile.TemporaryDirectory() as td:
        tmp = os.path.join(td, "catalog.db")
        with gzip.open(gz_path, "rb") as f_in, open(tmp, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=1 << 20)
        conn = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
        try:
            row = conn.execute("PRAGMA integrity_check").fetchone()
            assert row[0] == "ok", f"integrity_check: {row}"
            n = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        finally:
            conn.close()
    assert n == expect_counts["entries"], \
        f"entry count mismatch: gz has {n}, live has {expect_counts['entries']}"
    print(f"  catalog.db.gz round-trip ok: {n} entries, integrity ok")


def _write_manifest(root, counts):
    """Inventory with sizes + md5s, for verification. The manifest
    lists itself (the previous refresh's bytes/md5 -- inherently one
    refresh stale, since it is written after the inventory loop); the
    entry is kept so manifest-vs-tree counts stay consistent. The
    inventory applies the same exclusions as the push (EXCLUDE_FILES,
    EXCLUDE_DIRS) so verify never reports a phantom missing file."""
    manifest = {"generated": "refresh from live workspace",
                "counts": {"entries": counts["entries_total"],
                           "verified": counts["entries_by_status"].get(
                               "verified"),
                           "queue": counts["queue_total"],
                           "brands": counts["brands_total"],
                           "candidates": counts["candidates_total"]},
                "files": {}}
    for p in sorted(root.rglob("*")):
        if not p.is_file() or ".git" in p.parts:
            continue
        if p.name in EXCLUDE_FILES:
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(root).parts):
            continue
        rel = str(p.relative_to(root))
        manifest["files"][rel] = {"bytes": p.stat().st_size,
                                  "md5": _md5(p)}
    (root / "manifest.json").write_text(json.dumps(manifest, indent=1))
    total = sum(f["bytes"] for f in manifest["files"].values())
    print(f"  {root.name}/manifest.json: {len(manifest['files'])} files, "
          f"{total} bytes total")
    return manifest


def _scrub_value(v):
    """Recursively drop provenance from a kept value. Dict keys naming
    provenance (examples, thread_id, thread_date, author, post) are
    dropped -- that covers attestation examples and sotd-post evidence
    items. Provenance also hides in STRING form (evidence strings of
    the form "author:NAME; date:...; thread_id:XXXX"), so string
    values get their thread_id/author VALUES redacted too -- the
    citation stays, the identifying value goes. The bare words
    'aliases'/'author_scoped' in our own evidence prose are NOT
    redacted (they are our words, not Reddit data); see the scrub
    verification in the report for the exact residual counts.
    (decisions and match_notes are no longer exported at all --
    Jim, 2026-11-18 -- so their prose residuals are gone by
    construction.)"""
    _PROVENANCE_KEYS = {"examples", "thread_id", "thread_date", "author",
                        "post"}
    if isinstance(v, dict):
        return {k: _scrub_value(x) for k, x in v.items()
                if k not in _PROVENANCE_KEYS}
    if isinstance(v, list):
        return [_scrub_value(x) for x in v]
    if isinstance(v, str):
        s = re.sub(r"(['\"]?thread_id['\"]?\s*[:=]\s*['\"]?)[A-Za-z0-9]+",
                   r"\1[redacted]", v)
        s = re.sub(r"(['\"]?author['\"]?\s*[:=]\s*['\"]?)[^'\",}\];\s]+",
                   r"\1[redacted]", s)
        return s
    return v


def _norm_name(s):
    """Accent-folded, lowercased, punctuation-collapsed name compare."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def _build_evidence_ctx(conn, pub_entries):
    """Redaction context for evidence prose. Authors come from every
    attestation example in the live DB; aliases from every entry's
    alias fields; product/brand names from the public entries only
    (a quoted string that IS a product or brand name is the public
    catalogue's own content, not a leak)."""
    authors = set()
    aliases = set()
    for (d,) in conn.execute("SELECT data FROM entries"):
        e = json.loads(d)
        for ex in ((e.get("attestation") or {}).get("examples") or []):
            if isinstance(ex, dict) and ex.get("author"):
                authors.add(ex["author"])
        for a in (e.get("aliases") or []):
            aliases.add(a)
        for la in (e.get("loose_aliases") or []):
            if isinstance(la, dict) and la.get("alias"):
                aliases.add(la["alias"])
        for asa in (e.get("author_scoped_aliases") or []):
            if isinstance(asa, dict) and asa.get("alias"):
                aliases.add(asa["alias"])
    names = set()
    for e in pub_entries:
        if e.get("product"):
            names.add(_norm_name(e["product"]))
        if e.get("brand"):
            names.add(_norm_name(e["brand"]))
    return {"authors_lower": {a.lower() for a in authors if len(a) >= 4},
            "aliases": aliases, "names": names}


def _redact_thread(m):
    """Redact 'thread <id>' only when the token looks like a Reddit /
    forum thread id (6 chars any, or 7 chars with a digit) -- plain
    words after 'thread' ('thread confirms', 'thread photo') stay."""
    tok = m.group(1)
    if len(tok) == 6 or (len(tok) == 7 and any(c.isdigit() for c in tok)):
        return "thread [redacted]"
    return m.group(0)


def _scrub_evidence_text(s, ctx):
    """Redact Reddit provenance out of one evidence prose string.
    Order matters: quoted alias strings first (a quoted span may
    itself contain a u/ handle), then u/ handles, thread ids, and
    author-name tokens."""
    def _quoted(m):
        content = m.group(2)
        if (content in ctx["aliases"]
                and _norm_name(content) not in ctx["names"]):
            return "[redacted]"
        return m.group(0)
    s = re.sub(r"""(['"])([^'"]{2,120})\1""", _quoted, s)
    s = re.sub(r"\bu/[A-Za-z0-9_-]+", "u/[redacted]", s)
    s = re.sub(r"\bthread\s+([A-Za-z0-9]{6,7})\b", _redact_thread, s,
               flags=re.I)
    parts = re.split(r"([A-Za-z0-9_.\-]+)", s)
    authors = ctx["authors_lower"]
    parts = [("[redacted]" if p.lower() in authors else p)
             if re.fullmatch(r"[A-Za-z0-9_.\-]+", p or "") else p
             for p in parts]
    return "".join(parts)


def _scrub_evidence(v, ctx):
    """Evidence items only: _scrub_value first (provenance keys +
    thread_id:/author: values), then prose redaction on every string
    except URLs (reddit.com citation links are an accepted residual).
    """
    v = _scrub_value(v)
    if isinstance(v, dict):
        return {k: (x if k == "url" else _scrub_evidence(x, ctx))
                for k, x in v.items()}
    if isinstance(v, list):
        return [_scrub_evidence(x, ctx) for x in v]
    if isinstance(v, str):
        return _scrub_evidence_text(v, ctx)
    return v


# Statuses that are products (or product-like) and belong in the public
# catalogue. Unverified clusters are raw post strings, not products --
# they stay private.
PUBLIC_STATUSES = {"verified", "needs-review", "attested", "corroborated",
                   "anecdotal"}
# The ONLY top-level keys a public-catalogue entry may carry. Everything
# else -- aliases, loose_aliases, author_scoped_aliases, label, format,
# and any other field -- is dropped by construction (whitelist, not
# blacklist). attestation is rebuilt separately with counts only.
# decisions and match_notes are EXCLUDED by Jim's 2026-11-18 decision:
# they are the audit trail / working notes, and their prose quoted
# alias strings and Reddit author names (~36 entries) -- the very match
# data the public catalogue exists to keep out. The audit trail stays
# in the private data repo.
PUBLIC_KEEP_KEYS = {"id", "category", "brand", "brand_group",
                    "brand_status", "product", "status", "evidence",
                    "set_key", "set_siblings"}


def _build_public_catalog(conn, out_path):
    """Scrubbed public catalogue: just what the products in the
    catalogue are. No match data, no provenance. Repeatable -- refresh
    regenerates it from the live DB every time."""
    rows = conn.execute("SELECT data FROM entries").fetchall()
    entries = []
    skipped = 0
    for (d,) in rows:
        e = json.loads(d)
        if e.get("status") not in PUBLIC_STATUSES:
            skipped += 1
            continue
        pub = {}
        for k in sorted(PUBLIC_KEEP_KEYS):
            if k in e:
                pub[k] = _scrub_value(e[k])
        att = e.get("attestation") or {}
        pub_att = {k: att[k] for k in ("uses", "distinct_authors", "years")
                   if k in att}
        if pub_att:
            pub["attestation"] = pub_att
        entries.append(pub)
    # Evidence prose gets a second pass: Reddit author names, u/
    # handles, thread ids, and quoted alias strings that are not the
    # product/brand name are redacted to [redacted]. (Jim, 2026-11-18:
    # push only with zero quoted alias strings, zero author names,
    # zero thread_id values in the public file.)
    ctx = _build_evidence_ctx(conn, entries)
    for pub in entries:
        if "evidence" in pub:
            pub["evidence"] = _scrub_evidence(pub["evidence"], ctx)
    entries.sort(key=lambda x: x["id"])
    by_status = {}
    for e in entries:
        by_status[e["status"]] = by_status.get(e["status"], 0) + 1
    out = {"generated": "scrubbed public catalogue: products only. "
                        "Match data (aliases, loose aliases, author-scoped "
                        "aliases, attestation examples/provenance) stripped; "
                        "decisions and match_notes excluded by Jim's "
                        "2026-11-18 decision (audit trail stays private). "
                        "Evidence prose has Reddit author names, u/ handles, "
                        "thread ids, and quoted alias strings that are not "
                        "the product/brand name redacted to [redacted]. "
                        "Regenerated from the live catalog DB by "
                        "tools/sync_to_github.py refresh.",
           "counts": {"entries": len(entries), "by_status": by_status,
                      "excluded_unverified": skipped},
           "entries": entries}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"  catalog_public.json: {len(entries)} entries "
          f"({skipped} unverified excluded), "
          f"{out_path.stat().st_size} bytes")
    return out


def cmd_refresh(_args):
    """Rebuild both staging trees from the live workspace."""
    sys.path.insert(0, str(CATALOG))
    import sotd_db
    conn = sotd_db.connect()
    written = sotd_db.export_json(conn)
    counts = sotd_db.counts(conn)
    print(f"fresh export: {written}")
    print(f"counts: entries={counts['entries_total']} "
          f"verified={counts['entries_by_status'].get('verified')} "
          f"queue={counts['queue_total']}")

    # Scrubbed public catalogue (products only, match data stripped)
    # into the public tree; the full DB + exports go to the data tree.
    _build_public_catalog(conn, ROOT / "catalog" / "catalog_public.json")

    for src, rel in COPIES:
        if not src.exists():
            print(f"  SKIP missing: {src}")
            continue
        dst = ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"  copied {len(COPIES)} files to public tree")

    # knowledge/ tree (whole, minus the derived index + pycache)
    dst_k = ROOT / "knowledge"
    if dst_k.exists():
        shutil.rmtree(dst_k)
    shutil.copytree(KNOWLEDGE, dst_k, ignore=shutil.ignore_patterns(
        "string_index.pkl", "__pycache__"))
    print("  copied knowledge/ (excluding string_index.pkl, __pycache__)")

    # crons/ tree as-is
    dst_c = ROOT / "crons"
    if dst_c.exists():
        shutil.rmtree(dst_c)
    shutil.copytree(GOAL / "crons", dst_c)
    print("  copied crons/")

    # catalog data tree: DB, gzipped + round-trip verified, plus the
    # JSON exports regenerated above. Data NEVER goes in ROOT.
    for src, rel in DATA_COPIES:
        if not src.exists():
            print(f"  SKIP missing: {src}")
            continue
        dst = DATA_ROOT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"  copied {len(DATA_COPIES)} files to data tree")

    # merged catalog shards (one file per category; the single
    # catalog_merged.json is retired -- Jim, 2026-11-18)
    shard_src = CATALOG / "catalog_merged"
    shard_dst = DATA_ROOT / "catalog" / "catalog_merged"
    if shard_dst.exists():
        shutil.rmtree(shard_dst)
    shutil.copytree(shard_src, shard_dst)
    print(f"  copied {len(list(shard_dst.glob('*.json')))} shards "
          f"to data tree")
    stale = DATA_ROOT / "catalog" / "catalog_merged.json"
    if stale.exists():
        stale.unlink()
        print("  removed retired catalog_merged.json from data tree")

    gz_path = DATA_ROOT / "catalog" / "catalog.db.gz"
    gz_path.parent.mkdir(parents=True, exist_ok=True)
    _gzip_db(CATALOG / "catalog.db", gz_path)
    print(f"  catalog.db.gz: {gz_path.stat().st_size} bytes")
    _verify_gz(gz_path, {"entries": counts["entries_total"]})

    _write_manifest(ROOT, counts)
    _write_manifest(DATA_ROOT, counts)
    print("refresh done")


def iter_source_files(source):
    for p in sorted(source.rglob("*")):
        if not p.is_file():
            continue
        if p.name in EXCLUDE_FILES:
            continue
        if any(part in EXCLUDE_DIRS for part in p.relative_to(source).parts):
            continue
        yield p


def current_branch_head(branch, repo=REPO):
    status, out = gh.call(
        "GET", f"{API}/repos/{OWNER}/{repo}/git/ref/heads/{branch}")
    if status >= 400:
        return None, None
    head = out["object"]["sha"]
    commit = call("GET", f"{API}/repos/{OWNER}/{repo}/git/commits/{head}")
    return head, commit["tree"]["sha"]


def _local_blob_info(p, source):
    """(rel, git_blob_sha, mode, raw_bytes) computed locally, no upload."""
    rel = str(p.relative_to(source))
    if p.is_symlink():
        raw = p.readlink().encode()
        mode = "120000"
    else:
        raw = p.read_bytes()
        mode = "100755" if (p.stat().st_mode & 0o111) else "100644"
    sha = hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    return rel, sha, mode, raw


def _commit_and_ref(tree_sha, parent, branch, message, repo=REPO):
    commit = call("POST", f"{API}/repos/{OWNER}/{repo}/git/commits", {
        "message": message,
        "tree": tree_sha,
        "parents": [parent] if parent else [],
    })
    print(f"commit: {commit['sha']}")
    try:
        ref = call("POST", f"{API}/repos/{OWNER}/{repo}/git/refs",
                   {"ref": f"refs/heads/{branch}", "sha": commit["sha"]})
        print(f"ref created: {ref['ref']} -> {ref['object']['sha']}")
    except SystemExit:
        ref = call("PATCH",
                   f"{API}/repos/{OWNER}/{repo}/git/refs/heads/{branch}",
                   {"sha": commit["sha"], "force": False})
        print(f"ref updated: {ref['ref']} -> {ref['object']['sha']}")


def push_tree(source, branch, message, repo=REPO):
    """Full tree build (push.py pattern): upload every blob, build
    subtrees deepest-first, commit, update ref. NOTE: a fresh root
    tree built from staging DELETES anything on the branch that is
    not in staging -- correct for these repos, whose staging trees
    are the whole content, but never point this at a repo with files
    that live only remotely. Files over BLOB_SIZE_LIMIT are uploaded
    via the Contents API first (see _push_large_files_via_contents)
    and referenced by their content SHA below."""
    _push_large_files_via_contents(source, repo, branch)
    files = list(iter_source_files(source))
    print(f"files to upload: {len(files)}")
    total = sum(p.stat().st_size for p in files)
    print(f"total bytes: {total}")

    # Files over the Data-API blob limit go up via the Contents API
    # first (one commit each); the tree below then references their
    # already-existing blobs by local content SHA.
    _push_large_files_via_contents(source, repo, branch)

    def make_blob(p):
        rel = str(p.relative_to(source))
        if p.is_symlink():
            raw = p.readlink().encode()
            out = call("POST", f"{API}/repos/{OWNER}/{repo}/git/blobs",
                       {"content": raw.decode("utf-8"), "encoding": "utf-8"})
            return rel, out["sha"], "120000"
        st = p.stat()
        mode = "100755" if (st.st_mode & 0o111) else "100644"
        if st.st_size > BLOB_SIZE_LIMIT:
            # Already uploaded via the Contents API above; the blob
            # exists remotely under its content SHA.
            _rel, sha, _mode, _raw = _local_blob_info(p, source)
            return rel, sha, mode
        raw = p.read_bytes()
        try:
            content, encoding = raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            content, encoding = base64.b64encode(raw).decode(), "base64"
        out = call("POST", f"{API}/repos/{OWNER}/{repo}/git/blobs",
                   {"content": content, "encoding": encoding})
        return rel, out["sha"], mode

    entries = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for i, (rel, sha, mode) in enumerate(ex.map(make_blob, files)):
            entries.append((rel, sha, mode))
            if (i + 1) % 200 == 0:
                print(f"  blobs: {i + 1}/{len(files)}")
    print(f"blobs done: {len(entries)}")

    by_dir = {}
    for rel, sha, mode in entries:
        d, _, name = rel.rpartition("/")
        by_dir.setdefault(d, []).append(
            {"path": name, "mode": mode, "type": "blob", "sha": sha})
    all_dirs = {""}
    for rel, _sha, _mode in entries:
        d = rel.rpartition("/")[0]
        parts = d.split("/") if d else []
        for i in range(1, len(parts) + 1):
            all_dirs.add("/".join(parts[:i]))

    def depth(d):
        return 0 if d == "" else d.count("/") + 1

    dir_sha = {}
    for d in sorted(all_dirs, key=depth, reverse=True):
        tree_entries = list(by_dir.get(d, []))
        children = set()
        for x in all_dirs:
            if x == d:
                continue
            if d == "":
                if "/" not in x:
                    children.add(x)
            elif x.startswith(d + "/") and x[len(d) + 1:].count("/") == 0:
                children.add(x)
        for sub in sorted(children):
            tree_entries.append({"path": sub.rpartition("/")[2],
                                 "mode": "040000", "type": "tree",
                                 "sha": dir_sha[sub]})
        out = call("POST", f"{API}/repos/{OWNER}/{repo}/git/trees",
                   {"tree": tree_entries})
        dir_sha[d] = out["sha"]
    print(f"tree: {dir_sha['']}")
    parent, _bt = current_branch_head(branch, repo=repo)
    _commit_and_ref(dir_sha[""], parent, branch, message, repo=repo)


def push_tree_incremental(source, branch, message, repo=REPO):
    """Diff local files against the parent commit's recursive tree,
    upload only changed blobs, POST one small tree (base_tree +
    changed/deleted paths). Raises before the commit step on any
    failure so the caller can fall back to push_tree(). Files over
    BLOB_SIZE_LIMIT are uploaded via the Contents API first (see
    _push_large_files_via_contents) -- the diff below then sees them
    as already in sync and skips them."""
    _push_large_files_via_contents(source, repo, branch)
    parent, parent_tree = current_branch_head(branch, repo=repo)
    if not parent_tree:
        raise RuntimeError("no parent tree to diff against")
    status, out = gh.call(
        "GET",
        f"{API}/repos/{OWNER}/{repo}/git/trees/{parent_tree}?recursive=1")
    if status >= 400:
        raise RuntimeError(f"recursive tree fetch -> {status}")
    if out.get("truncated"):
        raise RuntimeError("recursive tree truncated; cannot diff safely")
    remote = {t["path"]: (t["sha"], t["mode"])
              for t in out.get("tree", []) if t.get("type") == "blob"}

    files = list(iter_source_files(source))
    local = {}
    for p in files:
        rel, sha, mode, raw = _local_blob_info(p, source)
        local[rel] = (sha, mode, raw)

    changed = {rel: v for rel, v in local.items()
               if remote.get(rel) != (v[0], v[1])}
    deleted = sorted(set(remote) - set(local))
    print(f"incremental: {len(files)} files, {len(changed)} changed, "
          f"{len(deleted)} deleted vs {parent[:7]}")
    if not changed and not deleted:
        print("incremental: no changes, skipping commit")
        return

    tree_entries = []
    for rel in sorted(changed):
        sha, mode, raw = changed[rel]
        if len(raw) > BLOB_SIZE_LIMIT:
            # Cannot happen in a single run: the helper above uploaded
            # this file via the Contents API and the diff then sees it
            # as in sync. Fail closed rather than attempting a Data-API
            # blob POST that is known to 422.
            raise RuntimeError(
                f"{rel} changed after Contents upload; rerun the push")
        if mode == "120000":
            content, encoding = raw.decode("utf-8"), "utf-8"
        else:
            try:
                content, encoding = raw.decode("utf-8"), "utf-8"
            except UnicodeDecodeError:
                content, encoding = base64.b64encode(raw).decode(), "base64"
        blob = call("POST", f"{API}/repos/{OWNER}/{repo}/git/blobs",
                    {"content": content, "encoding": encoding})
        if blob["sha"] != sha:
            raise RuntimeError(f"blob sha mismatch for {rel}")
        tree_entries.append({"path": rel, "mode": mode,
                             "type": "blob", "sha": blob["sha"]})
    for rel in deleted:
        tree_entries.append({"path": rel, "mode": remote[rel][1],
                             "type": "blob", "sha": None})

    out = call("POST", f"{API}/repos/{OWNER}/{repo}/git/trees",
               {"base_tree": parent_tree, "tree": tree_entries})
    print(f"tree: {out['sha']} ({len(tree_entries)} entries)")
    _commit_and_ref(out["sha"], parent, branch, message, repo=repo)


def _assert_repo_private(repo):
    """Hard gate for the data repo: abort unless GitHub says private.
    Call before ANY data push. Never push catalog data to a repo that
    does not verify as private."""
    status, out = gh.call("GET", f"{API}/repos/{OWNER}/{repo}")
    if status >= 400:
        print(f"ERROR: cannot verify visibility of {OWNER}/{repo} "
              f"(GET -> {status}); refusing to push data",
              file=sys.stderr)
        raise SystemExit(1)
    if not out.get("private"):
        print(f"ERROR: {OWNER}/{repo} is NOT private "
              f"(private={out.get('private')}); refusing to push data",
              file=sys.stderr)
        raise SystemExit(1)
    print(f"verified private: {OWNER}/{repo}")


def cmd_create(_args):
    out = call("POST", f"{API}/user/repos", {
        "name": REPO,
        "description": "Canonical catalog of r/Wetshaving Shave of the Day "
                       "products -- matcher, validation queue, precedents, "
                       "and world knowledge. Code, docs, and knowledge "
                       "only; the catalog data lives in the private "
                       "sibling repo sotd-catalog-data.",
        "private": False,
        "auto_init": False,
    })
    print(f"created: {out['full_name']} "
          f"(default_branch={out.get('default_branch')})")
    print(f"url: {out['html_url']}")


def cmd_create_data(_args):
    out = call("POST", f"{API}/user/repos", {
        "name": DATA_REPO,
        "description": "Catalog data for the SOTD canonical product "
                       "catalog (SQLite DB + JSON exports). PRIVATE: holds "
                       "Reddit-derived content; paired with the public "
                       "martha-muse-bot/sotd-catalog repo.",
        "private": True,
        "auto_init": False,
    })
    if not out.get("private"):
        print(f"ERROR: created {out['full_name']} but it is NOT private; "
              f"do NOT push data to it", file=sys.stderr)
        raise SystemExit(1)
    print(f"created (private): {out['full_name']} "
          f"(default_branch={out.get('default_branch')})")
    print(f"url: {out['html_url']}")


def cmd_seed(_args):
    """First commit via the Contents API (the Git Database API refuses
    blob creation on a completely empty repo). Seeds README.md."""
    raw = (ROOT / "README.md").read_bytes()
    out = call("PUT", f"{API}/repos/{OWNER}/{REPO}/contents/README.md", {
        "message": "Seed repository",
        "content": base64.b64encode(raw).decode(),
        "branch": "main",
    })
    print(f"seed commit: {out['commit']['sha']}")


def cmd_seed_data(_args):
    """Same as seed, for the private data repo."""
    raw = (DATA_ROOT / "README.md").read_bytes()
    out = call("PUT",
               f"{API}/repos/{OWNER}/{DATA_REPO}/contents/README.md", {
        "message": "Seed repository",
        "content": base64.b64encode(raw).decode(),
        "branch": "main",
    })
    print(f"seed commit: {out['commit']['sha']}")


def cmd_push(_args):
    cmd_refresh(_args)
    try:
        push_tree_incremental(
            ROOT, "main", "Sync sotd-catalog from live workspace")
    except (Exception, SystemExit) as e:
        print(f"incremental push failed ({e}); falling back to full "
              f"tree build", file=sys.stderr)
        push_tree(ROOT, "main", "Sync sotd-catalog from live workspace")


def cmd_push_data(_args):
    cmd_refresh(_args)
    _assert_repo_private(DATA_REPO)
    try:
        push_tree_incremental(
            DATA_ROOT, "main", "Sync sotd-catalog-data from live workspace",
            repo=DATA_REPO)
    except (Exception, SystemExit) as e:
        print(f"incremental push failed ({e}); falling back to full "
              f"tree build", file=sys.stderr)
        push_tree(DATA_ROOT, "main",
                  "Sync sotd-catalog-data from live workspace",
                  repo=DATA_REPO)


def _verify(repo, root):
    info = call("GET", f"{API}/repos/{OWNER}/{repo}")
    print(f"repo: {info['full_name']} default={info['default_branch']} "
          f"private={info['private']}")
    ref = call("GET", f"{API}/repos/{OWNER}/{repo}/git/ref/heads/main")
    print(f"main head: {ref['object']['sha']}")
    status, out = gh.call(
        "GET", f"{API}/repos/{OWNER}/{repo}/git/trees/"
        f"{ref['object']['sha']}?recursive=1")
    if status == 200 and not out.get("truncated"):
        remote = {t["path"]: t["sha"] for t in out.get("tree", [])
                  if t.get("type") == "blob"}
        manifest = json.loads((root / "manifest.json").read_text())
        local = set(manifest["files"])
        print(f"remote blobs: {len(remote)}, manifest files: {len(local)}")
        print(f"missing on remote: {sorted(local - set(remote))[:10]}")
        print(f"extra on remote: {sorted(set(remote) - local)[:10]}")
        # blob-SHA comparison proves remote content is byte-identical
        mismatched = []
        for rel in sorted(local & set(remote)):
            p = root / rel
            _rel, sha, _mode, _raw = _local_blob_info(p, root)
            if sha != remote[rel]:
                mismatched.append(rel)
        print(f"blob-sha mismatches: {len(mismatched)} {mismatched[:10]}")
    readme = call("GET", f"{API}/repos/{OWNER}/{repo}/readme")
    print(f"README via API: {readme.get('name')} "
          f"({readme.get('size')} bytes)")


def cmd_verify(_args):
    _verify(REPO, ROOT)


def cmd_verify_data(_args):
    _verify(DATA_REPO, DATA_ROOT)


if __name__ == "__main__":
    cmds = {"refresh": cmd_refresh, "push": cmd_push,
            "push-data": cmd_push_data, "create": cmd_create,
            "create-data": cmd_create_data, "seed": cmd_seed,
            "seed-data": cmd_seed_data, "verify": cmd_verify,
            "verify-data": cmd_verify_data}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        print(f"usage: sync_to_github.py {'|'.join(cmds)}", file=sys.stderr)
        print("Run `push` (and `push-data`) after every validated change. "
              "There is no scheduled sync -- see HANDOFF.md.", file=sys.stderr)
        sys.exit(2)
    cmds[sys.argv[1]](sys.argv[2:])
