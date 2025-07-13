@echo off

REM .\scripts\init_db.bat

python app\database\init_db.py
if %errorlevel% neq 0 (
    echo init_db.py failed
    exit /b %errorlevel%
)

echo Database initialization and migration completed successfully.
pause
