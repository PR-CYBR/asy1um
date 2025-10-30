# Testing Guide for Project Asylum

## Overview

This guide covers testing strategies for all components of Project Asylum.

## Prerequisites

```bash
# Install test dependencies
cd ai && pip install pytest pytest-cov pytest-mock
cd ../orchestration && npm install --save-dev jest supertest
```

## Unit Tests

### AI/ML Component

```bash
cd ai

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_anomaly_detector.py

# Run with verbose output
pytest -v
```

### Orchestration Component

```bash
cd orchestration

# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Integration Tests

### Start Test Environment

```bash
# Use test compose file
docker-compose -f docker-compose.test.yml up -d

# Wait for services to be ready
sleep 30
```

### Test Service Communication

```bash
# Test AI API
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "features": [[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                  0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]]
  }'

# Test Orchestration API
curl http://localhost:3001/health

# Test event flow
curl -X POST http://localhost:3001/events \
  -H "Content-Type: application/json" \
  -d '{
    "type": "anomaly_detected",
    "source": "test",
    "data": {"score": 85}
  }'
```

### Test Honeypot

```bash
# Test SSH honeypot
ssh -o StrictHostKeyChecking=no -p 2222 root@localhost
# Try some commands: ls, whoami, cat /etc/passwd

# Test Telnet honeypot
telnet localhost 2223
```

### Test Monitoring Stack

```bash
# Test Prometheus
curl http://localhost:9090/-/healthy

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up'

# Test Grafana
curl http://localhost:3000/api/health

# Test Elasticsearch
curl http://localhost:9200/_cluster/health
```

## End-to-End Tests

### Complete Workflow Test

```bash
#!/bin/bash
# e2e_test.sh

set -e

echo "Starting E2E tests..."

# 1. Start all services
docker-compose up -d
sleep 60

# 2. Train model
echo "Training AI model..."
docker-compose exec -T ai-api python train.py --synthetic --epochs 10

# 3. Generate honeypot activity
echo "Generating honeypot activity..."
for i in {1..10}; do
  sshpass -p "password" ssh -o StrictHostKeyChecking=no -p 2222 root@localhost "ls" || true
  sleep 2
done

# 4. Wait for logs to be processed
sleep 30

# 5. Check for anomaly detection
echo "Checking anomaly detection..."
ANOMALIES=$(curl -s http://localhost:8000/state | jq .last_anomaly_count)
echo "Detected $ANOMALIES anomalies"

# 6. Verify metrics
echo "Checking Prometheus metrics..."
UP=$(curl -s 'http://localhost:9090/api/v1/query?query=up' | jq '.data.result | length')
echo "Prometheus monitoring $UP targets"

# 7. Check logs in Elasticsearch
sleep 10
LOGS=$(curl -s http://localhost:9200/honeypot-logs-*/_count | jq .count)
echo "Elasticsearch has $LOGS log entries"

echo "E2E tests completed!"
```

## Performance Tests

### Load Testing AI API

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test AI API throughput
ab -n 1000 -c 10 -p test_data.json -T application/json \
   http://localhost:8000/predict
```

### Stress Testing Honeypot

```bash
# Install stress testing tool
pip install locust

# Run load test
locust -f tests/locustfile.py --host=http://localhost:2222
```

## Security Tests

### Vulnerability Scanning

```bash
# Scan Docker images
trivy image project-asylum/ai:latest
trivy image project-asylum/orchestration:latest

# Scan dependencies
cd ai && safety check
cd orchestration && npm audit
```

### Secret Detection

```bash
# Scan for secrets in code
pip install detect-secrets
detect-secrets scan --all-files
```

## Terraform Tests

### Validation

```bash
cd terraform

# Format check
terraform fmt -check -recursive

# Initialize
terraform init -backend=false

# Validate
terraform validate

# Plan
terraform plan -var-file=envs/dev/terraform.tfvars
```

### Infrastructure Tests

```bash
# Install Terratest (Go required)
go get github.com/gruntwork-io/terratest/modules/terraform

# Run infrastructure tests
cd tests/terraform
go test -v -timeout 30m
```

## Continuous Integration Tests

The CI/CD pipeline (`.github/workflows/deploy.yml`) runs:

1. **Lint**: Code style checks
2. **Terraform Validate**: Infrastructure validation
3. **Build**: Docker image builds
4. **Test**: Unit and integration tests
5. **Security Scan**: Vulnerability scanning

### Local CI Testing

```bash
# Install act (GitHub Actions local runner)
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash

# Run CI locally
act -j test
act -j build-docker-images
```

## Test Data Generation

### Generate Synthetic Log Data

```python
# generate_test_data.py
import json
import random
from datetime import datetime, timedelta

def generate_honeypot_logs(count=1000):
    logs = []
    start_time = datetime.now() - timedelta(hours=24)
    
    for i in range(count):
        log = {
            "timestamp": (start_time + timedelta(minutes=i)).isoformat(),
            "eventid": random.choice([
                "cowrie.session.connect",
                "cowrie.login.success",
                "cowrie.login.failed",
                "cowrie.command.input"
            ]),
            "src_ip": f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
            "username": random.choice(["root", "admin", "test", "user"]),
            "password": random.choice(["password", "123456", "admin"]),
            "command": random.choice(["ls", "whoami", "cat /etc/passwd", "wget"])
        }
        logs.append(log)
    
    return logs

if __name__ == "__main__":
    logs = generate_honeypot_logs()
    with open("test_logs.json", "w") as f:
        json.dump({"logs": logs}, f, indent=2)
```

## Monitoring Test Results

### Grafana Test Dashboard

Create a test dashboard to monitor:
- Test execution time
- Success/failure rates
- Coverage metrics
- Performance benchmarks

### Test Metrics in Prometheus

```promql
# Test execution duration
test_duration_seconds

# Test success rate
rate(test_passed_total[5m]) / rate(test_total[5m])

# Code coverage
code_coverage_percent
```

## Troubleshooting Tests

### Common Issues

1. **Services not ready**
   - Increase sleep time between operations
   - Use health check endpoints before proceeding

2. **Port conflicts**
   - Check for existing services: `netstat -tuln`
   - Modify ports in docker-compose.yml

3. **Memory issues**
   - Reduce test data size
   - Increase Docker memory limits

4. **Timing issues**
   - Add retries with exponential backoff
   - Increase timeouts for slow operations

### Debug Mode

```bash
# Run services with debug logging
DEBUG=* docker-compose up

# View detailed logs
docker-compose logs -f --tail=100

# Exec into container for debugging
docker-compose exec ai-api /bin/bash
docker-compose exec orchestration-api /bin/sh
```

## Test Coverage Goals

- **Unit Tests**: >80% coverage
- **Integration Tests**: All service interactions
- **E2E Tests**: Critical user workflows
- **Security Tests**: All dependencies and images
- **Performance Tests**: Load and stress scenarios

## Best Practices

1. **Isolate Tests**: Each test should be independent
2. **Clean Up**: Remove test data after tests
3. **Mock External Services**: Use mocks for third-party APIs
4. **Use Test Fixtures**: Reusable test data and setups
5. **Document Tests**: Clear test names and descriptions
6. **Automate**: Run tests in CI/CD pipeline
7. **Monitor Flaky Tests**: Track and fix unstable tests
8. **Regular Updates**: Keep test dependencies updated
