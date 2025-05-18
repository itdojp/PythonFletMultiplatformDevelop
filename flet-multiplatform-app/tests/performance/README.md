# Performance Testing

This directory contains performance tests for the application, including load testing, stress testing, endurance testing, and scalability testing.

## Test Types

### 1. Load Testing
- **Purpose**: Verify system behavior under expected load
- **Location**: `test_load.py`
- **Key Metrics**: Response time, throughput, error rate
- **Configuration**: See `config/perf_config.json`

### 2. Stress Testing
- **Purpose**: Determine system limits and breaking points
- **Location**: `test_stress.py`
- **Key Metrics**: Maximum concurrent users, failure points, recovery time

### 3. Endurance Testing
- **Purpose**: Verify system stability over extended periods
- **Location**: `test_endurance.py`
- **Key Metrics**: Memory usage, response time consistency, error rates over time

### 4. Scalability Testing
- **Purpose**: Measure how the system scales with increasing load
- **Location**: `test_scalability.py`
- **Key Metrics**: Throughput vs. users, response time vs. load

## Running Tests

### Prerequisites
- Python 3.8+
- Dependencies from `requirements-test.txt`
- Running instance of the application

### Running All Performance Tests

```bash
# Run all performance tests
pytest tests/performance/ -v --perf-test

# Run with custom config
pytest tests/performance/ -v --perf-test --perf-config=path/to/config.json
```

### Running Specific Test Types

```bash
# Run only load tests
pytest tests/performance/test_load.py -v --perf-test

# Run only stress tests
pytest tests/performance/test_stress.py -v --perf-test

# Run only endurance tests
pytest tests/performance/test_endurance.py -v --perf-test

# Run only scalability tests
pytest tests/performance/test_scalability.py -v --perf-test
```

## Configuration

Performance test settings can be configured in `config/perf_config.json`:

```json
{
  "load_test": {
    "users": 100,
    "spawn_rate": 10,
    "duration": "30s",
    "warm_up_time": 5
  },
  "stress_test": {
    "users": 1000,
    "spawn_rate": 100,
    "duration": "5m",
    "warm_up_time": 10
  },
  "endurance_test": {
    "users": 100,
    "spawn_rate": 10,
    "duration": "1h",
    "warm_up_time": 30
  },
  "scalability_test": {
    "start_users": 1,
    "max_users": 500,
    "step_size": 10,
    "step_duration": "30s",
    "warm_up_time": 10
  }
}
```

## Test Results

Test results are saved in the `results/performance` directory with timestamps in the filenames.

### Analyzing Results

Use the `analyze_performance_results` function to generate a summary of test results:

```python
from src.backend.tests.performance.utils import analyze_performance_results

summary = analyze_performance_results("results/performance")
print(summary)
```

## CI/CD Integration

Performance tests can be integrated into your CI/CD pipeline. Example GitHub Actions workflow:

```yaml
name: Performance Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  performance-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt

    - name: Run performance tests
      run: |
        pytest tests/performance/ -v --perf-test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: performance-test-results
        path: results/performance/
```

## Best Practices

1. **Start Small**: Begin with small load tests and gradually increase the load.
2. **Monitor Resources**: Keep an eye on CPU, memory, and I/O during tests.
3. **Baseline**: Establish performance baselines for future comparison.
4. **Isolate Tests**: Run performance tests in an isolated environment.
5. **Document**: Keep detailed records of test configurations and results.
6. **Automate**: Integrate performance tests into your CI/CD pipeline.
7. **Analyze**: Regularly review test results to identify trends and potential issues.

## Troubleshooting

### Common Issues

1. **Connection Errors**: Ensure the application is running and accessible.
2. **Resource Exhaustion**: Monitor system resources and adjust test parameters.
3. **Timeout Errors**: Increase timeouts in the test configuration if needed.
4. **Inconsistent Results**: Run tests multiple times to account for variability.

### Debugging

To enable debug logging, set the `LOG_LEVEL` environment variable:

```bash
LOG_LEVEL=DEBUG pytest tests/performance/ -v --perf-test
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
