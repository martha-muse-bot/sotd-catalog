"""Shared SQLite access layer for the SOTD canonical catalog.

catalog.db is the SOURCE OF TRUTH for catalog entries, the validation
queue, candidate aliases, and the brand registry. The JSON files
(catalog_merged/ shards, validation_queue.json, candidate_aliases.json,
brands.json) are read-only EXPORTS regenerated from the DB by
export_json(); never edit them directly. The merged catalog is sharded
one file per category (catalog_merged/<category>.json, 7 files) so each
stays under GitHub's API size limits and diffs stay per-category;
load_merged()/save_merged_shards() are the shard-aware accessors.

All agents doing catalog work must go through this module so writes are
transactional and crash-safe (WAL mode, busy_timeout 60s).

Usage:
    import sotd_db
    conn = sotd_db.connect()                  # read-write, WAL
    e = sotd_db.get_entry(conn, "soap/...")
    sotd_db.upsert_entry(conn, e)             # commits
    items = sotd_db.next_queue(conn, 12)      # next pending, seq order
    sotd_db.export_json(conn)                 # refresh the JSON exports
"""

import json
import os
import sqlite3
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, "catalog.db")

ENTRY_FILTER_COLS = ("category", "status", "brand", "product",
                     "brand_group", "brand_status")

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    ord INTEGER,
    category TEXT,
    status TEXT,
    brand TEXT,
    product TEXT,
    brand_group TEXT,
    brand_status TEXT,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category);
CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status);
CREATE INDEX IF NOT EXISTS idx_entries_cat_status ON entries(category, status);
CREATE INDEX IF NOT EXISTS idx_entries_brand_group ON entries(brand_group);
CREATE TABLE IF NOT EXISTS queue (
    queue_id TEXT PRIMARY KEY,
    ord INTEGER,
    kind TEXT,
    ref TEXT,
    state TEXT,
    seq INTEGER,
    data TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_queue_state ON queue(state);
CREATE INDEX IF NOT EXISTS idx_queue_seq ON queue(seq);
CREATE INDEX IF NOT EXISTS idx_queue_ref ON queue(ref);
CREATE TABLE IF NOT EXISTS brands (
    brand_id TEXT PRIMARY KEY,
    ord INTEGER,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidates (
    idx INTEGER PRIMARY KEY,
    data TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


def connect(db_path=DB_PATH, read_only=False):
    """Open a connection with WAL, 60s busy timeout, FK on."""
    if read_only:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True,
                               timeout=60.0)
    else:
        conn = sqlite3.connect(db_path, timeout=60.0)
    conn.execute("PRAGMA busy_timeout = 60000")
    conn.execute("PRAGMA foreign_keys = ON")
    if not read_only:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
    conn.row_factory = sqlite3.Row
    return conn


def init_schema(conn):
    conn.executescript(SCHEMA)
    conn.commit()


# ---------------------------------------------------------------- meta

def set_meta(conn, key, value):
    conn.execute("INSERT INTO meta(key, value) VALUES (?, ?) "
                 "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                 (key, value if isinstance(value, str) else json.dumps(value)))
    conn.commit()


def get_meta(conn, key, default=None):
    row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
    return row["value"] if row else default


# ---------------------------------------------------------------- entries

def _entry_cols(e):
    return (e.get("category"), e.get("status"), e.get("brand"),
            e.get("product"), e.get("brand_group"), e.get("brand_status"))


def get_entry(conn, entry_id):
    row = conn.execute("SELECT data FROM entries WHERE id = ?",
                       (entry_id,)).fetchone()
    return json.loads(row["data"]) if row else None


def upsert_entry(conn, entry):
    """Insert or replace one entry dict; extracted columns are refreshed
    from the dict. Preserves the original export order (ord) for ids
    that already exist; new ids go at the end. Commits."""
    eid = entry["id"]
    row = conn.execute("SELECT ord FROM entries WHERE id = ?", (eid,)).fetchone()
    if row is not None:
        ordv = row["ord"]
    else:
        ordv = conn.execute(
            "SELECT COALESCE(MAX(ord), -1) + 1 AS n FROM entries").fetchone()["n"]
    cat, status, brand, product, bgroup, bstatus = _entry_cols(entry)
    conn.execute(
        "INSERT INTO entries(id, ord, category, status, brand, product,"
        " brand_group, brand_status, data) VALUES (?,?,?,?,?,?,?,?,?)"
        " ON CONFLICT(id) DO UPDATE SET ord=excluded.ord,"
        " category=excluded.category, status=excluded.status,"
        " brand=excluded.brand, product=excluded.product,"
        " brand_group=excluded.brand_group,"
        " brand_status=excluded.brand_status, data=excluded.data",
        (eid, ordv, cat, status, brand, product, bgroup, bstatus,
         json.dumps(entry, ensure_ascii=False)))
    conn.commit()


def delete_entry(conn, entry_id):
    conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
    conn.commit()


def find_entries(conn, **filters):
    """filters: any of category, status, brand, product, brand_group,
    brand_status (exact match on the extracted columns). Returns full
    entry dicts in export order."""
    bad = set(filters) - set(ENTRY_FILTER_COLS)
    if bad:
        raise ValueError(f"unfilterable columns: {sorted(bad)}")
    sql = "SELECT data FROM entries"
    if filters:
        sql += " WHERE " + " AND ".join(f"{k} IS ?" if v is None else f"{k} = ?"
                                        for k, v in filters.items())
    sql += " ORDER BY ord"
    rows = conn.execute(sql, tuple(filters.values())).fetchall()
    return [json.loads(r["data"]) for r in rows]


def all_entries(conn):
    rows = conn.execute("SELECT data FROM entries ORDER BY ord").fetchall()
    return [json.loads(r["data"]) for r in rows]


# ---------------------------------------------------------------- queue

def next_queue(conn, n, states=("pending",)):
    """Next n queue items in seq order whose state is in `states`."""
    ph = ",".join("?" * len(states))
    rows = conn.execute(
        f"SELECT data FROM queue WHERE state IN ({ph})"
        " ORDER BY seq, ord LIMIT ?", (*states, n)).fetchall()
    return [json.loads(r["data"]) for r in rows]


def get_queue_item(conn, queue_id):
    row = conn.execute("SELECT data FROM queue WHERE queue_id = ?",
                       (queue_id,)).fetchone()
    return json.loads(row["data"]) if row else None


def queue_by_ref(conn, ref):
    rows = conn.execute("SELECT data FROM queue WHERE ref = ? ORDER BY seq",
                        (ref,)).fetchall()
    return [json.loads(r["data"]) for r in rows]


def update_queue(conn, item):
    """Insert or replace one queue item dict. Commits."""
    qid = item["queue_id"]
    row = conn.execute("SELECT ord FROM queue WHERE queue_id = ?",
                       (qid,)).fetchone()
    if row is not None:
        ordv = row["ord"]
    else:
        ordv = conn.execute(
            "SELECT COALESCE(MAX(ord), -1) + 1 AS n FROM queue").fetchone()["n"]
    conn.execute(
        "INSERT INTO queue(queue_id, ord, kind, ref, state, seq, data)"
        " VALUES (?,?,?,?,?,?,?)"
        " ON CONFLICT(queue_id) DO UPDATE SET ord=excluded.ord,"
        " kind=excluded.kind, ref=excluded.ref, state=excluded.state,"
        " seq=excluded.seq, data=excluded.data",
        (qid, ordv, item.get("kind"), item.get("ref"), item.get("state"),
         item.get("seq"), json.dumps(item, ensure_ascii=False)))
    conn.commit()


def all_queue(conn):
    rows = conn.execute("SELECT data FROM queue ORDER BY ord").fetchall()
    return [json.loads(r["data"]) for r in rows]


# ---------------------------------------------------------------- brands

def get_brand(conn, brand_id):
    row = conn.execute("SELECT data FROM brands WHERE brand_id = ?",
                       (brand_id,)).fetchone()
    return json.loads(row["data"]) if row else None


def upsert_brand(conn, brand):
    bid = brand["brand_id"]
    row = conn.execute("SELECT ord FROM brands WHERE brand_id = ?",
                       (bid,)).fetchone()
    if row is not None:
        ordv = row["ord"]
    else:
        ordv = conn.execute(
            "SELECT COALESCE(MAX(ord), -1) + 1 AS n FROM brands").fetchone()["n"]
    conn.execute(
        "INSERT INTO brands(brand_id, ord, data) VALUES (?,?,?)"
        " ON CONFLICT(brand_id) DO UPDATE SET ord=excluded.ord,"
        " data=excluded.data",
        (bid, ordv, json.dumps(brand, ensure_ascii=False)))
    conn.commit()


def all_brands(conn):
    rows = conn.execute("SELECT data FROM brands ORDER BY ord").fetchall()
    return [json.loads(r["data"]) for r in rows]


# ---------------------------------------------------------------- candidates

def all_candidates(conn):
    rows = conn.execute("SELECT data FROM candidates ORDER BY idx").fetchall()
    return [json.loads(r["data"]) for r in rows]


def upsert_candidate(conn, cand):
    idx = cand["index"]
    conn.execute(
        "INSERT INTO candidates(idx, data) VALUES (?,?)"
        " ON CONFLICT(idx) DO UPDATE SET data=excluded.data",
        (idx, json.dumps(cand, ensure_ascii=False)))
    conn.commit()


# ---------------------------------------------------------------- counts

def counts(conn):
    out = {}
    out["entries_total"] = conn.execute(
        "SELECT COUNT(*) AS n FROM entries").fetchone()["n"]
    out["entries_by_status"] = {
        r["status"]: r["n"] for r in conn.execute(
            "SELECT status, COUNT(*) AS n FROM entries GROUP BY status")}
    out["entries_by_category_status"] = {
        (r["category"], r["status"]): r["n"] for r in conn.execute(
            "SELECT category, status, COUNT(*) AS n FROM entries"
            " GROUP BY category, status")}
    out["queue_total"] = conn.execute(
        "SELECT COUNT(*) AS n FROM queue").fetchone()["n"]
    out["queue_by_state"] = {
        r["state"]: r["n"] for r in conn.execute(
            "SELECT state, COUNT(*) AS n FROM queue GROUP BY state")}
    out["brands_total"] = conn.execute(
        "SELECT COUNT(*) AS n FROM brands").fetchone()["n"]
    out["candidates_total"] = conn.execute(
        "SELECT COUNT(*) AS n FROM candidates").fetchone()["n"]
    return out


# ---------------------------------------------------------------- export

def _atomic_write_json(path, obj):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ---------------------------------------------------------------- merged catalog shards

MERGED_CATEGORIES = ('aftershave', 'blade', 'brush', 'fragrance',
                     'knot', 'razor', 'soap')
MERGED_SHARD_DIRNAME = 'catalog_merged'


def merged_shard_dir(cat_dir=HERE):
    return os.path.join(cat_dir, MERGED_SHARD_DIRNAME)


def _write_merged_shards(meta, entries, out_dir=HERE):
    """Write the merged catalog as one shard per category under
    <out_dir>/catalog_merged/<category>.json. Each shard keeps the same
    doc shape as the old single file (per-file metadata restored
    verbatim, entry_count refreshed per shard, entries = that category's
    entries, indent=1). All 7 shards are always written, even empty ones,
    so the layout is stable. Raises on an entry whose category is not
    one of the 7 — never silently drop an entry."""
    shard_dir = merged_shard_dir(out_dir)
    os.makedirs(shard_dir, exist_ok=True)
    by_cat = {c: [] for c in MERGED_CATEGORIES}
    for e in entries:
        cat = e.get('category')
        if cat not in by_cat:
            raise ValueError(
                f"entry {e.get('id')} has unknown category {cat!r}; "
                "refusing to shard")
        by_cat[cat].append(e)
    for cat in MERGED_CATEGORIES:
        doc = dict(meta)
        doc['entry_count'] = len(by_cat[cat])
        doc['entries'] = by_cat[cat]
        _atomic_write_json(os.path.join(shard_dir, cat + '.json'), doc)


def load_merged(cat_dir=HERE):
    """Load the sharded merged catalog. Returns the doc dict with the
    per-file metadata (from the first shard) and 'entries' concatenated
    in deterministic sorted-filename order."""
    shard_dir = merged_shard_dir(cat_dir)
    entries = []
    meta = None
    for name in sorted(os.listdir(shard_dir)):
        if not name.endswith('.json'):
            continue
        with open(os.path.join(shard_dir, name), encoding='utf-8') as f:
            doc = json.load(f)
        if meta is None:
            meta = {k: v for k, v in doc.items()
                    if k not in ('entries', 'entry_count')}
        entries.extend(doc['entries'])
    out = dict(meta or {})
    out['entry_count'] = len(entries)
    out['entries'] = entries
    return out


def save_merged_shards(doc, cat_dir=HERE):
    """Write a loaded merged doc back out as per-category shards. The
    doc's metadata (everything except entries/entry_count) is carried
    onto every shard."""
    meta = {k: v for k, v in doc.items()
            if k not in ('entries', 'entry_count')}
    _write_merged_shards(meta, doc['entries'], cat_dir)


def export_json(conn, out_dir=HERE):
    """Regenerate the JSON exports from the DB, in the exact shapes
    the files have always used. The merged catalog is written as
    per-category shards (see _write_merged_shards); the other exports
    are single files. The per-file non-list metadata saved at
    migration time is restored verbatim; count fields are refreshed from
    the DB. Returns a dict of the counts written."""
    written = {}

    meta = json.loads(get_meta(conn, "filemeta:catalog_merged.json") or "{}")
    entries = all_entries(conn)
    _write_merged_shards(meta, entries, out_dir)
    written["entries"] = len(entries)

    meta = json.loads(get_meta(conn, "filemeta:validation_queue.json") or "{}")
    items = all_queue(conn)
    doc = dict(meta)
    doc["count"] = len(items)
    doc["queue"] = items
    _atomic_write_json(os.path.join(out_dir, "validation_queue.json"), doc)
    written["queue"] = len(items)

    meta = json.loads(get_meta(conn, "filemeta:candidate_aliases.json") or "{}")
    cands = all_candidates(conn)
    doc = dict(meta)
    doc["candidates"] = cands
    _atomic_write_json(os.path.join(out_dir, "candidate_aliases.json"), doc)
    written["candidates"] = len(cands)

    meta = json.loads(get_meta(conn, "filemeta:brands.json") or "{}")
    groups = all_brands(conn)
    doc = dict(meta)
    doc["group_count"] = len(groups)
    doc["groups"] = groups
    _atomic_write_json(os.path.join(out_dir, "brands.json"), doc)
    written["brands"] = len(groups)

    return written
