@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo   Update Website  (git commit + push -^> Cloudflare deploy)
echo ============================================================

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Git not found. Install Git for Windows first:
  echo         https://git-scm.com/download/win
  goto end
)

if not exist ".git" (
  echo [Setup] First time: linking this folder to your GitHub repo...
  git init
  git branch -M main
  git remote add origin https://github.com/KINGGM0330/xianni-web.git
)

echo [1/3] Staging changes...
git add -A
echo [2/3] Commit...
git commit -m "update %date% %time%"
echo [3/3] Push to GitHub (force: local overwrites online)...
git push -u --force origin main
echo.
echo DONE. Cloudflare Pages will auto-deploy in about 1 minute.
echo (URL stays the same: kingage.pages.dev)

:end
echo.
pause
