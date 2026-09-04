from __future__ import annotations
import argparse, asyncio, json, time
from collections import Counter
from dataclasses import asdict
from security import generate_keypair, sign_proposal
try:
    import websockets
except ImportError:
    websockets = None

async def one_client(url, client_id, messages, faults, results):
    if websockets is None: results.append('missing_dependency'); return
    private_key, _ = generate_keypair()
    try:
        async with websockets.connect(url, open_timeout=10, close_timeout=2, max_size=1_000_000) as ws:
            ready = await asyncio.wait_for(ws.recv(), 10); results.append('ready' if 'ready' in ready else 'unexpected')
            for i in range(messages):
                if faults == 'malformed' and i == 0: frame = '{not-json'
                elif faults == 'stale' and i == 0: frame = json.dumps({'node_id':client_id,'timestamp':1})
                elif faults == 'duplicate' and i == 0:
                    frame = json.dumps({'node_id':client_id,'payload':{'i':i},'timestamp':int(time.time()),'nonce':'same','public_key':'bad','signature':'bad','digest':'bad'})
                elif faults == 'equivocation' and i < 2: frame = json.dumps({'node_id':client_id,'status':'open' if i else 'proven','timestamp':int(time.time()),'nonce':f'{client_id}-{i}'})
                else: frame = json.dumps(asdict(sign_proposal(client_id, {'sequence': i}, private_key)))
                await ws.send(frame)
                try:
                    reply = await asyncio.wait_for(ws.recv(), 3)
                    results.append('rejected' if 'rejected' in reply else 'proposal')
                except asyncio.TimeoutError: results.append('timeout')
    except Exception as exc: results.append(type(exc).__name__)

async def run(url, clients=10, messages=5, faults='none'):
    results=[]; started=time.perf_counter()
    await asyncio.gather(*(one_client(url, f'load-{i}', messages, faults, results) for i in range(clients)))
    elapsed=time.perf_counter()-started
    return {'url':url,'clients':clients,'messages_per_client':messages,'fault_mode':faults,'elapsed_seconds':round(elapsed,4),'events':len(results),'outcomes':dict(Counter(results)),'throughput_events_per_second':round(len(results)/elapsed,2) if elapsed else 0}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--url',default='wss://four-leibniz-consensus.chyren-sovereign.workers.dev/ws/loadtest'); p.add_argument('--clients',type=int,default=10); p.add_argument('--messages',type=int,default=5); p.add_argument('--faults',choices=['none','malformed','stale','duplicate','equivocation'],default='none'); p.add_argument('--output')
    args=p.parse_args(); result=asyncio.run(run(args.url,args.clients,args.messages,args.faults)); text=json.dumps(result,indent=2)
    print(text)
    if args.output: open(args.output,'w').write(text+'\n')
if __name__=='__main__': main()
