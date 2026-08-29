/**
 * auth.mjs — password hashing, session tokens, and login throttling.
 *
 * Deliberately dependency-free: everything here is node:crypto.
 */

import { randomBytes, scrypt as scryptCb, timingSafeEqual, createHash } from 'node:crypto';
import { promisify } from 'node:util';

const scrypt = promisify(scryptCb);

/* Cost parameters. N must stay a power of two; raising it invalidates nothing
   because the parameters are stored alongside each hash. */
const N = 16384, r = 8, p = 1, KEYLEN = 64;
const SALT_BYTES = 16;
const TOKEN_BYTES = 32;

export const SESSION_TTL_MS = 30 * 24 * 60 * 60 * 1000;   /* 30 days, slid on use */

export async function hashPassword(password) {
  const salt = randomBytes(SALT_BYTES);
  const key = await scrypt(password, salt, KEYLEN, { N, r, p, maxmem: 64 * 1024 * 1024 });
  return ['scrypt', N, r, p, salt.toString('base64'), key.toString('base64')].join('$');
}

export async function verifyPassword(password, stored) {
  try {
    const [kind, sN, sr, sp, saltB64, keyB64] = String(stored).split('$');
    if (kind !== 'scrypt') return false;
    const salt = Buffer.from(saltB64, 'base64');
    const expected = Buffer.from(keyB64, 'base64');
    const got = await scrypt(password, salt, expected.length, {
      N: Number(sN), r: Number(sr), p: Number(sp), maxmem: 64 * 1024 * 1024,
    });
    /* constant time: a length mismatch is answered without leaking where */
    if (got.length !== expected.length) return false;
    return timingSafeEqual(got, expected);
  } catch {
    return false;
  }
}

/* The raw token is handed to the client once and never stored; the server keeps
   only its digest, so a copy of the data directory cannot be used to log in. */
export function newToken() {
  const raw = randomBytes(TOKEN_BYTES).toString('base64url');
  return { raw, hash: hashToken(raw) };
}

export function hashToken(raw) {
  return createHash('sha256').update(String(raw)).digest('hex');
}

/* ---- login throttling ----
   Per-key sliding window. Keys are "<ip>" for registration and "<ip>:<email>" for
   login, so one attacker cannot lock every account off a shared address. */
const WINDOW_MS = 15 * 60 * 1000;
const MAX_ATTEMPTS = 10;
const attempts = new Map();

export function throttle(key, now = Date.now()) {
  const list = (attempts.get(key) || []).filter((t) => now - t < WINDOW_MS);
  if (list.length >= MAX_ATTEMPTS) {
    attempts.set(key, list);
    return { allowed: false, retryAfterMs: WINDOW_MS - (now - list[0]) };
  }
  list.push(now);
  attempts.set(key, list);
  if (attempts.size > 5000) {
    for (const [k, v] of attempts) if (!v.some((t) => now - t < WINDOW_MS)) attempts.delete(k);
  }
  return { allowed: true };
}

export function throttleClear(key) {
  attempts.delete(key);
}

/* ---- validation ---- */
export function normalizeEmail(email) {
  return String(email || '').trim().toLowerCase();
}

export function validateCredentials(email, password) {
  const e = normalizeEmail(email);
  if (e.length < 3 || e.length > 254 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e)) {
    return 'Enter a valid email address.';
  }
  const pw = String(password ?? '');
  if (pw.length < 8) return 'Use a password of at least 8 characters.';
  if (pw.length > 200) return 'That password is too long.';
  return null;
}
