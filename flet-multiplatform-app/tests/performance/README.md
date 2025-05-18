# Performance Testing

This directory contains performance tests for the application, including load testing, stress testing, endurance testing, and scalability testing.

## Test Types

### 1. Load Testing
- **Purpose**: Verify system behavior under expected load
- **Location**: `test_load.py`
- **Key Metrics**: Response time, throughput, error rate
- **Configuration**: Environment variables or `config/perf_config.json`
- **Parameters**:
  - `PERF_LOAD_USERS`: Number of concurrent users (default: 10)
  - `PERF_LOAD_SPAWN_RATE`: Users spawned per second (default: 2)
  - `PERF_LOAD_DURATION`: Test duration (default: 30s)
  - `PERF_LOAD_WARM_UP`: Warm-up time in seconds (default: 5)

### 2. Stress Testing
- **Purpose**: Determine system limits and breaking points
- **Location**: `test_stress.py`
- **Key Metrics**: Maximum concurrent users, failure points, recovery time
- **Parameters**:
  - `PERF_STRESS_USERS`: Maximum users (default: 20)
  - `PERF_STRESS_SPAWN_RATE`: Spawn rate (default: 5)
  - `PERF_STRESS_DURATION`: Test duration (default: 1m)
  - `PERF_STRESS_WARM_UP`: Warm-up time (default: 5s)

### 3. Endurance Testing
- **Purpose**: Verify system stability over extended periods
- **Location**: `test_endurance.py`
- **Key Metrics**: Memory usage, response time consistency, error rates over time
- **Parameters**:
  - `PERF_ENDURANCE_USERS`: Concurrent users (default: 5)
  - `PERF_ENDURANCE_SPAWN_RATE`: Spawn rate (default: 1)
  - `PERF_ENDURANCE_DURATION`: Test duration (default: 2m)
  - `PERF_ENDURANCE_WARM_UP`: Warm-up time (default: 10s)

### 4. Scalability Testing
- **Purpose**: Measure how the system scales with increasing load
- **Location**: `test_scalability.py`
- **Key Metrics**: Throughput vs. users, response time vs. load
- **Parameters**:
  - `PERF_SCALE_START_USERS`: Starting users (default: 1)
  - `PERF_SCALE_MAX_USERS`: Maximum users (default: 5)
  - `PERF_SCALE_STEP_SIZE`: User increment per step (default: 1)
  - `PERF_SCALE_STEP_DURATION`: Duration per step (default: 30s)
  - `PERF_SCALE_WARM_UP`: Warm-up time (default: 5s)

## Running Tests

### Prerequisites
- Python 3.10+
- Dependencies from `tests/performance/requirements-test.txt`
- Running instance of the application
- PostgreSQL database (for application data)

### Running Tests with the Test Runner

The recommended way to run performance tests is using the test runner script:

```bash
# Install dependencies
pip install -r tests/performance/requirements-test.txt

# Run all performance tests
python scripts/run_performance_tests.py

# Run specific test type
python scripts/run_performance_tests.py --test-type load
```

### Running Tests Directly with Locust

You can also run tests directly using Locust:

```bash
# Run load test
locust -f tests/performance/test_load.py --headless --users 10 --spawn-rate 2 -H http://localhost:8000

# Run stress test
locust -f tests/performance/test_stress.py --headless --users 20 --spawn-rate 5 -H http://localhost:8000

# Run endurance test
locust -f tests/performance/test_endurance.py --headless --users 5 --spawn-rate 1 -H http://localhost:8000 --run-time 2m

# Run scalability test
locust -f tests/performance/test_scalability.py --headless --users 5 --spawn-rate 1 -H http://localhost:8000 --run-time 2m
```

### Running in CI/CD

The performance tests are integrated into the CI/CD pipeline and will run automatically on pushes to the main branch. The pipeline will:

1. Set up the test environment
2. Start the application
3. Run all performance tests
4. Generate and upload test reports
5. Clean up resources

## Configuration

### Environment Variables

All test parameters can be configured using environment variables:

```bash
# Example: Configure load test
PERF_LOAD_USERS=20 \
PERF_LOAD_SPAWN_RATE=5 \
PERF_LOAD_DURATION=1m \
PERF_LOAD_WARM_UP=5 \
python scripts/run_performance_tests.py --test-type load
```

### Configuration File

You can also use a JSON configuration file (default: `tests/performance/config/perf_config.json`):

```json
{
  "load_test": {
    "users": 10,
    "spawn_rate": 2,
    "duration": "30s",
    "warm_up_time": 5
  },
  "stress_test": {
    "users": 20,
    "spawn_rate": 5,
    "duration": "1m",
    "warm_up_time": 5
  },
  "endurance_test": {
    "users": 5,
    "spawn_rate": 1,
    "duration": "2m",
    "warm_up_time": 10
  },
  "scalability_test": {
    "start_users": 1,
    "max_users": 5,
    "step_size": 1,
    "step_duration": "30s",
    "warm_up_time": 5
  }
}
```

## Test Results

Test results are saved in the following directories:

- **Raw Results**: `flet-multiplatform-app/results/`
  - CSV files with detailed metrics
  - JSON files with aggregated results
  - HTML reports

- **Reports**: `flet-multiplatform-app/reports/`
  - HTML reports with visualizations
  - Summary statistics

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   - Check if the database is running
   - Verify the database connection string
   - Check application logs for errors

2. **Connection Errors**
   - Ensure the application is running and accessible
   - Check network connectivity
   - Verify the base URL in test configuration

3. **Performance Issues**
   - Monitor system resources (CPU, memory, disk I/O)
   - Check database performance
   - Review application logs for bottlenecks

### Debugging

Enable debug logging:

```bash
LOG_LEVEL=DEBUG python scripts/run_performance_tests.py
```

## Best Practices

1. **Start Small**: Begin with a small number of users and gradually increase
2. **Monitor Resources**: Keep an eye on system resources during tests
3. **Run Tests in Isolation**: Ensure no other processes are affecting the results
4. **Document Results**: Save test configurations and results for comparison
5. **Automate**: Integrate performance tests into your CI/CD pipeline

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
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
