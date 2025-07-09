@echo off

REM .\alembic\init_db.bat

python app\database\init_db.py
if %errorlevel% neq 0 (
    echo init_db.py failed
    exit /b %errorlevel%
)

REM alembic upgrade head
if %errorlevel% neq 0 (
    echo alembic upgrade failed
    exit /b %errorlevel%
)

echo Database initialization and migration completed successfully.
pause
