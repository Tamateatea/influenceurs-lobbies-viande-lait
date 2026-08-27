@echo off
REM ===================================================================
REM  Tour de nuit du projet — lance la collecte sans intervention.
REM
REM  A LANCER PAR LE PLANIFICATEUR DE TACHES WINDOWS, une fois par jour.
REM  Peut aussi se lancer a la main : double-clic sur ce fichier.
REM
REM  Ce qu'il fait : moisson YouTube, croisement TikTok, moisson TikTok
REM  (deux mois de plus par jour), export, consolidation, tri.
REM  Ce qu'il ne fait pas : juger. Cela reste humain.
REM
REM  Chaque etape est isolee : si l'une echoue, les suivantes tournent.
REM  Le compte rendu est ecrit dans recherche\routine\ , un fichier par jour.
REM ===================================================================

set PYTHONIOENCODING=utf-8
set PROJET=%~dp0
set PY=C:\Users\Vincent\AppData\Local\Python\pythoncore-3.14-64\python.exe

cd /d "%PROJET%"

if not exist "%PY%" (
    echo Python introuvable a l'emplacement attendu : %PY%
    echo Corriger la ligne "set PY=" dans ce fichier.
    exit /b 1
)

echo [%DATE% %TIME%] Debut du tour de nuit
"%PY%" outils\routine_quotidienne.py
echo [%DATE% %TIME%] Fin du tour de nuit, code %ERRORLEVEL%
exit /b %ERRORLEVEL%
