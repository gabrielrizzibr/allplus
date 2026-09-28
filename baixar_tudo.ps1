# Baixa os cursos do HTML (dados\cursos.json) para o seu PC, do maior para o menor.
# Uma pasta por curso, aulas numeradas na ordem. Pode fechar e abrir de novo:
# o que já foi baixado é pulado e arquivo pela metade continua de onde parou.
#
# Uso (ou dê dois cliques em BAIXAR_TUDO.bat):
#   .\baixar_tudo.ps1                          # tudo (~628 GB)
#   .\baixar_tudo.ps1 -Top 10                  # só os 10 maiores
#   .\baixar_tudo.ps1 -MinGB 2                 # só cursos com 2 GB ou mais
#   .\baixar_tudo.ps1 -Destino "D:\para_vimeo" # outra pasta/disco
#   .\baixar_tudo.ps1 -Lista dados\nao_esta_em_lugar_nenhum.txt   # só os que faltam
param(
    [string]$Destino = (Join-Path $PSScriptRoot "para_vimeo"),
    [int]$Top = 0,
    [double]$MinGB = 0,
    [string]$Lista = ""
)
$ErrorActionPreference = "Stop"

function Limpar([string]$nome) {
    $n = ($nome -replace '[<>:"/\\|?*\x00-\x1f]', '').Trim(' ', '.')
    if ($n.Length -gt 100) { $n = $n.Substring(0, 100).Trim() }
    if (-not $n) { $n = "sem nome" }
    return $n
}

$json = Get-Content (Join-Path $PSScriptRoot "dados\cursos.json") -Raw -Encoding UTF8
$cursos = @(ConvertFrom-Json $json)

if ($Lista) {
    $ranks = Get-Content $Lista -Encoding UTF8 | Where-Object { ($_ -split "`t")[0] -match '^\d+$' } | ForEach-Object { [int]($_ -split "`t")[0] }
    $cursos = @($cursos | Where-Object { $ranks -contains $_.rank })
}
$cursos = @($cursos | Where-Object { $_.bytes -ge $MinGB * 1e9 } | Sort-Object rank)
if ($Top -gt 0) { $cursos = @($cursos | Select-Object -First $Top) }

New-Item -ItemType Directory -Force -Path $Destino | Out-Null
$totalGB = ($cursos | Measure-Object -Property bytes -Sum).Sum / 1e9
$drive = (Get-Item $Destino).PSDrive
$livreGB = $drive.Free / 1e9
Write-Host ("{0} cursos, {1:N1} GB -> {2}" -f $cursos.Count, $totalGB, $Destino)
Write-Host ("Espaço livre em {0}: {1:N1} GB" -f $drive.Name, $livreGB)
if ($totalGB -gt $livreGB) {
    Write-Host "ATENÇÃO: não cabe tudo. Vai baixando do maior para o menor até encher." -ForegroundColor Yellow
}

$i = 0
foreach ($c in $cursos) {
    $i++
    $pasta = Join-Path $Destino ("{0:D3} - {1}" -f $c.rank, (Limpar $c.curso))
    New-Item -ItemType Directory -Force -Path $pasta | Out-Null
    Write-Host ""
    Write-Host ("[{0}/{1}] {2:N2} GB  {3}" -f $i, $cursos.Count, ($c.bytes / 1e9), $c.curso) -ForegroundColor Cyan

    $n = 0
    foreach ($v in $c.videos) {
        $n++
        $arq = Join-Path $pasta ("{0:D3} - {1}.mp4" -f $n, (Limpar $v.nome))
        if ((Test-Path -LiteralPath $arq) -and ((Get-Item -LiteralPath $arq).Length -eq $v.bytes)) {
            Write-Host ("  {0}/{1} já existe" -f $n, $c.videos.Count)
            continue
        }
        if ((Get-PSDrive $drive.Name).Free -lt ($v.bytes + 1GB)) {
            Write-Host "Disco cheio. Libere espaço e rode de novo." -ForegroundColor Red
            exit 1
        }
        Write-Host ("  {0}/{1} {2:N0} MB  {3}" -f $n, $c.videos.Count, ($v.bytes / 1MB), $v.nome)
        # curl.exe já vem no Windows 10/11; -C - continua download interrompido
        & curl.exe -L -C - --retry 5 --retry-delay 5 -# -o $arq $v.url
        if ($LASTEXITCODE -ne 0) { Write-Host "    ERRO ao baixar (código $LASTEXITCODE), segue para o próximo" -ForegroundColor Red }
    }
}
Write-Host ""
Write-Host "Terminou. Arquivos em $Destino" -ForegroundColor Green
