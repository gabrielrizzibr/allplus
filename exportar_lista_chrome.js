// Cole no Console do Chrome (F12 > Console) com a página aberta:
//   - na pasta do Vimeo  -> salva vimeo.txt
//   - na lista de cursos do site (allplusead.com.br) -> salva site.txt
// Ele rola a página até o fim (carrega tudo), junta os títulos e baixa um .txt.
(async () => {
  const nomeArquivo = location.host.includes("vimeo") ? "vimeo.txt" : "site.txt";
  const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
  const titulos = new Set();

  const coletar = () => {
    document.querySelectorAll("a, h1, h2, h3, h4, [title], [aria-label]").forEach((el) => {
      const t = (el.getAttribute("title") || el.innerText || el.getAttribute("aria-label") || "")
        .split("\n")[0].trim();
      if (t.length >= 4 && t.length <= 200) titulos.add(t);
    });
  };

  // rola até não aparecer mais nada novo (listas com carregamento infinito)
  let parado = 0;
  while (parado < 4) {
    const antes = titulos.size;
    coletar();
    const rolavel = [...document.querySelectorAll("*")]
      .filter((e) => e.scrollHeight > e.clientHeight + 50 && getComputedStyle(e).overflowY.match(/auto|scroll/));
    rolavel.forEach((e) => (e.scrollTop = e.scrollHeight));
    window.scrollTo(0, document.body.scrollHeight);
    await esperar(1500);
    // botão "carregar mais"/"próxima", se existir
    const mais = [...document.querySelectorAll("button, a")].find((b) =>
      /carregar mais|ver mais|load more|show more|próxima|next/i.test(b.innerText || ""));
    if (mais) { mais.click(); await esperar(2000); }
    parado = titulos.size === antes ? parado + 1 : 0;
  }
  coletar();

  const blob = new Blob([[...titulos].join("\n")], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nomeArquivo;
  a.click();
  console.log(`${titulos.size} títulos salvos em ${nomeArquivo}`);
})();
