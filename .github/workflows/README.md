# GitHub Actions Workflows

This directory contains GitHub Actions workflow definitions for the Project Asylum CI/CD pipeline.

## Workflows

### build.yml - Optimized Docker Build Pipeline

**Purpose:** Build and publish Docker images with optimal caching and cost efficiency.

**Triggers:**
- Push to `main`, `develop`, or `copilot/**` branches
- Pull requests to `main` or `develop`
- Manual workflow dispatch

**Jobs:**

1. **build-base-image**
   - Builds the base ML image with heavy dependencies
   - Only runs when `requirements.txt` changes or manually triggered
   - Tags: `base-ml`, `base-ml-{timestamp}`, `base-ml-{sha}`

2. **build-ai-image** 
   - Builds the main application image
   - Runs on every push
   - Uses the pre-built base image
   - Tags: `ai`, `latest` (on main), `{branch}`, `{sha}`

3. **security-scan**
   - Scans images for vulnerabilities using Trivy
   - Results available in the Security tab

**Performance Features:**
- Pip package caching across runs
- Docker layer caching via GitHub Actions cache
- Concurrency control to cancel outdated builds
- Conditional base image builds

**Cache Keys:**
- Pip: `${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}`
- Docker Base: `type=gha,scope=base-ml`
- Docker App: `type=gha,scope=ai-app`

## Permissions Required

The workflow requires the following permissions:
- `contents: read` - Read repository contents
- `packages: write` - Push images to GitHub Container Registry
- `security-events: write` - Upload security scan results

## Environment Variables

- `REGISTRY`: Container registry URL (default: `ghcr.io`)
- `IMAGE_NAME`: Full repository name (auto-populated)

## Secrets Required

- `GITHUB_TOKEN`: Automatically provided by GitHub Actions (no configuration needed)

## Monitoring and Troubleshooting

**View Build Logs:**
1. Go to the Actions tab in GitHub
2. Select the workflow run
3. Click on individual jobs to see detailed logs

**Common Issues:**

- **Base image not found:** Build it manually via workflow dispatch
- **Cache miss:** First run or `requirements.txt` changed
- **Permission denied:** Check repository package permissions

**Performance Metrics:**
- Base image build: ~15 minutes (infrequent)
- App image build: ~1-2 minutes (typical)
- Total pipeline: ~2-3 minutes (typical code change)

## Customization

To customize the workflow:

1. **Add new build steps:** Edit the workflow file
2. **Change triggers:** Modify the `on:` section
3. **Adjust caching:** Update cache keys in the `cache` steps
4. **Add build args:** Modify the `build-args` in build steps

For more details, see [docs/ci-cd-optimizations.md](../../docs/ci-cd-optimizations.md).
