@echo off
chcp 65001 >nul
echo SmartTrip - GitHub Push Script
echo ================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please download and install Git from: https://git-scm.com/download/win
    echo After installation, restart your terminal and run this script again.
    pause
    exit /b 1
)

echo [OK] Git is installed. Proceeding...
echo.

:: Navigate to project directory
cd /d "%~dp0"

:: Check if git is initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
    echo.
)

:: Configure git (change these if needed)
echo Setting up git configuration...
git config user.name "Tal Golan"
git config user.email "tal.golan99@gmail.com"
echo.

:: Add remote if not exists
git remote get-url origin >nul 2>nul
if %errorlevel% neq 0 (
    echo Adding remote repository...
    git remote add origin https://github.com/tal-golan99/smarTrip.git
    echo.
)

:: Add all files
echo Adding files...
git add .
echo.

:: Commit changes
echo Committing changes...
git commit -m "Fix TypeScript build error: Add category property to Tag interface"
echo.

:: Set branch to main
echo Setting branch to main...
git branch -M main
echo.

:: Push to GitHub
echo Pushing to GitHub...
git push -u origin main
echo.

if %errorlevel% equ 0 (
    echo ================================
    echo SUCCESS! Code pushed to GitHub
    echo ================================
    echo.
    echo Next steps:
    echo 1. Go to Vercel: https://vercel.com
    echo 2. It should automatically detect the new commit and redeploy
    echo 3. Check the deployment logs to verify the build succeeds
    echo 4. Follow DEPLOYMENT_GUIDE.md for full deployment instructions
) else (
    echo ================================
    echo ERROR: Push failed!
    echo ================================
    echo.
    echo Possible reasons:
    echo 1. Authentication required - you may need to authenticate with GitHub
    echo 2. Remote branch has changes - try: git pull origin main --rebase
    echo 3. Permission denied - check your GitHub credentials
)

echo.
pause

