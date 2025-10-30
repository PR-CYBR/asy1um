# Contributing to Project Asylum

Thank you for your interest in contributing to Project Asylum! This document provides guidelines and standards for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites
- Git
- Docker and Docker Compose
- Terraform >= 1.0
- Python >= 3.11
- Node.js >= 18
- Basic understanding of AI/ML, infrastructure as code, and honeypots

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/project-asylum.git
   cd project-asylum
   ```

2. **Install Dependencies**
   ```bash
   # Python dependencies
   cd ai
   pip install -r requirements.txt
   
   # Node.js dependencies
   cd ../orchestration
   npm install
   
   cd ..
   ```

3. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Start Development Environment**
   ```bash
   docker-compose up -d
   ```

## Branch Standards

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications
- `chore/` - Maintenance tasks

Examples:
- `feature/add-gcp-module`
- `fix/prometheus-metrics`
- `docs/update-readme`

### Branch Workflow

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit regularly

3. Push your branch and create a pull request

4. Address review feedback

5. Once approved, your PR will be merged

## Commit Standards

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### Examples

```
feat(terraform): add GCP module for cloud deployment

- Implement GCP provider configuration
- Add VPC and compute instance resources
- Include outputs for instance IPs
- Update documentation

Closes #123
```

```
fix(ai): resolve anomaly detection threshold calculation

The threshold was being calculated incorrectly for small datasets,
causing false positives. Updated to use percentile-based approach.

Fixes #456
```

### Commit Guidelines

- Use present tense ("add feature" not "added feature")
- Use imperative mood ("move cursor to..." not "moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests in footer
- Explain what and why, not how (code explains how)

## Pull Request Process

### Before Submitting

1. **Run Tests**
   ```bash
   # Python tests
   cd ai && pytest
   
   # Node.js tests
   cd orchestration && npm test
   ```

2. **Lint Code**
   ```bash
   # Python
   flake8 ai/ --max-line-length=120
   black ai/ --check
   
   # JavaScript
   cd orchestration && npm run lint
   
   # Terraform
   cd terraform && terraform fmt -check
   ```

3. **Update Documentation**
   - Update README.md if adding features
   - Add inline code comments for complex logic
   - Update relevant markdown files in `docs/`

4. **Test Locally**
   ```bash
   docker-compose up -d
   # Verify your changes work as expected
   ```

### PR Title Format

Similar to commit messages:
```
<type>(<scope>): <description>
```

Examples:
- `feat(honeypot): add Honeyd support`
- `fix(orchestration): correct event handling logic`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- List of specific changes
- Another change
- Yet another change

## Testing
- [ ] Local testing completed
- [ ] Unit tests added/updated
- [ ] Integration tests passed
- [ ] Documentation updated

## Screenshots (if applicable)
Add screenshots for UI changes

## Related Issues
Closes #XXX
Relates to #YYY

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] Tests added/updated and passing
- [ ] Dependent changes merged
```

## Code Style Guidelines

### Python (PEP 8 + Black)

```python
# Use type hints
def analyze_logs(log_data: List[Dict], threshold: float = 0.5) -> Dict[str, Any]:
    """
    Analyze logs for anomalies.
    
    Args:
        log_data: List of log entries
        threshold: Anomaly detection threshold
        
    Returns:
        Dictionary with analysis results
    """
    pass

# Use descriptive names
anomaly_count = 0
is_critical = False

# Constants in UPPERCASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30
```

### JavaScript (Standard Style)

```javascript
// Use const/let, not var
const apiUrl = 'http://localhost:8000'
let retryCount = 0

// Use arrow functions for callbacks
const processEvent = async (event) => {
  // Handle event
}

// Use async/await over promises
async function fetchData() {
  try {
    const response = await axios.get(url)
    return response.data
  } catch (error) {
    logger.error(error)
  }
}

// Use descriptive names
const anomalyDetectionResult = await analyzeData(features)
```

### Terraform (HashiCorp Style)

```hcl
# Use snake_case for resource names
resource "aws_instance" "honeypot_node" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  tags = merge(var.tags, {
    Name = "honeypot-${var.environment}"
  })
}

# Variables with descriptions
variable "node_count" {
  description = "Number of honeypot nodes to deploy"
  type        = number
  default     = 3
}

# Outputs with descriptions
output "instance_ips" {
  description = "IP addresses of deployed instances"
  value       = aws_instance.honeypot_node[*].public_ip
}
```

## Testing Guidelines

### Unit Tests

- Write tests for all new functions
- Aim for >80% code coverage
- Use descriptive test names
- Test edge cases and error conditions

```python
# Python test example
def test_anomaly_detector_with_high_anomaly_rate():
    detector = AnomalyDetector()
    X_train = np.random.randn(1000, 20)
    detector.train(X_train)
    
    X_test = np.random.randn(100, 20) + 5  # Anomalies
    results = detector.predict(X_test)
    
    assert results['anomaly_count'] > 50
    assert results['threshold'] > 0
```

### Integration Tests

- Test component interactions
- Use Docker Compose for test environment
- Clean up after tests

## Documentation Standards

### Code Comments

```python
# Good: Explains why
# Calculate threshold at 95th percentile to minimize false positives
threshold = np.percentile(scores, 95)

# Bad: Explains what (obvious from code)
# Calculate percentile
threshold = np.percentile(scores, 95)
```

### Markdown Documentation

- Use clear headings
- Include code examples
- Add diagrams where helpful (Mermaid supported)
- Keep line length reasonable (~80-100 chars)

## Security Guidelines

1. **Never commit secrets**
   - Use `.env` files (in `.gitignore`)
   - Use environment variables
   - Use secret management tools (Vault, etc.)

2. **Validate input**
   - Sanitize user input
   - Use type checking
   - Validate API parameters

3. **Follow least privilege**
   - Minimal IAM permissions
   - Restricted network access
   - Container security best practices

4. **Keep dependencies updated**
   - Regular security updates
   - Scan for vulnerabilities
   - Use lock files

## Review Process

### For Contributors

- Be open to feedback
- Respond to comments promptly
- Make requested changes
- Be patient during review

### For Reviewers

- Be constructive and respectful
- Explain reasoning for suggestions
- Approve when ready
- Provide clear feedback

## Getting Help

- **Issues**: Open an issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check `docs/` directory
- **Examples**: See existing code for patterns

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to Project Asylum! 🎉
