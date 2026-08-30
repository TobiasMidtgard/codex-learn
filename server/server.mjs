/**
 * server.mjs — serves the built app and the sync API.
 *
 *   node server/server.mjs [port]      default 4173
 *
 * The app stays a working single file with no server: this only adds the account
 * that lets one learner's progress follow them between machines. Everything the
 * client does against it degrades to local-only when it is not reachable.
 *
 * Auth is a bearer token, not a cookie, so the app also works when it is opened
 * from a different origin — and because no credential is sent ambiently, there is
 * no CSRF surface to defend.
 */

import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, dirname, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  hashPassword, verifyPassword, newToken, throttle, throttleClear,
  normalizeEmail, validateCredentials,
} from './auth.mjs';
import {
  findByEmail, createUser, addSession, findBySession, dropSession,
  updateProgress, getUser, publicUser, DATA_DIR,
} from './store.mjs';
import { mergeProgress } from './merge.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BUILD = join(ROOT, 'build');
const PORT = Number(process.argv[2] || process.env.PORT || 4173);

const MAX_BODY = 2 * 1024 * 1024;          /* a progress document is a few hundred KB */
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
};

/* ------------------------------------------------------------------ helpers */
function send(res, code, obj, extra) {
  const body = JSON.stringify(obj);
  res.writeHead(code, Object.assign({
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  }, extra || {}));
  res.end(body);
}

function cors(req, res) {
  /* The token lives in the Authorization header, never in a cookie, so reflecting
     the origin grants a reader nothing it could not get by asking for the token. */
  const origin = req.headers.origin;
  if (origin) res.setHeader('Access-Control-Allow-Origin', origin);
  res.setHeader('Vary', 'Origin');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, OPTIONS');
  res.setHeader('Access-Control-Max-Age', '86400');
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on('data', (c) => {
      size += c.length;
      if (size > MAX_BODY) { reject(new Error('too large')); req.destroy(); return; }
      chunks.push(c);
    });
    req.on('end', () => {
      if (!chunks.length) { resolve({}); return; }
      try { resolve(JSON.parse(Buffer.concat(chunks).toString('utf8'))); }
      catch { reject(new Error('bad json')); }
    });
    req.on('error', reject);
  });
}

function clientIp(req) {
  return String(req.socket.remoteAddress || 'unknown');
}

function bearer(req) {
  const h = String(req.headers.authorization || '');
  return h.startsWith('Bearer ') ? h.slice(7).trim() : '';
}

async function requireUser(req, res) {
  const token = bearer(req);
  if (!token) { send(res, 401, { error: 'Sign in to sync.' }); return null; }
  const found = await findBySession(token);
  if (!found) { send(res, 401, { error: 'That session has expired — sign in again.' }); return null; }
  return { ...found, token };
}

/* ------------------------------------------------------------------- routes */
async function api(req, res, path) {
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }

  if (path === '/api/health' && req.method === 'GET') {
    send(res, 200, { ok: true, service: 'codex-learn', accounts: true });
    return;
  }

  if (path === '/api/register' && req.method === 'POST') {
    const gate = throttle('reg:' + clientIp(req));
    if (!gate.allowed) { send(res, 429, { error: 'Too many attempts. Try again later.' }); return; }
    const body = await readBody(req);
    const email = normalizeEmail(body.email);
    const bad = validateCredentials(email, body.password);
    if (bad) { send(res, 400, { error: bad }); return; }
    if (await findByEmail(email)) {
      send(res, 409, { error: 'That email already has an account — sign in instead.' });
      return;
    }
    const user = await createUser(email, await hashPassword(body.password));
    if (!user) { send(res, 409, { error: 'That email already has an account.' }); return; }
    const tok = newToken();
    await addSession(user.id, tok.hash, String(body.device || '').slice(0, 60));
    send(res, 201, { token: tok.raw, user: publicUser(user) });
    return;
  }

  if (path === '/api/login' && req.method === 'POST') {
    const body = await readBody(req);
    const email = normalizeEmail(body.email);
    const gate = throttle('login:' + clientIp(req) + ':' + email);
    if (!gate.allowed) {
      send(res, 429, { error: 'Too many sign-in attempts. Try again in a few minutes.' });
      return;
    }
    const user = await findByEmail(email);
    /* Same answer either way: whether an email is registered is not public. */
    const ok = user ? await verifyPassword(String(body.password ?? ''), user.passwordHash) : false;
    if (!ok) { send(res, 401, { error: 'That email and password do not match.' }); return; }
    throttleClear('login:' + clientIp(req) + ':' + email);
    const tok = newToken();
    await addSession(user.id, tok.hash, String(body.device || '').slice(0, 60));
    send(res, 200, { token: tok.raw, user: publicUser(user) });
    return;
  }

  if (path === '/api/logout' && req.method === 'POST') {
    const auth = await requireUser(req, res);
    if (!auth) return;
    await dropSession(auth.user.id, auth.token);
    send(res, 200, { ok: true });
    return;
  }

  if (path === '/api/me' && req.method === 'GET') {
    const auth = await requireUser(req, res);
    if (!auth) return;
    const fresh = await getUser(auth.user.id);
    send(res, 200, { user: publicUser(fresh), rev: fresh.rev || 0, progressAt: fresh.progressAt || 0 });
    return;
  }

  if (path === '/api/progress' && req.method === 'GET') {
    const auth = await requireUser(req, res);
    if (!auth) return;
    const fresh = await getUser(auth.user.id);
    send(res, 200, { progress: fresh.progress, rev: fresh.rev || 0, progressAt: fresh.progressAt || 0 });
    return;
  }

  if (path === '/api/progress' && req.method === 'PUT') {
    const auth = await requireUser(req, res);
    if (!auth) return;
    let body;
    try { body = await readBody(req); }
    catch (e) {
      send(res, 413, { error: String(e.message) === 'too large' ? 'That progress file is too large.' : 'Malformed request.' });
      return;
    }
    const incoming = body && body.progress;
    if (!incoming || typeof incoming !== 'object' || typeof incoming.completed !== 'object') {
      send(res, 400, { error: 'That does not look like a progress document.' });
      return;
    }
    /* Merging inside the store's per-user chain is what makes two devices syncing at
       the same moment safe: each merge sees the other's result, never a stale copy. */
    const saved = await updateProgress(auth.user.id, (stored) => mergeProgress(stored, incoming));
    if (!saved) { send(res, 404, { error: 'Account not found.' }); return; }
    send(res, 200, { progress: saved.progress, rev: saved.rev, progressAt: saved.progressAt });
    return;
  }

  send(res, 404, { error: 'No such endpoint.' });
}

/* ------------------------------------------------------------------- static */
async function serveStatic(req, res, path) {
  /* '/' is the SPLIT build, the same shape GitHub Pages publishes, so a local preview
     actually exercises the payload fetches. The inlined single file stays reachable at
     /codewright.html for the open-it-from-disk check. */
  if (path === '/' || path === '') path = '/index.html';
  const file = normalize(join(BUILD, path));
  /* startsWith alone lets a sibling directory whose name merely begins with the
     root's name through; compare on a separator boundary. Pre-existing. */
  if (file !== BUILD && !file.startsWith(BUILD + sep)) { res.writeHead(403).end('forbidden'); return; }
  try {
    await stat(file);
    const body = await readFile(file);
    res.writeHead(200, {
      'Content-Type': TYPES[extname(file)] || 'application/octet-stream',
      'Cache-Control': 'no-store',
    });
    res.end(body);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain' }).end('not found');
  }
}

createServer(async (req, res) => {
  /* decodeURIComponent throws on a malformed escape such as `/%`, and this is
     outside the try below, in an async handler — so one bad request became an
     unhandled rejection and took the whole process down. Pre-existing; it
     matters more now that the app itself requests generated paths. */
  let path;
  try { path = decodeURIComponent((req.url || '/').split('?')[0]); }
  catch { path = (req.url || '/').split('?')[0]; }
  cors(req, res);
  try {
    if (path.startsWith('/api/')) await api(req, res, path);
    else await serveStatic(req, res, path);
  } catch (e) {
    /* never leak a stack to the client, and never log a request body */
    console.error('[codex-learn]', req.method, path, '->', e && e.message);
    if (!res.headersSent) send(res, 500, { error: 'Something went wrong on the server.' });
    else res.end();
  }
}).listen(PORT, () => {
  console.log(`codex-learn on http://localhost:${PORT}`);
  console.log(`accounts and progress in ${DATA_DIR}`);
});
