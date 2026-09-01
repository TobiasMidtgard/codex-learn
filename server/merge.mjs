/**
 * merge.mjs — combine two progress documents without losing anything.
 *
 * Two devices are edited independently and neither is "the truth", so last-write-wins
 * would silently throw away whichever side synced first. Every field here has a rule
 * chosen so that a merge can only ever move progress forward:
 *
 *   completed  union            — a finished unit never becomes unfinished
 *   quiz       max per lesson   — the best score stands
 *   derive     furthest step    — progress through a derivation never rewinds
 *   activity   max per day      — each device counts its own work; max under-counts
 *                                 rather than double-counting a re-sync
 *   code       newest per lesson (by its `t` stamp)
 *   xp         max as a floor — the client recomputes the exact figure from
 *              `completed`, which it can do because it knows the XP table
 *   scalars    from whichever document was saved more recently
 *
 * The result is order-independent: merge(a, b) and merge(b, a) agree on everything
 * except the scalars, which are decided by `updatedAt`.
 *
 * `clearedAt` is the one exception, and it exists because every rule above moves progress
 * forward and never back — which is right for two devices both doing work, and wrong for
 * the single action whose entire purpose is to remove it. "Reset progress" cleared the
 * local copy, pushed it, and the union handed all of it straight back about two seconds
 * later, with the toast still on screen saying it had been cleared. Import had the same
 * shape: it replaced P locally and merged remotely, so "Restored 1 completed unit" left
 * an account holding three.
 *
 * A document carries `clearedAt` when its owner cleared or replaced it wholesale. Both
 * sides take the larger of the two, and any document whose own `updatedAt` predates that
 * moment was written before the clear and is discarded; one saved after it is real work
 * done since, and is kept. Still order-independent, because both sides compute the same
 * `clearedAt` and are tested against it rather than against each other.
 */

const SCALARS = ['name', 'theme', 'symbols', 'railHidden', 'last'];

function obj(v) {
  return v && typeof v === 'object' && !Array.isArray(v) ? v : {};
}

function unionTrue(a, b) {
  const out = {};
  for (const k of Object.keys(obj(a))) if (a[k]) out[k] = true;
  for (const k of Object.keys(obj(b))) if (b[k]) out[k] = true;
  return out;
}

function maxNumbers(a, b) {
  const out = {};
  a = obj(a); b = obj(b);
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = Number(a[k]) || 0;
    const y = Number(b[k]) || 0;
    out[k] = Math.max(x, y);
  }
  return out;
}

function newestPerKey(a, b) {
  const out = {};
  a = obj(a); b = obj(b);
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = a[k], y = b[k];
    if (!x) { out[k] = y; continue; }
    if (!y) { out[k] = x; continue; }
    out[k] = (Number(y.t) || 0) >= (Number(x.t) || 0) ? y : x;
  }
  return out;
}

function mergeSlots(a, b) {
  const out = {};
  a = obj(a); b = obj(b);
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    out[k] = Object.assign({}, obj(a[k]), obj(b[k]));
  }
  return out;
}

function newestWhole(a, b) {
  const out = {};
  a = obj(a); b = obj(b);
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) out[k] = b[k] || a[k];
  return out;
}

function furthestStep(a, b) {
  const out = {};
  a = obj(a); b = obj(b);
  for (const k of new Set([...Object.keys(a), ...Object.keys(b)])) {
    const x = Number((a[k] || {}).done) || 0;
    const y = Number((b[k] || {}).done) || 0;
    out[k] = y > x ? b[k] : (a[k] || b[k]);
  }
  return out;
}

export function mergeProgress(stored, incoming) {
  const kept = obj(stored);
  const sent = obj(incoming);
  /* A clear is a fact about a moment, not about a document, so both sides honour the
     latest one either of them has heard of — including the side that has never seen it,
     which is what makes a second device stop resurrecting what the first one erased. */
  const clearedAt = Math.max(Number(kept.clearedAt) || 0, Number(sent.clearedAt) || 0);
  const survives = (d) => ((Number(d.updatedAt) || 0) >= clearedAt ? d : {});
  const a = survives(kept);
  const b = survives(sent);
  const aTime = Number(a.updatedAt) || 0;
  const bTime = Number(b.updatedAt) || 0;
  const newer = bTime >= aTime ? b : a;

  const out = {
    completed: unionTrue(a.completed, b.completed),
    quiz: maxNumbers(a.quiz, b.quiz),
    /* a derivation only ever moves forward, so the furthest step wins */
    derive: furthestStep(a.derive, b.derive),
    /* a schematic is whole; the more recently edited one wins outright */
    build: newestWhole(a.build, b.build),
    /* a filled blank stays filled; the union keeps whichever side answered one */
    blanks: mergeSlots(a.blanks, b.blanks),
    /* a placed symbol and a tuned slider behave the same way */
    match: mergeSlots(a.match, b.match),
    numeric: newestWhole(a.numeric, b.numeric),
    tune: newestWhole(a.tune, b.tune),
    activity: maxNumbers(a.activity, b.activity),
    code: newestPerKey(a.code, b.code),
    xp: Math.max(Number(a.xp) || 0, Number(b.xp) || 0),
    playground: newer.playground ?? a.playground ?? b.playground ?? null,
    updatedAt: Math.max(aTime, bTime),
    clearedAt: clearedAt,
  };
  /* A device signing in for the first time carries a blank name and a fresh
     `updatedAt`, so "newest wins" alone would let its emptiness erase a real value.
     An unset field never overwrites a set one; `false` and `0` count as set. */
  const older = newer === b ? a : b;
  const isSet = (v) => v !== undefined && v !== null && v !== '';
  for (const k of SCALARS) {
    out[k] = isSet(newer[k]) ? newer[k] : (isSet(older[k]) ? older[k] : (newer[k] ?? older[k] ?? null));
  }
  return out;
}
