"""Lê a duração de cada vídeo direto do S3 sem baixar o arquivo inteiro
(só o cabeçalho do MP4, alguns KB por vídeo) e grava em dados/duracoes.json.

Uso: python duracoes.py
"""
import concurrent.futures as cf
import json
import os
import struct
import urllib.request

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")


def ler(url, inicio, tamanho):
    req = urllib.request.Request(url, headers={"Range": f"bytes={inicio}-{inicio + tamanho - 1}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def duracao_mp4(url, total):
    """Percorre as caixas do topo do MP4 até achar 'moov' e lê o 'mvhd' dentro dela."""
    pos = 0
    while pos < total:
        cab = ler(url, pos, 16)
        tam, tipo = struct.unpack(">I4s", cab[:8])
        cab_len = 8
        if tam == 1:
            tam, cab_len = struct.unpack(">Q", cab[8:16])[0], 16
        elif tam == 0:
            tam = total - pos
        if tipo == b"moov":
            dados = ler(url, pos + cab_len, min(tam - cab_len, 4096))
            i = dados.find(b"mvhd")
            if i < 0:
                return None
            v = dados[i + 4]
            if v == 1:
                escala, dur = struct.unpack(">IQ", dados[i + 24:i + 36])
            else:
                escala, dur = struct.unpack(">II", dados[i + 16:i + 24])
            return dur / escala if escala else None
        if tam < 8:
            return None
        pos += tam
    return None


def main():
    cursos = json.load(open(os.path.join(DADOS, "cursos.json"), encoding="utf-8"))
    caminho = os.path.join(DADOS, "duracoes.json")
    cache = json.load(open(caminho)) if os.path.exists(caminho) else {}
    videos = {v["url"]: v["bytes"] for c in cursos for v in c["videos"]}
    faltam = [(u, b) for u, b in videos.items() if cache.get(u) is None]

    def um(item):
        u, b = item
        for _ in range(3):
            try:
                return u, duracao_mp4(u, b)
            except Exception:
                pass
        return u, None

    with cf.ThreadPoolExecutor(32) as ex:
        cache.update(dict(ex.map(um, faltam)))
    json.dump(cache, open(caminho, "w"))
    ok = sum(v is not None for v in cache.values())
    print(f"{ok}/{len(videos)} vídeos com duração, total {sum(v or 0 for v in cache.values()) / 3600:.0f} h")


if __name__ == "__main__":
    main()
