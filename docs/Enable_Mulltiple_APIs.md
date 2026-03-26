# Testing Multiple API Versions (FAC Backend)

## Overview

The current default API version is:

```
api_v1_1_0
```

Whenever making changes that impact API endpoints, you must test across multiple API versions to ensure backward compatibility and prevent regressions.

## Tools for Testing

You can use either:
- Postman (Desktop App)
- Postman VS Code Extension (preferred)

#### Enabling & Testing Multiple API Versions
About `api_v1_1_1`
- Includes the combined table
- Maintained but disabled by default

### Step 1: Prepare Your Environment
- Create or checkout your branch
- Stop containers:
  - Docker Desktop OR
  - Terminal:
    - `docker compose down`

### Step 2: Enable API Version
**Update Docker Config**

- Edit: `backend/docker-compose.yml`
  - line 165 by adding "api_v1_1_1" to the list `PGRST_DB_SCHEMAS`.

**Update API Versions Config**

- Edit: `backend/dissemination/api_versions.py`
  - line 10 by adding "api_v1_1_1" to the list `live["dissemination"]`.

### Step 3: Restart Containers
- `docker compose up`
  - Note: API startup may take a few minutes.

### Step 4: Test Both Versions
- Test Default Version

- **In Postman:**
`Accept-Profile: api_v1_1_0`
  - Run your endpoint tests.

- **Test New Version**
Update header:
`Accept-Profile: api_v1_1_1`
  - Run the same tests again.

