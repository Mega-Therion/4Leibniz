export class ConsensusRoom {
  constructor(state) { this.state = state; this.sessions = new Set(); }
  async fetch(request) {
    if (request.headers.get('Upgrade') !== 'websocket') return new Response('Consensus room online', {status: 200});
    const pair = new WebSocketPair(); const [client, server] = Object.values(pair); server.accept();
    this.sessions.add(server); server.addEventListener('close', () => this.sessions.delete(server));
    server.send(JSON.stringify({event:'ready', room:this.state.id?.toString?.() || 'consensus'}));
    server.addEventListener('message', event => {
      // Production: verify Ed25519 envelope, enforce room authorization, persist event, then broadcast.
      for (const peer of this.sessions) if (peer.readyState === 1) peer.send(event.data);
    });
    return new Response(null, {status: 101, webSocket: client});
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === '/health') return Response.json({ok:true, service:'4Leibniz consensus edge'});
    if (url.pathname.startsWith('/ws/')) {
      const room = url.pathname.split('/').filter(Boolean)[1] || 'default';
      const id = env.CONSENSUS_ROOM.idFromName(room);
      return env.CONSENSUS_ROOM.get(id).fetch(request);
    }
    return new Response('Deploy the dashboard separately; this Worker owns the consensus edge.', {status: 404});
  }
};
