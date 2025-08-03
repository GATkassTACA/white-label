@echo off
REM Simple batch script to run tests on Windows

echo Running White Label Chat SaaS Tests...
echo.

set FLASK_ENV=testing

REM Run specific test types based on argument
if "%1"=="models" (
    echo Running model tests...
    C:/Users/kmoun/OneDrive/Documents/GitHub/white-label/.venv/Scripts/python.exe -m pytest tests/test_models.py -v
) else if "%1"=="auth" (
    echo Running auth tests...
    C:/Users/kmoun/OneDrive/Documents/GitHub/white-label/.venv/Scripts/python.exe -m pytest tests/test_auth.py -v
) else if "%1"=="quick" (
    echo Running quick tests...
    C:/Users/kmoun/OneDrive/Documents/GitHub/white-label/.venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_auth.py -v --tb=short
) else if "%1"=="coverage" (
    echo Running tests with coverage...
    C:/Users/kmoun/OneDrive/Documents/GitHub/white-label/.venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_auth.py --cov=app --cov=models --cov=services --cov-report=html
) else (
    echo Running all available tests...
    C:/Users/kmoun/OneDrive/Documents/GitHub/white-label/.venv/Scripts/python.exe -m pytest tests/ -v
)

echo.
echo Test run completed!
