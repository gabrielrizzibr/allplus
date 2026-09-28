"""Baixa os cursos que não estão em lugar nenhum para a pasta para_vimeo/,
um subdiretório por curso, aulas numeradas na ordem.

Uso:
  python baixar_para_vimeo.py                 # todos de nao_esta_em_lugar_nenhum.txt
  python baixar_para_vimeo.py --top 10        # só os 10 maiores
  python baixar_para_vimeo.py --min-gb 2      # só cursos com 2 GB ou mais
  python baixar_para_vimeo.py --dry-run       # só mostra o que baixaria

Pode interromper e rodar de novo: arquivos já completos são pulados.
"""
import argparse
import json
import os
import re
import shutil
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")


def limpar(nome):
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome).strip(" .")
    return nome[:120] or "sem nome"


def baixar(url, destino, tamanho):
    if os.path.exists(destino) and os.path.getsize(destino) == tamanho:
        return "já existe"
    tmp = destino + ".part"
    with urllib.request.urlopen(url, timeout=60) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, 1024 * 1024)
    os.replace(tmp, destino)
    return "ok"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--lista", default=os.path.join(DADOS, "nao_esta_em_lugar_nenhum.txt"))
    p.add_argument("--saida", default=os.path.join(AQUI, "para_vimeo"))
    p.add_argument("--top", type=int)
    p.add_argument("--min-gb", type=float, default=0)
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()

    cursos = {c["rank"]: c for c in json.load(open(os.path.join(DADOS, "cursos.json"), encoding="utf-8"))}
    ranks = [int(l.split("\t")[0]) for l in open(a.lista, encoding="utf-8") if l.split("\t")[0].strip().isdigit()]
    escolhidos = [cursos[r] for r in ranks if cursos[r]["bytes"] >= a.min_gb * 1e9][: a.top]

    total = sum(c["bytes"] for c in escolhidos) / 1e9
    print(f"{len(escolhidos)} cursos, {total:.1f} GB -> {a.saida}")
    livre = shutil.disk_usage(os.path.dirname(os.path.abspath(a.saida)) or ".").free / 1e9
    if total > livre:
        print(f"ATENÇÃO: só tem {livre:.1f} GB livres no disco.")

    for c in escolhidos:
        pasta = os.path.join(a.saida, f'{c["rank"]:03d} - {limpar(c["curso"])}')
        print(f'\n[{c["bytes"] / 1e9:.2f} GB] {c["curso"]}')
        if a.dry_run:
            continue
        os.makedirs(pasta, exist_ok=True)
        for i, v in enumerate(c["videos"], 1):
            destino = os.path.join(pasta, f"{i:03d} - {limpar(v['nome'])}.mp4")
            try:
                print(f"  {i}/{c['aulas']} {baixar(v['url'], destino, v['bytes'])}  {v['nome']}")
            except Exception as e:
                print(f"  {i}/{c['aulas']} ERRO {e}  {v['nome']}")


if __name__ == "__main__":
    main()
