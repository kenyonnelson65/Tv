@echo off
rem Copies the dashboard into %USERPROFILE%\garmin-dashboard, checks Python, creates .env.local.
setlocal
set "SRC=%~dp0"
set "DEST=%USERPROFILE%\garmin-dashboard"

py -3 -c "import sys; sys.exit(sys.version_info < (3, 10))" >nul 2>&1
if errorlevel 1 (
  echo You need Python 3.10 or newer.
  echo Install it from https://www.python.org/downloads/ and TICK "Add python.exe to PATH".
  start "" "https://www.python.org/downloads/"
  pause
  exit /b 1
)
for /f "delims=" %%v in ('py -3 --version') do echo Python OK: %%v

if not exist "%DEST%\data" mkdir "%DEST%\data"
copy /y "%SRC%*.py" "%DEST%\" >nul
copy /y "%SRC%*.bat" "%DEST%\" >nul
copy /y "%SRC%*.sh" "%DEST%\" >nul
copy /y "%SRC%.gitignore" "%DEST%\" >nul
if not exist "%DEST%\.env.local" (echo GARMIN_PERSONAL_API_KEY=)> "%DEST%\.env.local"
echo Ready: %DEST%
pause
