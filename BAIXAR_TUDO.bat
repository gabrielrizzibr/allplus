@echo off
rem Dois cliques aqui para baixar todos os cursos (do maior para o menor) em para_vimeo\
rem Para escolher outra pasta, ex.: BAIXAR_TUDO.bat -Destino "D:\para_vimeo"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0baixar_tudo.ps1" %*
pause
