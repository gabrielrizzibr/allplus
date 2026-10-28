@echo off
rem Dois cliques: baixa na ordem de dados\prioridade_download.txt para a pasta "CURSOS ALL PLUS" da Area de Trabalho
rem Para escolher outra pasta, ex.: BAIXAR_TUDO.bat -Destino "D:\CURSOS ALL PLUS"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0baixar_tudo.ps1" -Lista "%~dp0dados\prioridade_download.txt" %*
pause
