"""Cruza os cursos do HTML (dados/cursos.json) com o que já está no Vimeo e no site.

Uso: python comparar.py vimeo.txt site.txt
  (cada .txt = um título por linha; pode ter nomes de cursos ou de aulas)

Gera em dados/:
  - status_cursos.csv          todos os cursos, do maior pro menor, com Vimeo/Site
  - falta_no_site.txt          está no Vimeo mas ainda não no site
  - nao_esta_em_lugar_nenhum.txt  só existe no HTML -> baixar e subir pro Vimeo
"""
import csv
import difflib
import json
import os
import re
import sys
import unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
DADOS = os.path.join(AQUI, "dados")


def normalizar(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\((premium)\)|-\s*inativo|\.mp4$", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def carregar_titulos(caminho):
    if not caminho or not os.path.exists(caminho):
        return set()
    with open(caminho, encoding="utf-8", errors="ignore") as f:
        return {normalizar(l) for l in f if normalizar(l)}


def bate(nome, titulos):
    n = normalizar(nome)
    if not n:
        return False
    if n in titulos:
        return True
    # um contém o outro, mas só com palavras inteiras ("modulo i" não bate com "modulo ii")
    contem = lambda a, b: re.search(rf"(^| ){re.escape(a)}( |$)", b)
    if len(n) >= 12 and any(contem(n, t) or (len(t) >= 12 and contem(t, n)) for t in titulos):
        return True
    return bool(difflib.get_close_matches(n, titulos, n=1, cutoff=0.9))


def presente(curso, titulos):
    """Curso conta como presente se o nome bate ou se ao menos metade das aulas bate."""
    if not titulos:
        return False
    if any(bate(n, titulos) for n in curso["nomes"]):
        return True
    aulas = [v["nome"] for v in curso["videos"] if normalizar(v["nome"])]
    if not aulas:
        return False
    return sum(bate(a, titulos) for a in aulas) / len(aulas) >= 0.5


def main():
    vimeo = carregar_titulos(sys.argv[1] if len(sys.argv) > 1 else None)
    site = carregar_titulos(sys.argv[2] if len(sys.argv) > 2 else None)
    cursos = json.load(open(os.path.join(DADOS, "cursos.json"), encoding="utf-8"))

    falta_site, nenhum = [], []
    with open(os.path.join(DADOS, "status_cursos.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["rank", "curso", "GB", "aulas", "no_vimeo", "no_site"])
        for c in cursos:
            v, s = presente(c, vimeo), presente(c, site)
            w.writerow([c["rank"], c["curso"], f'{c["bytes"] / 1e9:.2f}'.replace(".", ","),
                        c["aulas"], "sim" if v else "", "sim" if s else ""])
            if v and not s:
                falta_site.append(c)
            if not v and not s:
                nenhum.append(c)

    def salvar(nome, lista):
        with open(os.path.join(DADOS, nome), "w", encoding="utf-8") as f:
            for c in lista:
                f.write(f'{c["rank"]}\t{c["bytes"] / 1e9:.2f} GB\t{c["curso"]}\n')

    salvar("falta_no_site.txt", falta_site)
    salvar("nao_esta_em_lugar_nenhum.txt", nenhum)
    gb = sum(c["bytes"] for c in nenhum) / 1e9
    print(f"{len(cursos)} cursos | no Vimeo e fora do site: {len(falta_site)} | "
          f"em lugar nenhum: {len(nenhum)} ({gb:.1f} GB)")
    print("Maiores que não estão em lugar nenhum:")
    for c in nenhum[:20]:
        print(f'  #{c["rank"]:<4} {c["bytes"] / 1e9:6.2f} GB  {c["curso"]}')


if __name__ == "__main__":
    main()
