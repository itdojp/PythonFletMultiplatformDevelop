#!/bin/bash

# テストを実行
echo "Running tests..."
python -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

# カバレッジレポートを表示
echo -e "\nCoverage report:"
coverage report -m

echo -e "\nTest completed."
