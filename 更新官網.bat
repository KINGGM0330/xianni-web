@echo off
setlocal
cd /d "%~dp0"
echo ============================================================
echo   Update Website  (git commit + push -^> Cloudflare deploy)
echo ============================================================

where git >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Git not found. Install Git for Windows first.
  goto end
)

if not exist ".git" (
  echo [Setup] First time: linking this folder to GitHub repo...
  git init
  git branch -M main
  git remote add origin https://github.com/KINGGM0330/xianni-web.git
)

REM  Cache busting. Each script tag in index.html loads its JS with a
REM  "?v=..." suffix. That suffix is the cache key for browsers and for
REM  Cloudflare: same URL means the old cached copy is served no matter
REM  what the file now contains, so an update looks like it did nothing.
REM  _cachebust.py rewrites every ?v= to that file's own MD5.
echo [0/4] Refreshing cache-busting version numbers...
set "PY="
where python >nul 2>&1 && set "PY=python"
if not defined PY where py >nul 2>&1 && set "PY=py"
if defined PY (
  %PY% "_cachebust.py"
) else (
  echo   [WARN] python not found - version numbers NOT updated.
  echo   [WARN] Visitors may keep seeing the cached old files.
)

echo [0/4] Removing local backup files from Git tracking (files stay on disk)...
git rm --cached --ignore-unmatch index.html.bak_*
git rm --cached --ignore-unmatch "*.bak_*"
git rm --cached --ignore-unmatch "assets/*.bak_*"

echo [1/4] Staging changes...
git add -A

echo [2/4] Commit...
git commit -m "update %date% %time%"

echo [3/4] Syncing remote changes safely (rebase, no force push)...
git fetch origin
git pull --rebase origin main
if errorlevel 1 (
  echo.
  echo [STOP] Remote sync failed. No force push was performed.
  echo Resolve the Git conflict first, then run this file again.
  goto end
)

echo [4/4] Push to GitHub...
git push -u origin main
if errorlevel 1 (
  echo.
  echo [ERROR] Push failed. No force push was performed.
  goto end
)

echo.
echo DONE. Cloudflare Pages will auto-deploy after GitHub updates.
echo (URL stays the same: kingage.pages.dev)

:end
echo.
pause
