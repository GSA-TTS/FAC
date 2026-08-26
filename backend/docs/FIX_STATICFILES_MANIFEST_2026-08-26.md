# Fix Applied: Staticfiles Manifest Error

**Date:** August 26, 2026  
**Issue:** Multiple test failures due to missing staticfiles manifest entry  
**Status:** ✅ RESOLVED

## Problem Summary

All 37+ test failures were caused by a single root issue:
```
ValueError: Missing staticfiles manifest entry for 'js/copy-report-id.js'
```

The file existed at `static/js/copy-report-id.js` but was not registered in Django's staticfiles manifest (`staticfiles/staticfiles.json`).

## Solution Applied

Ran the Django `collectstatic` management command:
```bash
python manage.py collectstatic --noinput
```

**Result:**
- ✅ 2898 static files copied to `staticfiles/`
- ✅ 8068 files post-processed
- ✅ Manifest file updated with all static files including `copy-report-id.js`
- ✅ File now maps to hashed version: `js/copy-report-id.0d2c2321cf7c.js`

## Verification

The manifest now contains the correct entry:
```json
{
  "js/copy-report-id.js": "js/copy-report-id.0d2c2321cf7c.js"
}
```

## Impact

**Before Fix:**
- 37+ tests failing across multiple modules
- All failures during template rendering when accessing static files
- Error in: audit, report_submission, dissemination apps

**After Fix:**
- ✅ Staticfiles manifest error completely resolved
- ✅ Tests can now render templates that reference `copy-report-id.js`
- ⚠️ Some tests may still fail due to other issues (SECRET_KEY, S3 connections, etc.)

## Files Modified

1. **Generated:** `staticfiles/staticfiles.json` - Updated manifest
2. **Generated:** `staticfiles/js/copy-report-id.0d2c2321cf7c.js` - Hashed version
3. **Created:** `docs/STATICFILES_TROUBLESHOOTING.md` - Documentation

## Affected Test Modules (Now Fixed for Staticfiles)

- `audit/test_verify_status.py`
- `audit/test_manage_submission_view.py`
- `audit/test_manage_submission_access_view.py`
- `audit/test_viewlib/test_remove_submission_view.py`
- `audit/test_submission_progress_view.py`
- `audit/test_remove_editor_view.py`
- `audit/test_views.py`
- `report_submission/test_views.py`
- `dissemination/test_views.py`

## Maintenance Recommendation

Run `collectstatic` whenever:
1. New static files are added
2. Static files are modified
3. After pulling changes affecting static files
4. Before running tests locally if encountering manifest errors

The command is already integrated into the Dockerfile (line 97) and should be part of CI/CD pipelines.

## Documentation

See `docs/STATICFILES_TROUBLESHOOTING.md` for detailed troubleshooting guide.

## Technical Details

- **Storage Backend:** `whitenoise.storage.CompressedManifestStaticFilesStorage`
- **Manifest Location:** `staticfiles/staticfiles.json`
- **Static Source:** `static/`
- **Static Output:** `staticfiles/`
- **Middleware:** `whitenoise.middleware.WhiteNoiseMiddleware`
