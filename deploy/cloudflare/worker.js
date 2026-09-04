const MAX_AGE_SECONDS = 300;

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') return Object.keys(value).sort().reduce((o, k) => { o[k] = stable(value[k]); return o; }, {});
  return value;
}
function canonical(value) { return JSON.stringify(stable(value)); }
function bytes(text) { return new TextEncoder().encode(text); }
function fromB64(text) { const raw = atob(text.replace(/-/g, '+').replace(/_/g, '/') + '='.repeat((4 - text.length % 4) % 4)); return Uint8Array.from(raw, c => c.charCodeAt(0)); }
async function sha256Hex(text) { const digest = await crypto.subtle.digest('SHA-256', bytes(text)); return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, '0')).join(''); }

async function verifyEnvelope(envelope, state) {
  const {node_id, payload, public_key, signature, digest, timestamp, nonce} = envelope || {};
  if (!node_id || !public_key || !signature || !digest || !nonce || !Number.isInteger(timestamp)) return {ok:false, reason:'malformed envelope'};
  if (Math.abs(Math.floor(Date.now()/1000) - timestamp) > MAX_AGE_SECONDS) return {ok:false, reason:'stale timestamp'};
  const message = {node_id, payload, timestamp, nonce};
  const text = canonical(message);
  if (await sha256Hex(text) !== digest) return {ok:false, reason:'digest mismatch'};
  try {
    const key = await crypto.subtle.importKey('raw', fromB64(public_key), {name:'Ed25519'}, false, ['verify']);
    const valid = await crypto.subtle.verify({name:'Ed25519'}, key, fromB64(signature), bytes(text));
    if (!valid) return {ok:false, reason:'signature invalid'};
  } catch (_) { return {ok:false, reason:'signature key rejected'}; }
  const replayKey = `nonce:${node_id}:${nonce}`;
  if (await state.storage.get(replayKey)) return {ok:false, reason:'replayed nonce'};
  await state.storage.put(replayKey, {seen_at: Math.floor(Date.now()/1000)}, {expirationTtl: MAX_AGE_SECONDS});
  return {ok:true};
}

export class ConsensusRoom {
  constructor(state) { this.state = state; this.sessions = new Set(); }
  async fetch(request) {
    if (request.headers.get('Upgrade') !== 'websocket') return new Response('Consensus room online', {status: 200});
    const pair = new WebSocketPair(); const [client, server] = Object.values(pair); server.accept();
    this.sessions.add(server); server.addEventListener('close', () => this.sessions.delete(server));
    server.send(JSON.stringify({event:'ready', room:'consensus', security:'ed25519+freshness+nonce'}));
    server.addEventListener('message', event => {
      let envelope; try { envelope = JSON.parse(event.data); } catch (_) { server.send(JSON.stringify({event:'rejected', reason:'invalid json'})); return; }
      verifyEnvelope(envelope, this.state).then(result => {
        if (!result.ok) { server.send(JSON.stringify({event:'rejected', reason:result.reason})); return; }
        const message = JSON.stringify({event:'proposal', envelope});
        for (const peer of this.sessions) if (peer.readyState === 1) peer.send(message);
      });
    });
    return new Response(null, {status: 101, webSocket: client});
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/health') return Response.json({ok:true, service:'4Leibniz consensus edge', security:['ed25519','timestamp-freshness','nonce-replay-protection']});
    if (url.pathname.startsWith('/ws/')) {
      const room = url.pathname.split('/').filter(Boolean)[1] || 'default';
      const id = env.CONSENSUS_ROOM.idFromName(room);
      return env.CONSENSUS_ROOM.get(id).fetch(request);
    }
    return new Response('Deploy the dashboard separately; this Worker owns the consensus edge.', {status: 404});
  }
};
