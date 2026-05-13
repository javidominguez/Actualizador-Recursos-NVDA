@echo off
chcp 65001 >nul
cls
title ActualizadorRecursos NVDA - Publicar en GitHub
echo ============================================================
echo   ActualizadorRecursos NVDA - Script de publicacion
echo ============================================================
echo.
set REPO_URL=https://github.com/hxebolax/Actualizador-Recursos-NVDA.git
set BRANCH=main
echo  Repositorio: %REPO_URL%
echo  Rama: %BRANCH%
echo.
echo  Que deseas hacer?
echo.
echo  [1] Subida inicial (inicializar + primer commit + push)
echo  [2] Commit y push
echo  [3] Inicializar repositorio (solo git init)
echo  [4] Ver estado del repositorio
echo  [5] Salir
echo.
set /p OPCION="  Elige una opcion (1-5): "
if "%OPCION%"=="1" goto INITIAL
if "%OPCION%"=="2" goto PUSH
if "%OPCION%"=="3" goto INIT
if "%OPCION%"=="4" goto STATUS
if "%OPCION%"=="5" goto END
echo  Opcion no valida.
goto END

:INIT
echo.
echo --- Inicializando repositorio ---
if exist ".git" (
    echo  Ya existe un repositorio git en este directorio.
    echo  Si deseas reinicializarlo, elimina la carpeta .git manualmente.
    goto END
)
git init
git remote add origin %REPO_URL%
git branch -M %BRANCH%
echo.
echo  Repositorio inicializado correctamente.
echo  Ahora puedes usar la opcion [1] para la subida inicial
echo  o la opcion [2] para commit y push.
goto END

:INITIAL
echo.
echo --- Subida inicial al repositorio ---
if not exist ".git" (
    echo  Inicializando repositorio...
    git init
    git remote add origin %REPO_URL%
    git branch -M %BRANCH%
) else (
    echo  Repositorio ya inicializado.
)
echo.
set /p MSG="  Mensaje del commit (Enter para usar 'Subida inicial'): "
if "%MSG%"=="" set MSG=Subida inicial
echo.
echo --- Agregando todos los archivos ---
git add --all
echo --- Creando commit ---
git commit -m "%MSG%"
echo --- Subiendo a %BRANCH% ---
git push -u origin %BRANCH%
echo.
echo  Subida inicial completada!
goto END

:PUSH
echo.
set /p MSG="  Mensaje del commit (Enter para usar 'Actualizacion'): "
if "%MSG%"=="" set MSG=Actualizacion
echo.
echo --- Agregando cambios ---
git add --all
echo --- Creando commit ---
git commit -m "%MSG%"
echo --- Subiendo a %BRANCH% ---
git push -u origin %BRANCH%
echo.
echo  Push completado.
goto END

:STATUS
echo.
echo --- Estado del repositorio ---
echo.
git status
echo.
echo --- Ultimo commit ---
git log -1 --oneline 2>nul
echo.
echo --- Remotos ---
git remote -v 2>nul
goto END

:END
echo.
echo ============================================================
echo  Proceso finalizado.
echo ============================================================
pause
