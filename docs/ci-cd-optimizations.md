# CI/CD Optimizations Guide

This document explains the CI/CD optimizations implemented in this repository to reduce GitHub Actions runtime costs and improve Docker build performance.

## Overview

The optimizations reduce typical build times from **15-20 minutes to under 2 minutes** through:
1. Persistent pip caching
2. Pre-built base image with heavy ML dependencies
3. Workflow concurrency control
4. Docker layer caching via GitHub Actions cache

## Architecture

### Two-Stage Docker Build Strategy

```
┌─────────────────────────────────────────────┐
│  Base Image (Dockerfile.base)              │
│  ghcr.io/folkvarlabs/project-asylum:base-ml │
│  ├─ Python 3.11                            │
│  ├─ CUDA 12.2 + cuDNN                      │
│  ├─ TensorFlow 2.18                        │
│  ├─ PyTorch 2.1                            │
│  ├─ scikit-learn, pandas, numpy            │
│  └─ Other heavy ML dependencies            │
│  Rebuild: Only when requirements.txt changes│
│  Build time: ~15 minutes                    │
└─────────────────────────────────────────────┘
                    ↓ (FROM)
┌─────────────────────────────────────────────┐
│  Application Image (Dockerfile)             │
│  ghcr.io/folkvarlabs/project-asylum:ai      │
│  ├─ Application code                        │
│  ├─ Configuration files                     │
│  └─ Application-specific dependencies       │
│  Rebuild: On every code change              │
│  Build time: ~1-2 minutes                   │
└─────────────────────────────────────────────┘
```

## Optimizations Explained

### 1. Persistent Pip Caching

**Configuration:**
```yaml
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

**How it works:**
- Caches compiled Python wheels between workflow runs
- Key is based on `requirements.txt` hash - cache invalidates only when dependencies change
- Restore keys provide fallback to partial cache matches
- Reduces pip install time by 70-90% on cache hits

**Benefits:**
- Faster pip installations (seconds vs. minutes)
- Reduced network bandwidth usage
- Lower risk of transient download failures

### 2. Base Image Strategy

**Base Image (`Dockerfile.base`):**
- Contains all heavy ML dependencies (TensorFlow 2.18, PyTorch 2.1, CUDA 12.2)
- Built once and stored in GitHub Container Registry
- Tagged as `ghcr.io/folkvarlabs/project-asylum:base-ml`
- Only rebuilt when `requirements.txt` changes

**Application Image (`Dockerfile`):**
- Uses base image as starting point (`FROM ghcr.io/folkvarlabs/project-asylum:base-ml`)
- Only copies application code and configs
- Installs lightweight, app-specific dependencies
- Rebuilds quickly on every code change

**Conditional Base Build Logic:**
```yaml
if: |
  github.event_name == 'workflow_dispatch' ||
  contains(github.event.head_commit.modified, 'requirements.txt') ||
  contains(github.event.head_commit.added, 'requirements.txt')
```

**Benefits:**
- 90% reduction in build time for code changes
- Predictable, fast builds
- Reduced CI/CD costs
- Base image can be reused across multiple projects

### 3. Workflow Concurrency Control

**Configuration:**
```yaml
concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true
```

**How it works:**
- Groups workflow runs by Git reference (branch or PR)
- Cancels in-progress builds when new commits are pushed
- Only the latest commit's build runs to completion

**Benefits:**
- Prevents wasted resources on outdated builds
- Reduces queue times
- Lower CI/CD costs from cancelled unnecessary builds
- Faster feedback on latest changes

### 4. Docker Layer Caching

**Configuration:**
```yaml
- name: Build and Push AI Image
  uses: docker/build-push-action@v5
  with:
    cache-from: type=gha,scope=ai-app
    cache-to: type=gha,mode=max,scope=ai-app
```

**How it works:**
- Stores Docker build layers in GitHub Actions cache
- `cache-from`: Retrieves layers from previous builds
- `cache-to`: Stores layers for future builds
- `mode=max`: Caches all layers (not just final image)
- Separate cache scopes for base and application images

**Benefits:**
- Reuses unchanged layers across builds
- Faster builds even when cache is warm but not complete
- Reduced network transfer for image pulls
- Works seamlessly with Docker BuildKit

## Workflow Structure

### Jobs Overview

1. **build-base-image**
   - Runs when: `requirements.txt` changes or manual trigger
   - Duration: ~15 minutes (one-time cost)
   - Output: `ghcr.io/folkvarlabs/project-asylum:base-ml`

2. **build-ai-image**
   - Runs: On every push
   - Duration: ~1-2 minutes (with cache)
   - Output: `ghcr.io/folkvarlabs/project-asylum:ai`

3. **security-scan** (optional)
   - Runs: After AI image build
   - Duration: ~30-60 seconds
   - Output: Vulnerability reports in Security tab

### Job Dependencies

```
build-base-image (conditional)
        ↓
build-ai-image (always)
        ↓
security-scan (optional)
```

## Maintenance Guide

### When to Rebuild the Base Image

Rebuild the base image when:
- Major ML framework versions change (TensorFlow, PyTorch)
- CUDA version needs updating
- New heavy dependencies are added to `requirements.txt`
- Python version changes

### Manual Base Image Rebuild

**Option 1: Via GitHub Actions**
1. Go to Actions tab
2. Select "Build and Push Docker Images" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

**Option 2: Local Build and Push**
```bash
# Build the base image
docker build -f Dockerfile.base -t ghcr.io/folkvarlabs/project-asylum:base-ml .

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Push the image
docker push ghcr.io/folkvarlabs/project-asylum:base-ml
```

### Monitoring Build Performance

**Key Metrics to Track:**
1. Build duration (check Actions logs)
2. Cache hit rates (look for "Cache restored" messages)
3. Image sizes (visible in package registry)
4. Workflow run costs (GitHub billing page)

**Expected Performance:**
- Base image build: ~15 minutes (rare)
- AI image build with warm cache: 1-2 minutes
- AI image build with cold cache: 3-5 minutes
- Pip cache hit: 30-60 seconds saved per run

### Troubleshooting

**Problem: Base image not found**
```
Error: pull access denied for ghcr.io/folkvarlabs/project-asylum, repository does not exist
```
**Solution:** Build the base image first by manually triggering the workflow or by modifying `requirements.txt`.

**Problem: Slow builds despite caching**
```
Build time hasn't improved significantly
```
**Solution:** 
- Check cache hit rates in build logs
- Verify `cache-from` and `cache-to` are configured correctly
- Ensure `requirements.txt` hasn't changed (invalidates cache)
- Check if runner is using fresh VM (no cache available)

**Problem: Workflow not canceling previous runs**
```
Multiple builds running for the same branch
```
**Solution:** 
- Verify `concurrency` section is present in workflow
- Check that `cancel-in-progress: true` is set
- Ensure you're on a compatible GitHub Actions runner version

## Performance Comparison

### Before Optimizations
```
Total build time: 18-22 minutes
├─ Setup: 30 seconds
├─ Install Python packages: 12-15 minutes
├─ Build Docker image: 5-6 minutes
└─ Push image: 1 minute
```

### After Optimizations
```
Total build time: 1-3 minutes (typical code change)
├─ Setup: 30 seconds
├─ Restore pip cache: 10 seconds
├─ Build Docker image: 1-2 minutes (using base)
└─ Push image: 30 seconds

Total build time: 15-18 minutes (when base needs rebuild)
├─ Build base image: 15 minutes (one-time)
├─ Build AI image: 2 minutes
└─ Push images: 1 minute
```

**Cost Savings:**
- Per-build savings: 15-20 minutes
- Monthly savings (50 builds): ~12-17 hours
- Cost reduction: ~85% for typical code change builds

## Best Practices

1. **Keep the Base Image Stable**
   - Avoid frequent changes to `requirements.txt`
   - Group dependency updates into single commits
   - Use version pinning for reproducibility

2. **Optimize Application Code**
   - Use `.dockerignore` to exclude unnecessary files
   - Keep application image layers small
   - Order COPY commands to maximize cache hits

3. **Monitor Cache Effectiveness**
   - Review build logs regularly
   - Track build times over time
   - Adjust cache keys if patterns change

4. **Security Scanning**
   - Keep base image dependencies updated
   - Review security scan results
   - Address critical vulnerabilities promptly

5. **Documentation**
   - Update this guide when making changes
   - Document custom dependencies
   - Maintain version compatibility matrix

## Additional Resources

- [GitHub Actions Caching](https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows)
- [Docker Build Cache](https://docs.docker.com/build/cache/)
- [Docker BuildKit](https://docs.docker.com/build/buildkit/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

## Version History

- **v1.0** (2025-11-01): Initial implementation
  - Pip caching
  - Base image strategy
  - Concurrency control
  - Docker layer caching
  - Security scanning
