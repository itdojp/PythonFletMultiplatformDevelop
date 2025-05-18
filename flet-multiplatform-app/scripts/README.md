# Performance Testing Scripts

This directory contains scripts for running and analyzing performance tests for the application.

## Prerequisites

1. Python 3.8+
2. PostgreSQL database (for testing)
3. Required Python packages (install with `pip install -r requirements-perf.txt`)

## Running Performance Tests

### Run All Performance Tests

```bash
# From the project root directory
python scripts/run_performance_tests.py
```

### Run a Specific Test Type

```bash
# Run only load tests
python scripts/run_performance_tests.py --test-type load_test

# Run only stress tests
python scripts/run_performance_tests.py --test-type stress_test

# Run only endurance tests
python scripts/run_performance_tests.py --test-type endurance_test

# Run only scalability tests
python scripts/run_performance_tests.py --test-type scalability_test
```

### Using a Custom Configuration

```bash
python scripts/run_performance_tests.py --config path/to/config.json
```

## Test Configuration

Performance test configuration is stored in `tests/performance/config/perf_config.json`. You can modify this file or provide a custom configuration file using the `--config` option.

## Test Results

Test results are stored in the following directories:

- **Test Reports**: `test-results/performance/` - Contains JUnit XML test reports
- **Performance Metrics**: `reports/performance/` - Contains performance metrics and visualizations
- **HTML Report**: `reports/performance/performance_report.html` - Comprehensive HTML report

## Analyzing Results

To analyze test results and generate a report without running the tests again:

```bash
python tests/performance/analyze_results.py
```

## CI/CD Integration

The performance tests can be integrated into your CI/CD pipeline. See the `.github/workflows/ci-cd-pipeline.yml` file for an example of how to run the tests in a GitHub Actions workflow.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**: Ensure PostgreSQL is running and the connection string in the test configuration is correct.
2. **Port Conflicts**: If port 8000 is already in use, you may need to stop the conflicting service or change the port in the test configuration.
3. **Missing Dependencies**: Make sure all required Python packages are installed using `pip install -r requirements-perf.txt`.

### Debugging

To enable debug output, set the `LOG_LEVEL` environment variable to `DEBUG`:

```bash
LOG_LEVEL=DEBUG python scripts/run_performance_tests.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
