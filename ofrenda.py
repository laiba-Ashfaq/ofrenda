#!/usr/bin/env python3
"""Ofrenda: a local, offline remembrance writer. Open-weight model via Ollama. Stdlib only."""
import json, os, re, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

OLLAMA = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
MODEL = os.environ.get("OFRENDA_MODEL", "llama3.2")
PORT = int(os.environ.get("PORT", 8731))
DATA = Path(os.environ.get("OFRENDA_DIR", "ofrenda_data"))
DATA.mkdir(exist_ok=True)

ASK_SYS = ("You are a gentle oral-history interviewer helping someone remember a loved one who has died. "
           "Ask exactly ONE short, warm question that draws out a sensory detail (a smell, a sound, a phrase "
           "they always said, a place, a ritual). Do not repeat topics already covered. Do not invent facts "
           "about the person. Output only the question.")
WRITE_SYS = ("You write remembrances for a Dia de los Muertos ofrenda. Use ONLY the facts the family provided; "
             "never invent names, places, dates or events. Write 3 short, warm paragraphs in the second person "
             "addressed to the person who died, in plain language. Then write a heading 'For the ofrenda' with a "
             "short bulleted list of items to place on the altar, drawn from the foods, songs and objects mentioned. "
             "If few details were given, keep it short rather than padding.")

def chat(system, user):
    body = json.dumps({"model": MODEL, "stream": False, "options": {"temperature": 0.7},
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    req = urllib.request.Request(OLLAMA + "/api/chat", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)["message"]["content"].strip()

def dossier(p):
    parts = [f"Name: {p.get('name') or 'unknown'}", f"Relationship to me: {p.get('relation') or 'unspecified'}"]
    if p.get("years"): parts.append(f"Years: {p['years']}")
    if p.get("foods"): parts.append(f"Favorite foods: {p['foods']}")
    if p.get("songs"): parts.append(f"Favorite songs: {p['songs']}")
    for i, m in enumerate(p.get("memories", []), 1): parts.append(f"Memory {i}: {m}")
    return "\n".join(parts)

def save(p, text):
    slug = re.sub(r"[^a-z0-9]+", "-", (p.get("name") or "untitled").lower()).strip("-") or "untitled"
    (DATA / f"{slug}.json").write_text(json.dumps(p, indent=2, ensure_ascii=False), encoding="utf-8")
    (DATA / f"{slug}.md").write_text(f"# In memory of {p.get('name')}\n\n{text}\n", encoding="utf-8")
    return str(DATA / f"{slug}.md")

def status():
    try:
        with urllib.request.urlopen(OLLAMA + "/api/tags", timeout=3) as r:
            names = [m["name"] for m in json.load(r).get("models", [])]
        ok = any(n.split(":")[0] == MODEL.split(":")[0] for n in names)
        return {"ok": ok, "msg": f"model {MODEL} ready" if ok else f"run: ollama pull {MODEL}"}
    except Exception:
        return {"ok": False, "msg": "Ollama not running. Start it with: ollama serve"}

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode()
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path == "/api/status": self._send(200, json.dumps(status()))
        else: self._send(200, PAGE, "text/html")
    def do_POST(self):
        p = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        try:
            if self.path == "/api/ask":
                out = {"question": chat(ASK_SYS, "What I've shared so far:\n" + dossier(p) + "\n\nAsk the next question.")}
            elif self.path == "/api/remember":
                text = chat(WRITE_SYS, dossier(p)); out = {"text": text, "saved": save(p, text)}
            else: return self._send(404, "{}")
            self._send(200, json.dumps(out))
        except Exception as e:
            self._send(500, json.dumps({"error": str(e)}))

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ofrenda</title><style>
:root{--bg:#120a14;--card:#1d1221;--gold:#f6a823;--orange:#e8630a;--ink:#f3e9dc;--mute:#a8969f}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#2a1630,var(--bg) 60%);color:var(--ink);font:17px/1.6 Georgia,serif;min-height:100vh}
main{max-width:720px;margin:0 auto;padding:2rem 1.2rem 4rem}
h1{text-align:center;font-weight:400;letter-spacing:.2em;color:var(--gold);margin:.3rem 0}
.sub{text-align:center;color:var(--mute);margin-bottom:1.5rem}
.candle{text-align:center;font-size:2.4rem;animation:fl 2.2s infinite alternate}
@keyframes fl{0%{opacity:.75;transform:scale(.97)}100%{opacity:1;transform:scale(1.04)}}
.card{background:var(--card);border:1px solid #3a2340;border-radius:14px;padding:1.2rem;margin:1rem 0;box-shadow:0 0 30px #e8630a14}
label{display:block;font-size:.85rem;color:var(--mute);margin:.7rem 0 .2rem;text-transform:uppercase;letter-spacing:.08em}
input,textarea{width:100%;background:#120a14;color:var(--ink);border:1px solid #4a2d52;border-radius:8px;padding:.6rem;font:inherit}
textarea{min-height:90px}.row{display:flex;gap:.8rem}.row>div{flex:1}
button{background:var(--orange);color:#fff;border:0;border-radius:999px;padding:.6rem 1.2rem;font:inherit;cursor:pointer;margin:.6rem .5rem 0 0}
button.ghost{background:transparent;border:1px solid var(--gold);color:var(--gold)}button:disabled{opacity:.5}
.q{color:var(--gold);font-style:italic;margin:.8rem 0 0}.mem{border-left:3px solid var(--gold);padding-left:.8rem;margin:.5rem 0;color:#e6d8cc}
#out{white-space:pre-wrap}#st{text-align:center;font-size:.85rem;color:var(--mute)}.err{color:#ff8a7a}
</style></head><body><main>
<div class="candle">🕯️</div><h1>OFRENDA</h1>
<p class="sub">🌼 Write a remembrance. Everything stays on this machine. 🌼</p><div id="st">checking local model…</div>
<div class="card"><div class="row"><div><label>Their name</label><input id="name"></div><div><label>Who were they to you?</label><input id="rel" placeholder="grandmother, friend…"></div></div>
<label>Years (optional)</label><input id="years"><label>Favorite foods</label><input id="foods"><label>Favorite songs</label><input id="songs"></div>
<div class="card"><label>A memory, a saying, a small detail</label><textarea id="mem"></textarea>
<button onclick="addMem()">Add to ofrenda</button><button class="ghost" id="askb" onclick="ask()">Ask me something</button>
<div class="q" id="q"></div><div id="mems"></div></div>
<div class="card"><button id="wb" onclick="write_()">Write the remembrance</button><div id="out"></div><div id="saved" class="sub"></div></div>
</main><script>
const $=id=>document.getElementById(id);let memories=[];
const person=()=>({name:$('name').value,relation:$('rel').value,years:$('years').value,foods:$('foods').value,songs:$('songs').value,memories});
async function post(u,b){const r=await fetch(u,{method:'POST',body:JSON.stringify(b)});const j=await r.json();if(j.error)throw new Error(j.error);return j}
function addMem(){const v=$('mem').value.trim();if(!v)return;memories.push(v);$('mem').value='';$('q').textContent='';
 $('mems').innerHTML=memories.map(m=>'<div class="mem"></div>').join('');[...$('mems').children].forEach((d,i)=>d.textContent=memories[i])}
async function ask(){$('askb').disabled=true;$('q').textContent='…';try{$('q').textContent=(await post('/api/ask',person())).question}catch(e){$('q').innerHTML='<span class="err"></span>';$('q').firstChild.textContent=e.message}$('askb').disabled=false}
async function write_(){$('wb').disabled=true;$('out').textContent='Lighting the candles…';try{const j=await post('/api/remember',person());$('out').textContent=j.text;$('saved').textContent='Saved locally: '+j.saved}catch(e){$('out').textContent=e.message}$('wb').disabled=false}
fetch('/api/status').then(r=>r.json()).then(s=>{$('st').textContent=(s.ok?'🟢 ':'🔴 ')+s.msg});
</script></body></html>"""

if __name__ == "__main__":
    print(f"Ofrenda on http://127.0.0.1:{PORT}  (model: {MODEL}, data: {DATA.resolve()})")
    ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
