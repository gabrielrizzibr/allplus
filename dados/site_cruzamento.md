# Cruzamento site allplusead.com.br × 47 "maiores fora do site" — 13/11/2026

## Resultado: o catálogo do site NÃO pode ser lido sem login

Não foi possível extrair a lista de cursos publicados. Por isso **não** foram gerados
`site_cursos_completo.tsv` nem `maiores_fora_do_site_atualizado.csv`: a lista
`maiores_fora_do_site.csv` (47 cursos) continua sendo a referência, sem alteração.

## O que foi tentado e o que respondeu

| Tentativa | Resposta |
|---|---|
| `curl -L https://allplusead.com.br/` | 200, 10 KB. App React/TanStack (gerado no Lovable), renderizado no servidor. Texto da página: *"Nenhum canal cadastrado ainda. Acesse o admin para adicionar conteúdo."* Único link interno: `/auth`. |
| `/cursos`, `/catalogo`, `/courses`, `/dashboard` | 404 (página "não encontrada" do app) |
| `/sitemap.xml`, `/robots.txt` | 404 (não existem) |
| `/ranking` | 200, mas no navegador redireciona para a tela de login (*"Acesso restrito. Novos cadastros são feitos via SSO Klass ou pelo painel administrativo."*) |
| Home renderizada no Chromium headless (visitante anônimo, espera de rede ociosa + 4 s) | Mesmo texto: *"Nenhum canal cadastrado ainda"*. A página não fez nenhuma chamada de dados visível; só `POST /__l5e/trackevents` (analytics). |
| Leitura do JS (`/assets/api-*.js`) | Os cursos ficam num banco Supabase (tabelas `channels`, `courses`, `modules`, `lessons`; aulas com `vimeo_id`). Para visitante sem login a home não lista nada. |

Não foi feito login, nem envio de formulário, nem acesso direto à API do Supabase
(a consulta direta ao banco foi bloqueada pela permissão desta sessão e, de qualquer
forma, para visitante anônimo o site mostra o catálogo vazio).

## Como destravar
1. **Mais fácil:** entrar no site com uma conta (de preferência admin) e exportar/printar a lista
   de cursos do painel admin → salvar em `dados/site_cursos_completo.tsv`
   (colunas: curso, categoria, aulas, professor, url). Com isso o cruzamento roda em minutos.
2. Ou, no painel do Supabase/Lovable do projeto, exportar a tabela `courses` (com contagem de
   `lessons` por curso) em CSV.
3. Ou rodar a extração numa sessão **Local** (máquina do usuário) com o navegador já logado.

## Lista final (sem alteração)
Continuam os 47 cursos de `dados/maiores_fora_do_site.csv`.
- 1 — Excel 2019 - Módulo II (Premium) — aulas: 126
- 2 — Office 365 para Negócios: Domine a Produtividade (Premium) — aulas: 89
- 3 — Excel 2019 - Gráficos e Dashboards (Premium) — aulas: 81
- 4 — React - Direto ao Ponto (Premium) — aulas: 70
- 5 — Photoshop CC 2019 - Módulo I (Premium) — aulas: 49
- 6 — Scrum - Gestão e Desenvolvimento Ágil de Projetos — aulas: 34
- 7 — SQL 2016: Construindo Sistemas de Banco de Dados Poderosos (Premium) — aulas: 31
- 8 — Power BI Desktop: Dominando Análise de Dados (Premium) — aulas: 21
- 9 — Domine o Inbound Marketing — aulas: 25
- 10 — Photoshop CC 2019 - Módulo II (Premium) — aulas: 30
- 11 — PNL - Desvendando a Mente (Premium) — aulas: 19
- 12 — Marketing Digital para Ecommerce (Premium) — aulas: 50
- 13 — Mongo DB em Ação: Dominando a Prática (Premium) — aulas: 22
- 14 — Big Data com Hadoop - Fundamentos (Premium) — aulas: 19
- 15 — ETL na Prática - Como trabalhar com dados (Premium) — aulas: 15
- 16 — Global Business for Tech Entrepreneurs — aulas: 13
- 17 — Negociação Produtiva (Premium) — aulas: 7
- 18 — Global Business for Entrepreneurs — aulas: 11
- 19 — Tik Tok Ads (Premium) — aulas: 16
- 20 — Data Warehouse Fundamentos e Implementação (Premium) — aulas: 12
- 21 — R: Explorando o Potencial da Análise de Dados (Premium) — aulas: 10
- 22 — Fundamentos de Liderança — aulas: 8
- 23 — Introdução à Lógica de Programação (Premium) — aulas: 10
- 24 — Reinventando a Carreira — aulas: 6
- 25 — IoT Desvendada: Fundamentos da Internet das Coisas — aulas: 13
- 26 — Tendências Globais para Fintechs (Premium) — aulas: 5
- 27 — Brand Experience (Premium) — aulas: 3
- 28 — Apertando START no mundo dos games (Premium) — aulas: 4
- 29 — Planejamento Estratégico — aulas: 6
- 30 — Mobile Economy — aulas: 3
- 31 — Como criar um E-Commerce Global — aulas: 4
- 32 — Vida e Morte das Organizações — aulas: 5
- 33 — Como criar uma marca global — aulas: 5
- 34 — Game Design e Prototipagem para Boardgames (Premium) — aulas: 3
- 35 — Double Diamond - Introdução ao UX Design (Premium) — aulas: 4
- 36 — Estratégias Aplicadas ao Empreendedorismo — aulas: 4
- 37 — Ferramentas para aumentar sua produtividade (Premium) — aulas: 3
- 38 — Empreender como PJ: O Guia para a Liberdade Profissional — aulas: 3
- 39 — Arquétipos do Networking — aulas: 3
- 40 — Neurociência da Educação — aulas: 6
- 41 — Aspectos Legais da Internacionalização — aulas: 2
- 42 — Marketing Digital para Iniciantes (Premium) — aulas: 2
- 43 — Pensamento Exponencial — aulas: 4
- 44 — Evolução dos Jogos e Gamificação (Premium) — aulas: 2
- 45 — First Principle — aulas: 4
- 46 — 21 Lições para o Século XXI — aulas: 5
- 47 — Agilidade Emocional (Premium) — aulas: 2

## Atualização 13/11 — prints enviados pelo usuário
Prints de: Inteligência Artificial (Canis Minor Solum 27, Fundamentos de Machine Learning 29,
Data Science 61, IA para Produtividade 2), Informática 5.0 (Volume 1, 5 módulos),
Game & Marketing (Game Dev 4, CBS 9) e Inglês (Basic 1 17, Business English 2).
Todos já constavam em `site_allplus.tsv`, exceto **Informática 5.0**, que não existe no HTML
(outra fonte, como INFORMATICA - LEO). **Nenhum dos 47 foi achado** → lista de downloads sem alteração.
Faltam prints da seção Gestão Empresarial e Tecnologia (e de outras seções, se houver) para fechar.

## Atualização 13/11 (2) — prints de Gestão Empresarial e Tecnologia
Gestão: Auxiliar Administrativo 17, 7 Tendências 10, Instagram Autoral 8, Contabilidade p/ Iniciantes 6,
Estratégias de Carreira 6, Liderança de Equipes 1. Tecnologia: Informática Básica 11 (Leonardo),
AutoCAD 2019 53, Python 86, B.I. 9, Power Point 16, Excel 2019 (Módulo I) 41, Illustrator CC 2019 47, React Avançado 4.
Novo só **Informática Básica** (= "INFORMATICA - LEO", outra fonte, não está no HTML).
**Conclusão: o site tem 23 cursos; nenhum dos 47 está lá. Lista de downloads sem alteração.**
