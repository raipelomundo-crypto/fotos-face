"""Escolhe a foto e a legenda para uma DATA de postagem (pode ser futura).
Uso: python3 escolher.py CONTROLE.json PASTA_FOTOS DATA_DO_POST(YYYY-MM-DD)
Considera todo o "historico" (posts já agendados ou publicados, cada um com a data do post).
Imprime JSON: {"foto":..., "legenda":..., "status": "ok"|"precisa_autorizacao"|"sem_fotos", ...}
Não altera nada; o histórico é gravado depois que o post é criado."""
import json, os, random, sys, datetime as dt
ctrl_path, pasta, hoje = sys.argv[1], sys.argv[2], dt.date.fromisoformat(sys.argv[3])
c = json.load(open(ctrl_path))
R = c["regras"]
LEG = [
 "Do you know this place? 🌍 Have you ever been here, or is it still on your travel bucket list?\nLet us know in the comments! 👇",
 "Do you know this place? 🌍 Have you been lucky enough to visit this place?\nTell us in the comments! 👇\n#travel",
 "Do you know this place? 🌍\nLet us know in the comments! 👇\n\n#travel",
 "Do you know where this place is? 🌍\nLet's see who gets it right in the comments! 👇\n#travel",
 "Do you know where this place is? 🌍\nHint: It's a city in {pais}...\nLet's see who gets it right in the comments! 👇\n#travel",
]
exts = (".jpg", ".jpeg", ".png", ".heic", ".webp")
na_pasta = sorted(f for f in os.listdir(pasta) if f.lower().endswith(exts) and not f.startswith("."))
# Só fotos com boa qualidade: lado menor com pelo menos 600 px
MIN_LADO = 600
def boa(f):
    try:
        from PIL import Image
        return min(Image.open(os.path.join(pasta, f)).size) >= MIN_LADO
    except Exception:
        return True
baixa = [f for f in na_pasta if not boa(f)]
na_pasta = [f for f in na_pasta if f not in baixa]
novas = [f for f in na_pasta if f not in c["fotos"]]
hist = c["historico"]
def dias(h): return abs((hoje - dt.date.fromisoformat(h["data"])).days)
recentes = [h for h in hist if dias(h) <= R["sem_lugar_parecido_dias"]]
lug_bloq = {h["lugar"] for h in recentes}; pais_bloq = {h["pais"] for h in recentes}
fotos_30 = {h["foto"] for h in hist if dias(h) < R["sem_repetir_foto_dias"]}
ja_postadas = {h["foto"] for h in hist}
def ok_lugar(f):
    m = c["fotos"][f]; return m["lugar"] not in lug_bloq and m["pais"] not in pais_bloq
cand = [f for f in na_pasta if f in c["fotos"] and ok_lugar(f)]
nunca = [f for f in cand if f not in ja_postadas]
fora30 = [f for f in cand if f not in fotos_30]
out = {"novas_sem_catalogo": novas, "ignoradas_baixa_qualidade": len(baixa)}
if nunca: pool, out["status"] = nunca, "ok"
elif fora30: pool, out["status"] = fora30, "precisa_autorizacao"
else:
    out["status"] = "sem_fotos"; print(json.dumps(out, ensure_ascii=False, indent=1)); sys.exit()
foto = random.choice(pool); m = c["fotos"][foto]
viz = {h["legenda_idx"] for h in hist if dias(h) == 1}
opc = [i for i in range(5) if i not in viz and (i != 4 or m.get("cidade_para_dica"))]
i = random.choice(opc)
ontem_completa = any(h.get("legenda_completa") for h in hist if (hoje - dt.date.fromisoformat(h["data"])).days == 1)
completa = bool(m.get("local_confirmado")) and not ontem_completa
out["legenda_completa"] = completa  # True: escrever legenda completa com dicas/curiosidades (ver instruções da tarefa)
out.update(foto=foto, lugar=m["lugar"], pais=m["pais"], legenda_idx=i, legenda=LEG[i].format(pais=m.get("pais_dica", m["pais"])))
print(json.dumps(out, ensure_ascii=False, indent=1))
