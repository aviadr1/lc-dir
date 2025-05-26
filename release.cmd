@echo off
REM release.cmd — Windows wrapper to call release.sh via WSL

REM Determine bump type (patch/minor/major)
set "BUMP=%\~1"
if "%BUMP%"=="" set "BUMP=patch"

REM Get current Windows directory
set "WINPWD=%cd%"

REM Convert to WSL path
echo Converting Windows path '%WINPWD%' to WSL path...
for /f "usebackq delims=" %%i in (`wsl wslpath -u "%WINPWD%"`) do set "WSLPWD=%%i"
echo WSL working directory: %WSLPWD%

REM Invoke release.sh inside WSL
echo Running release.sh %BUMP% in WSL...
wsl bash -lc "cd '%WSLPWD%' && ./release.sh %BUMP%"
