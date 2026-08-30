/* Minimal static server for the built app. node tools/serve.mjs [port] */
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname, dirname, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..', 'build');
const PORT = Number(process.argv[2] || 4173);
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
};

createServer(async (req, res) => {
  /* decodeURIComponent throws on a malformed escape such as `/%`. Pre-existing. */
  let path;
  try { path = decodeURIComponent((req.url || '/').split('?')[0]); }
  catch { path = (req.url || '/').split('?')[0]; }
  /* '/' is the SPLIT build, the same shape GitHub Pages publishes, so a local preview
     actually exercises the payload fetches. The inlined single file stays reachable at
     /codewright.html for the open-it-from-disk check. */
  if (path === '/' || path === '') path = '/index.html';
  const file = normalize(join(ROOT, path));
  /* startsWith alone lets a sibling directory whose name merely begins with the
     root's name through; compare on a separator boundary. Pre-existing. */
  if (file !== ROOT && !file.startsWith(ROOT + sep)) { res.writeHead(403).end('forbidden'); return; }
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
}).listen(PORT, () => console.log(`codewright on http://localhost:${PORT}`));
