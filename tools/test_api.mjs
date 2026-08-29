/**
 * test_api.mjs — end-to-end exercise of the account + sync API.
 *
 *   node tools/test_api.mjs [baseUrl]     default http://localhost:4180
 *
 * Runs against a real server with a throwaway data directory:
 *   CODEX_DATA_DIR=... node server/server.mjs 4180
 */

const BASE = process.argv[2] || 'http://localhost:4180';

let pass = 0, fail = 0;
function ok(name, cond, detail) {
  if (cond) { pass++; console.log('  ok   ' + name); }
  else { fail++; console.log('  FAIL ' + name + (detail ? '  -> ' + JSON.stringify(detail) : '')); }
}

async function call(path, method, body, token) {
  const headers = {};
  if (body !== undefined) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = 'Bearer ' + token;
  const res = await fetch(BASE + path, {
    method, headers, body: body === undefined ? undefined : JSON.stringify(body),
  });
  let data = null;
  try { data = await res.json(); } catch {}
  return { status: res.status, data };
}

const stamp = Date.now();
const emailA = `a${stamp}@example.com`;
const emailB = `b${stamp}@example.com`;
const PW = 'correct horse battery';

console.log('API tests against ' + BASE);

/* --- health --- */
{
  const r = await call('/api/health', 'GET');
  ok('health responds', r.status === 200 && r.data.ok === true, r.data);
}

/* --- validation --- */
{
  const r = await call('/api/register', 'POST', { email: 'not-an-email', password: PW });
  ok('rejects a malformed email', r.status === 400, r);
  const r2 = await call('/api/register', 'POST', { email: emailA, password: 'short' });
  ok('rejects a short password', r2.status === 400, r2);
}

/* --- register --- */
let tokenA;
{
  const r = await call('/api/register', 'POST', { email: emailA, password: PW });
  ok('registers a new account', r.status === 201 && !!r.data.token, r);
  ok('never returns the password hash', !JSON.stringify(r.data).includes('scrypt'), r.data);
  tokenA = r.data.token;
  const dup = await call('/api/register', 'POST', { email: emailA, password: PW });
  ok('refuses a duplicate email', dup.status === 409, dup);
}

/* --- login --- */
let tokenA2;
{
  const bad = await call('/api/login', 'POST', { email: emailA, password: PW + 'x' });
  ok('rejects a wrong password', bad.status === 401, bad);
  const unknown = await call('/api/login', 'POST', { email: 'nobody' + stamp + '@example.com', password: PW });
  ok('same answer for an unknown email (no account enumeration)',
     unknown.status === 401 && unknown.data.error === bad.data.error, { bad: bad.data, unknown: unknown.data });
  const good = await call('/api/login', 'POST', { email: emailA, password: PW });
  ok('signs in with the right password', good.status === 200 && !!good.data.token, good);
  tokenA2 = good.data.token;
  ok('a second sign-in issues a distinct token', tokenA2 !== tokenA);
}

/* --- auth required --- */
{
  const none = await call('/api/progress', 'GET');
  ok('progress needs a token', none.status === 401, none);
  const junk = await call('/api/progress', 'GET', undefined, 'not-a-real-token');
  ok('a forged token is refused', junk.status === 401, junk);
}

/* --- sync + merge --- */
{
  const deviceOne = {
    completed: { 'py-1-1': true, 'py-1-2': true },
    quiz: { 'py-1-3': 60 },
    activity: { '2026-08-20': 2 },
    code: { 'py-1-2': { files: { 'main.py': 'print(1)' }, hints: 0, t: 1000 } },
    xp: 50, name: 'Device One', updatedAt: 1000,
  };
  const r1 = await call('/api/progress', 'PUT', { progress: deviceOne }, tokenA);
  ok('first device stores its progress', r1.status === 200 && r1.data.progress.completed['py-1-1'], r1.data);

  const deviceTwo = {
    completed: { 'py-1-1': true, 'py-2-1': true },
    quiz: { 'py-1-3': 85 },
    activity: { '2026-08-20': 1, '2026-08-21': 4 },
    code: { 'py-1-2': { files: { 'main.py': 'print(2)' }, hints: 1, t: 2000 } },
    xp: 40, name: 'Device Two', updatedAt: 2000,
  };
  const r2 = await call('/api/progress', 'PUT', { progress: deviceTwo }, tokenA2);
  const m = r2.data.progress;
  ok('completed units are unioned',
     m.completed['py-1-1'] && m.completed['py-1-2'] && m.completed['py-2-1'], m.completed);
  ok('the better quiz score survives', m.quiz['py-1-3'] === 85, m.quiz);
  ok('activity takes the higher count per day',
     m.activity['2026-08-20'] === 2 && m.activity['2026-08-21'] === 4, m.activity);
  ok('the newer saved code wins', m.code['py-1-2'].files['main.py'] === 'print(2)', m.code);
  ok('xp is a floor, never a loss', m.xp === 50, m.xp);
  ok('the later device settles scalar fields', m.name === 'Device Two', m.name);
  ok('the revision advances', r2.data.rev > r1.data.rev, { a: r1.data.rev, b: r2.data.rev });

  /* device one now pulls and sees everything */
  const back = await call('/api/progress', 'GET', undefined, tokenA);
  ok('the first device reads the merged result',
     back.data.progress.completed['py-2-1'] === true, back.data.progress.completed);

  const badDoc = await call('/api/progress', 'PUT', { progress: { nope: 1 } }, tokenA);
  ok('a document without `completed` is refused', badDoc.status === 400, badDoc);

  /* A machine signing in for the first time is empty but has the newest clock. It
     must not blank out fields the account already holds. */
  const freshDevice = {
    completed: {}, quiz: {}, activity: {}, code: {},
    xp: 0, name: '', last: null, updatedAt: Date.now() + 60000,
  };
  const r3 = await call('/api/progress', 'PUT', { progress: freshDevice }, tokenA);
  ok('a blank new device does not erase the account name', r3.data.progress.name === 'Device Two', r3.data.progress.name);
  ok('a blank new device does not erase completed units',
     Object.keys(r3.data.progress.completed).length === 3, r3.data.progress.completed);
  ok('a blank new device does not erase xp', r3.data.progress.xp === 50, r3.data.progress.xp);
}

/* --- isolation between accounts --- */
{
  const r = await call('/api/register', 'POST', { email: emailB, password: PW });
  const tokenB = r.data.token;
  const mine = await call('/api/progress', 'GET', undefined, tokenB);
  ok('a new account starts empty (no cross-account leak)',
     mine.data.progress === null || Object.keys(mine.data.progress.completed || {}).length === 0, mine.data);
}

/* --- logout --- */
{
  const out = await call('/api/logout', 'POST', {}, tokenA);
  ok('signs out', out.status === 200, out);
  const after = await call('/api/progress', 'GET', undefined, tokenA);
  ok('the revoked token stops working', after.status === 401, after);
  const other = await call('/api/progress', 'GET', undefined, tokenA2);
  ok('the other session on that account still works', other.status === 200, other.status);
}

/* --- throttling --- */
{
  const email = 'throttle' + stamp + '@example.com';
  await call('/api/register', 'POST', { email, password: PW });
  let sawLimit = false;
  for (let i = 0; i < 14; i++) {
    const r = await call('/api/login', 'POST', { email, password: 'wrong-password-here' });
    if (r.status === 429) { sawLimit = true; break; }
  }
  ok('repeated wrong passwords get throttled', sawLimit);
}

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
