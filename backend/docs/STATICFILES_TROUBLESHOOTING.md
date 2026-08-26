# Static Files Troubleshooting Guide

## Common Error: Missing Staticfiles Manifest Entry

### Symptom
Tests fail with error:
```
ValueError: Missing staticfiles manifest entry for 'js/copy-report-id.js'
```

### Root Cause
The Django staticfiles manifest (`staticfiles/staticfiles.json`) is out of sync with the actual static files. This happens because the project uses `whitenoise.storage.CompressedManifestStaticFilesStorage` which requires a manifest file to map static file names to their hashed versions.

### Solution
Run the Django `collectstatic` management command to rebuild the manifest:

```bash
cd /path/to/backend
python manage.py collectstatic --noinput
```

This will:
- Collect all static files from app directories into `staticfiles/`
- Generate/update the `staticfiles.json` manifest
- Create compressed and hashed versions of files
- Process and post-process files (e.g., CSS, JS minification)

### When to Run `collectstatic`

You should run `collectstatic` whenever:
1. **New static files are added** to the project
2. **Existing static files are modified**
3. **After pulling changes** that affect static files from git
4. **Before running tests locally** if encountering manifest errors
5. **In CI/CD pipelines** before deploying or running tests

### Automated Solution

The `collectstatic` command is already included in:
- **Dockerfile** (line 97): Runs during Docker image build
- **CI/CD**: Should be part of your test workflow

### Local Development

For local development, if you don't want to deal with the manifest:
1. The tests should handle this automatically via test settings
2. If issues persist, run `collectstatic` as shown above

### Additional Information

- **Static files location**: `static/` (source files)
- **Collected files location**: `staticfiles/` (output directory)
- **Manifest file**: `staticfiles/staticfiles.json`
- **Storage backend**: `whitenoise.storage.CompressedManifestStaticFilesStorage`

### Related Settings

In `config/settings.py`:
```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    },
}
```

This storage backend provides:
- File compression (gzip)
- Cache-busting via content hashing
- Manifest-based file lookup
- Efficient serving via WhiteNoise middleware
