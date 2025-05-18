# Test Coverage Badge

## Codecov Badge

Add the following markdown to your README.md to display the test coverage badge:

```markdown
[![codecov](https://codecov.io/gh/your-username/your-repo/branch/main/graph/badge.svg?token=YOUR-TOKEN-HERE)](https://codecov.io/gh/your-username/your-repo)
```

Replace the following placeholders:
- `your-username`: Your GitHub username or organization name
- `your-repo`: Your repository name
- `YOUR-TOKEN-HERE`: Your Codecov repository token (optional, but recommended for private repositories)

## Local Coverage Badge

If you want to display a badge for local test coverage, you can use the following approach:

1. First, generate the coverage report:
   ```bash
   python scripts/generate_coverage_report.py
   ```

2. Then add this to your README.md:
   ```markdown
   ![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)
   ```

   Update the percentage manually or use a script to update it automatically as part of your CI/CD pipeline.

## Custom Badge with Shields.io

For more customization options, you can use [Shields.io](https://shields.io/) to create custom badges:

```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?logo=python&logoColor=white&style=for-the-badge&label=Test%20Coverage)
```

## Updating the Badge in CI/CD

To automatically update the badge in your CI/CD pipeline, add this step to your workflow:

```yaml
- name: Update Coverage Badge
  run: |
    # Get coverage percentage from the coverage report
    COVERAGE=$(python -c "import json; print(round(json.load(open('coverage.json'))['totals']['percent_covered'], 2))")

    # Update README.md with the new badge
    sed -i "s/!\[Test Coverage\](https:\/\/img\.shields\.io\/badge\/coverage-)[0-9.]*%25/![Test Coverage](https:\/\/img\.shields\.io\/badge\/coverage-${COVERAGE}%25/g" README.md

    # Commit and push the changes
    git config --global user.name 'GitHub Actions'
    git config --global user.email 'actions@github.com'
    git add README.md
    git commit -m "docs: update test coverage badge to ${COVERAGE}%" || true
    git push
```

## Badge Styles

Here are some popular badge styles you can use:

### Flat
```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?style=flat)
```

### Flat Square
```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?style=flat-square)
```

### For the Badge
```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?style=for-the-badge)
```

### With Logo
```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen?logo=python&logoColor=white)
```

### With Custom Colors
```markdown
![Test Coverage](https://img.shields.io/badge/coverage-95%25-44cc11?color=44cc11&labelColor=555555&style=flat)
```

## Dynamic Badges

For dynamic badges that update automatically, consider using:

1. **Codecov** (as shown above)
2. **Coveralls**
3. **SonarCloud**
4. **Custom API endpoint** that serves badge images based on your latest test results

## Best Practices

1. **Minimum Coverage**: Set a minimum coverage threshold (e.g., 80%) and enforce it in your CI/CD pipeline
2. **Trend Analysis**: Monitor coverage trends over time to ensure it's not decreasing
3. **Meaningful Tests**: Focus on testing critical paths and edge cases, not just achieving high coverage numbers
4. **Exclude Generated Code**: Don't include auto-generated code in your coverage reports
5. **Review Failing Tests**: Investigate and fix failing tests promptly
