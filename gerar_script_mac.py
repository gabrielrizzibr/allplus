"""Gera BAIXAR_TUDO_MAC.command: script bash (Mac) com todos os downloads já escritos,
na ordem de dados/prioridade_download.txt, para ~/Desktop/CURSOS ALL PLUS.
Não depende de Python no Mac, só de bash + curl (já vêm no macOS)."""
import json
import os
import re

AQUI = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(AQUI, "dados")


def limpar(nome):
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome).strip(" .")
    return nome[:120] or "sem nome"


def nome_modulo(nome):
    return re.sub(r"^\s*m[óo]dulo\s*\d+\s*[-–:.]?\s*", "", nome, flags=re.I).strip() or nome.strip()


def q(s):  # aspas simples seguras para bash
    return "'" + s.replace("'", "'\\''") + "'"


cursos = {c["rank"]: c for c in json.load(open(os.path.join(D, "cursos.json"), encoding="utf-8"))}
ranks = [int(l.split("\t")[0]) for l in open(os.path.join(D, "prioridade_download.txt"), encoding="utf-8")
         if l.split("\t")[0].strip().isdigit()]
total_gb = sum(cursos[r]["bytes"] for r in ranks) / 1e9

L = ["#!/bin/bash",
     "# Dois cliques (ou: bash BAIXAR_TUDO_MAC.command no Terminal).",
     "# Baixa os cursos para ~/Desktop/CURSOS ALL PLUS, separados por curso e módulo.",
     "# Pode fechar e rodar de novo: o que já baixou é pulado e o resto continua.",
     'DEST="$HOME/Desktop/CURSOS ALL PLUS"',
     'mkdir -p "$DEST" && cd "$DEST" || exit 1',
     f'echo "{len(ranks)} cursos, {total_gb:.0f} GB -> $DEST"',
     'echo "Espaço livre:"; df -h "$DEST" | tail -1',
     "ERROS=0",
     "baixa() {  # url tamanho caminho",
     '  local url="$1" tam="$2" arq="$3"',
     '  mkdir -p "$(dirname "$arq")"',
     '  if [ -f "$arq" ] && [ "$(stat -f%z "$arq" 2>/dev/null)" = "$tam" ]; then echo "  já existe: $arq"; return; fi',
     '  echo "  baixando: $arq"',
     '  if ! curl -f -L -C - --retry 5 --retry-delay 5 -# -o "$arq" "$url"; then',
     '    echo "  ERRO (sem acesso ou falha de rede): $arq"; ERROS=$((ERROS+1))',
     '    [ -f "$arq" ] && [ "$(stat -f%z "$arq" 2>/dev/null)" -lt 100000 ] && rm -f "$arq"',
     "  fi",
     "}"]
for n, r in enumerate(ranks, 1):
    c = cursos[r]
    pasta = f'{c["rank"]:03d} - {limpar(c["curso"])}'
    mods = list(dict.fromkeys(v["modulo"] for v in c["videos"]))
    L.append(f'echo; echo "[{n}/{len(ranks)}] {c["segundos"] / 3600:.1f} h, {c["aulas"]} aulas: "{q(c["curso"])}')
    for i, v in enumerate(c["videos"], 1):
        aula = f"Aula {i:03d} - {limpar(v['nome'])}.mp4"
        if len(mods) == 1 and not v["modulo"].strip():
            caminho = f"{pasta}/{aula}"
        else:
            m = limpar(nome_modulo(v["modulo"])) if v["modulo"].strip() else "Sem nome"
            caminho = f"{pasta}/Módulo {mods.index(v['modulo']) + 1:02d} - {m}/{aula}"
        L.append(f"baixa {q(v['url'])} {v['bytes']} {q(caminho)}")
L += ['echo', 'echo "Terminou. Erros: $ERROS (se tiver erro, rode de novo)."',
      'read -p "Aperte Enter para fechar."']
saida = os.path.join(AQUI, "BAIXAR_TUDO_MAC.command")
open(saida, "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
os.chmod(saida, 0o755)
print(saida, len(L), "linhas")
