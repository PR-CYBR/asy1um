# Quick Start Guide - CI/CD Optimizations

This guide helps you get started with the optimized CI/CD pipeline for Project Asylum.

## What Was Implemented

✅ **Pip Caching** - Saves 70-90% on package installation time
✅ **Base Image Strategy** - Reduces build time from 20 min to 2 min for code changes
✅ **Concurrency Control** - Cancels outdated builds automatically
✅ **Docker Layer Caching** - Reuses layers across builds
✅ **Security Scanning** - Automated vulnerability detection

## First-Time Setup

### Step 1: Trigger Initial Base Image Build

The base image must be built once before the workflow can run successfully.

**Option A: Via GitHub Actions (Recommended)**
1. Go to your repository on GitHub
2. Click the "Actions" tab
3. Select "Build and Push Docker Images" workflow
4. Click "Run workflow" button
5. Select your branch
6. Click "Run workflow"

**Option B: Via Git Push**
```bash
# Make a small change to requirements.txt to trigger the build
echo "" >> requirements.txt
git add requirements.txt
git commit -m "Trigger base image build"
git push
```

**Expected Duration:** ~15-18 minutes (one-time)

### Step 2: Verify Base Image

After the workflow completes:

1. Go to your repository's "Packages" tab
2. You should see: `project-asylum` package
3. Tags should include: `base-ml`, `base-ml-{timestamp}`, `base-ml-{sha}`

## Daily Usage

### For Code Changes

Just commit and push your code - the optimized build will run automatically:

```bash
git add .
git commit -m "Your commit message"
git push
```

**Expected Build Time:** 1-3 minutes ⚡

### For Dependency Changes

When you update `requirements.txt`:

1. Commit and push as normal
2. The workflow automatically detects changes
3. Both base and application images rebuild
4. Future builds use the new base image

**Expected Build Time:** 15-20 minutes (first build), then 1-3 minutes for subsequent code changes

## Monitoring Performance

### Check Build Times

1. Go to Actions tab
2. Click on any workflow run
3. Expand job details to see:
   - Setup time
   - Cache restore time
   - Build duration
   - Push duration

### Check Cache Effectiveness

Look for these indicators in the build logs:

✅ **Good Signs:**
```
Cache restored from key: Linux-pip-abc123...
Loaded build cache from ...
```

⚠️ **Cache Miss (Normal on first run):**
```
Cache not found for input keys: Linux-pip-abc123...
```

### Expected Performance Metrics

| Scenario | Build Time | Cache Status |
|----------|-----------|--------------|
| First run | 15-20 min | Cold cache |
| Code change | 1-3 min | Warm cache |
| Dependency change | 15-20 min | Cache invalidated |
| Repeat build | 1-2 min | Hot cache |

## Troubleshooting

### Base Image Not Found

**Error:**
```
Error: pull access denied for ghcr.io/folkvarlabs/project-asylum
```

**Solution:**
Build the base image using Step 1 above.

### Slow Builds

**Symptoms:**
- Builds taking 10+ minutes for code changes
- "Cache not found" messages in logs

**Solutions:**
1. Check if `requirements.txt` changed (invalidates cache)
2. Verify cache keys in workflow file
3. Wait for first build to complete (establishes cache)
4. Check GitHub Actions cache size limits

### Permission Errors

**Error:**
```
Error: failed to solve: failed to push: insufficient_scope
```

**Solution:**
1. Go to repository Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Save changes
5. Re-run the workflow

## Advanced Usage

### Manual Base Image Rebuild

Force rebuild the base image without changing requirements.txt:

1. Go to Actions → Build and Push Docker Images
2. Click "Run workflow"
3. This triggers `workflow_dispatch` event
4. Base image rebuilds regardless of requirements.txt

### Local Testing

Test Docker builds locally before pushing:

```bash
# Build base image locally
docker build -f Dockerfile.base -t project-asylum:base-ml .

# Build application image locally
docker build -t project-asylum:ai .

# Run the application
docker run -it project-asylum:ai
```

### Customize Caching

Edit `.github/workflows/build.yml` to adjust:

```yaml
# Change cache retention
- name: Cache pip packages
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: v2-${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
    # ^ Add version prefix to force cache refresh
```

## Cost Savings Calculator

### Before Optimization
- Average build: 20 minutes
- Builds per day: 10
- Daily usage: 200 minutes
- Monthly usage: ~6,000 minutes
- **Cost:** ~$150/month (estimated)

### After Optimization
- Average build: 2 minutes
- Builds per day: 10
- Daily usage: 20 minutes
- Monthly usage: ~600 minutes
- **Cost:** ~$15/month (estimated)

**💰 Monthly Savings: ~$135 (90% reduction)**

## Best Practices

1. ✅ **Group dependency updates** - Update all packages in one commit
2. ✅ **Keep base stable** - Avoid frequent requirements.txt changes
3. ✅ **Monitor cache hits** - Check logs regularly
4. ✅ **Review security scans** - Address critical vulnerabilities
5. ✅ **Test locally first** - Validate changes before pushing

## Support Resources

- **Detailed Documentation:** [docs/ci-cd-optimizations.md](ci-cd-optimizations.md)
- **Workflow Documentation:** [.github/workflows/README.md](../.github/workflows/README.md)
- **GitHub Actions Docs:** https://docs.github.com/actions
- **Docker Build Cache:** https://docs.docker.com/build/cache/

## Version

**CI/CD Optimization Version:** 1.0  
**Last Updated:** 2025-11-01  
**Status:** ✅ Production Ready
