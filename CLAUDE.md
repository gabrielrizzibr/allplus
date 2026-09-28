# Projeto: cursos allnet → Vimeo (All+) → site allplusead.com.br

Responda sempre em português, direto, com um **Resumo** no final.

## Objetivo
Levar os cursos do HTML (backup allnet na AWS/S3) para o site https://allplusead.com.br.
Fluxo de cada curso: **baixar → subir no Vimeo (pasta All+) → subir no site**.
Prioridade é o site. O Vimeo é o passo intermediário/backup: sinalizar o que está incompleto lá,
mas não é obrigatório para quem já está completo no site.

## Fontes
- HTML: `allnet-aws.html` (542 cursos, 2.342 vídeos no S3 público `fpass-backup`).
  Dados extraídos em `dados/cursos.json` (486 cursos únicos, duração e tamanho de cada aula).
  `allnet-vimeo.html` é só um subconjunto (35 cursos) do mesmo conteúdo — nada novo.
- Vimeo: pasta **All+** = https://vimeo.com/user/105818946/folder/30072703 (conta "all net").
  Conteúdo levantado por prints em `dados/vimeo_allplus.tsv` → `dados/etapa2_vimeo.csv`.
- Site: levantado por prints em `dados/site_allplus.tsv`.
- Resultado: `dados/checklist_final.csv` (gerado por `dados/checklist_final.py`).

## Decisões do usuário
- Curso duplicado com e sem "(Premium)": fica **só o Premium** (feito em `gerar_lista.py`).
- Não existe curso de inglês no HTML. Há só 3 mentorias faladas em inglês (Sales Pitch,
  Business with Americans, International Team Management) — vão primeiro.
- Inglês Basic 1/2, Business English, Auxiliar Administrativo, Power Point, IA para Produtividade,
  Liderança de Equipes, React Avançado, INFORMATICA - LEO, AUX ADM: vieram de outra fonte (não estão no HTML).
- Ordem de download: `dados/prioridade_download.txt`
  1. 3 mentorias em inglês  2. outros vídeos 00:00 no Vimeo (Hábitos Simples, Business Dô)
  3. incompletos no site: Inteligência Artificial, Excel Módulo I, Python, AutoCAD
  4. os 461 que não estão em lugar nenhum, da maior carga horária para a menor.
- Data Science: faltam 10 aulas no site, mas já estão completas no Vimeo (não precisa baixar).

## Estrutura dos arquivos baixados
`NNN - Nome do Curso\Módulo NN - Nome do módulo\Aula NNN - Nome da aula.mp4`
(curso sem módulos: aulas direto na pasta do curso; NNN do curso = rank por carga horária).

## Como baixar (rodar na máquina do usuário — sessão Local)
- Python: `python baixar_para_vimeo.py --lista dados/prioridade_download.txt --saida para_vimeo`
- Windows sem Python: `BAIXAR_TUDO.bat` (usa `baixar_tudo.ps1` + curl.exe)
Ambos retomam de onde pararam. Conferir espaço em disco antes (~670 GB no total).

## Scripts
- `gerar_lista.py` — HTML → `dados/cursos.json` (tamanhos por HEAD no S3, durações de `dados/duracoes.json`)
- `duracoes.py` — lê a duração de cada MP4 no S3 só pelo cabeçalho
- `comparar.py` — cruza listas de títulos (vimeo.txt/site.txt) com os cursos
- `dados/checklist_final.py` — gera o checklist final e `nao_esta_em_lugar_nenhum.txt`
