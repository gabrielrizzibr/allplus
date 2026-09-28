"""Etapa 1: lista todos os cursos do HTML com carga horária, aulas, módulos e GB.

Uso: python listar_html.py   (depois de gerar_lista.py e duracoes.py)
Grava a duração em dados/cursos.json e gera dados/etapa1_cursos_html.csv,
ordenado pela carga horária (maior primeiro).
"""
import csv
import json
import os

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")


def hhmm(seg):
    m = round(seg / 60)
    return f"{m // 60}h{m % 60:02d}"


def main():
    caminho = os.path.join(DADOS, "cursos.json")
    cursos = json.load(open(caminho, encoding="utf-8"))
    dur = json.load(open(os.path.join(DADOS, "duracoes.json")))
    for c in cursos:
        for v in c["videos"]:
            v["segundos"] = round(dur.get(v["url"]) or 0)
        c["segundos"] = sum(v["segundos"] for v in c["videos"])
        c["modulos"] = len({v["modulo"] for v in c["videos"]})
    json.dump(cursos, open(caminho, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    with open(os.path.join(DADOS, "etapa1_cursos_html.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["#", "curso", "carga_horaria", "horas", "aulas", "modulos", "GB", "outros_nomes"])
        for i, c in enumerate(sorted(cursos, key=lambda c: -c["segundos"]), 1):
            w.writerow([i, c["curso"], hhmm(c["segundos"]), f'{c["segundos"] / 3600:.2f}'.replace(".", ","),
                        c["aulas"], c["modulos"], f'{c["bytes"] / 1e9:.2f}'.replace(".", ","),
                        " | ".join(n for n in c["nomes"] if n != c["curso"])])
    print(f"{len(cursos)} cursos, {sum(c['segundos'] for c in cursos) / 3600:.0f} h, "
          f"{sum(c['aulas'] for c in cursos)} aulas")


if __name__ == "__main__":
    main()
