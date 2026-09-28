@echo off
rem Dois cliques: baixa os cursos que não estão no Vimeo nem no site, da maior carga horária para a menor, em para_vimeo\
rem Para escolher outra pasta, ex.: BAIXAR_TUDO.bat -Destino "D:\para_vimeo"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0baixar_tudo.ps1" -Lista "%~dp0dados\nao_esta_em_lugar_nenhum.txt" %*
pause
