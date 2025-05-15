@echo off
echo Running tests...
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo.
echo Coverage report:
python -m coverage report -m

echo.
echo Test completed.
pause
