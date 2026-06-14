@echo off
REM Plugin shim for Copilot CLI - Company framework (Windows)
SETLOCAL
REM Ensure PYTHONPATH points to src directory in this repo
SET REPO_DIR=%~dp0
SET PYTHONPATH=%REPO_DIR%src
python -m company.cli %*
ENDLOCAL
