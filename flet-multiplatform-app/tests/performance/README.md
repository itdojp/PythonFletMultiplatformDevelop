# Performance Testing Framework

This directory contains a comprehensive performance testing framework for the application, built on top of Locust. The framework supports various types of performance tests including load testing, stress testing, and endurance testing.

## Features

- **Multiple Test Types**: Support for load, stress, and endurance testing
- **Detailed Reporting**: HTML and JSON reports with visualizations
- **Alerting**: Configurable alerts for performance degradation
- **Test Data Management**: Tools for generating and managing test data
- **Configuration Management**: YAML-based configuration for test scenarios
- **Extensible**: Easy to add new test scenarios and metrics

## Test Types

### 1. Load Testing
- **Purpose**: Verify system behavior under expected load conditions
- **Location**: `test_load.py`
- **Key Metrics**:
  - Response time (p50, p90, p95, p99)
  - Requests per second (RPS)
  - Error rate
  - Concurrent users
- **Configuration**: `config/performance_config.yaml`

### 2. Stress Testing
- **Purpose**: Determine system limits and breaking points
- **Location**: `test_stress.py`
- **Key Metrics**:
  - Maximum sustainable throughput
  - Failure points
  - System recovery time
  - Resource utilization at peak load

### 3. Endurance Testing
- **Purpose**: Verify system stability over extended periods
- **Location**: `test_endurance.py`
- **Key Metrics**:
  - Memory usage over time
  - Response time consistency
  - Error rates over time
  - Database connection pool usage

## Getting Started

### Prerequisites

- Python 3.8+
- pip
- Locust
- Required Python packages (install via `pip install -r requirements-test.txt`)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd flet-multiplatform-app
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements-test.txt
   ```

## Running Tests

### Running a Specific Test

To run a specific test scenario, use the `run_perf_tests.py` script:

```bash
python scripts/run_perf_tests.py --config tests/performance/config/performance_config.yaml --scenario load
```

### Running All Tests

To run all test scenarios defined in the configuration file:

```bash
python scripts/run_perf_tests.py --config tests/performance/config/performance_config.yaml
```

### Running with Custom Parameters

You can override configuration parameters using command-line arguments:

```bash
python scripts/run_perf_tests.py --scenario load --users 20 --spawn-rate 5 --run-time 5m
```

## Analyzing Results

After running tests, you can generate detailed reports using the `analyze_perf_results.py` script:

```bash
python scripts/analyze_perf_results.py --results-dir reports/performance
```

This will generate:
- HTML report at `reports/performance/reports/performance_report.html`
- Plots in the `reports/performance/reports/plots/` directory
- JSON report with raw data

## Configuration

The performance testing framework is configured using YAML files. The main configuration file is located at `tests/performance/config/performance_config.yaml`.

### Configuration Options

- `base_url`: The base URL of the application under test
- `scenarios`: Test scenarios with their parameters
- `alerting`: Configuration for alerts (email, Slack)
- `test_data`: Configuration for test data generation
- `reporting`: Report generation settings
- `locust`: Locust-specific settings

Example configuration:

```yaml
base_url: "http://localhost:8000"

scenarios:
  smoke:
    description: "Quick smoke test"
    users: 1
    spawn_rate: 1
    run_time: "30s"
    thresholds:
      response_time_p95: 1000  # ms
      error_rate: 0.01  # 1%
      throughput: 5  # req/s

alerting:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.example.com"
    smtp_port: 587
    username: "user@example.com"
    password: "your-password"
    from_addr: "perf-tests@example.com"
    to_addrs:
      - "team@example.com"
```

## Creating Custom Tests

To create a new performance test, follow these steps:

1. Create a new test file in the `tests/performance/` directory (e.g., `test_custom.py`)
2. Define your test class by extending `BaseLocustTest` or `HttpUser`
3. Add your test methods with the `@task` decorator
4. Update the configuration file to include your new test scenario

Example test:

```python
from locust import task, between
from .base_test import BaseLocustTest

class CustomTestUser(BaseLocustTest):
    wait_time = between(1, 3)

    @task(3)
    def get_items(self):
        self.client.get("/api/items/")

    @task(1)
    def create_item(self):
        self.client.post(
            "/api/items/",
            json={"name": "test", "value": 42},
            headers={"Content-Type": "application/json"}
        )
```

## Alerting

The performance testing framework includes an alerting system that can notify you when performance degrades beyond configured thresholds.

### Email Alerts

To enable email alerts, update the `alerting` section in the configuration file:

```yaml
alerting:
  enabled: true
  email:
    enabled: true
    smtp_server: "smtp.example.com"
    smtp_port: 587
    use_tls: true
    username: "user@example.com"
    password: "your-password"
    from_addr: "perf-tests@example.com"
    to_addrs:
      - "team@example.com"
```

### Slack Alerts

To enable Slack alerts, update the `alerting` section in the configuration file:

```yaml
alerting:
  enabled: true
  slack:
    enabled: true
    webhook_url: "https://hooks.slack.com/services/..."
    channel: "#alerts"
```

## Best Practices

1. **Start Small**: Begin with a small number of users and gradually increase the load
2. **Monitor Resources**: Keep an eye on system resources during tests
3. **Use Realistic Data**: Generate test data that closely resembles production data
4. **Run Tests Regularly**: Include performance tests in your CI/CD pipeline
5. **Analyze Trends**: Look for patterns and trends in the test results over time
6. **Document Findings**: Keep records of test configurations and results for future reference

## Troubleshooting

### Common Issues

1. **Application Not Starting**
   - Check if the database is running
   - Verify the database connection string
   - Check application logs for errors

2. **Connection Refused**
   - Ensure the application is running and accessible
   - Check for firewall rules blocking the connection

3. **High Error Rates**
   - Check application logs for errors
   - Verify that the test data is valid
   - Check for rate limiting

4. **Performance Degradation**
   - Monitor system resources (CPU, memory, disk I/O)
   - Check for database locks or slow queries
   - Look for memory leaks

5. **Test Timeout**
   - Increase the test timeout in the configuration
   - Check for long-running operations in the application

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
