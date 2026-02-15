@echo off
title Rulare wan2gp - wgp.py

REM 1. Activarea mediului Conda
REM Folosim 'call' pentru ca scriptul să continue după activare
call conda activate wan2gp

REM 2. Executarea scriptului Python
python wgp.py

REM 3. Menținerea ferestrei deschise pentru vizualizarea rezultatelor
pause