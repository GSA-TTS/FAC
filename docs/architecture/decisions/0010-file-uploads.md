# 10. File Uploads

Date: 2022-08-01

## Status

Accepted

## Context

The FAC will need to support file uploads and file storage. In order to support this, the FAC backend will need to validate the size and type of uploaded files, and scan each file with an antimalware tool.

## Decision

We will use the file upload and storage backend that was built for the DOJ Civil Rights Portal as a reference for our implementation. Because the Civil Rights Portal backend is built on the same technical stack as the FAC (Django, DRF, PostgreSQL, Cloud.gov), we expect few, if any, significant setbacks during implementation - we know that this approach works well for a similar use case on a similar system.

The Civil Rights Portal file attachment backend includes file type validation, file size validation, and antivirus scanning of uploaded files.

We will use Amazon S3 as our underlying file storage mechanism for several reasons:
 - It is simple to use for basic upload and download functionality
 - It can be extended with more robust functionality if needed (bulk downloads, pre-signed URLs, etc).
 - It is available as a managed service at cloud.gov

We will use the Boto3 library to interact with S3 from the Django application, as this is the official Python SDK provided and maintained by AWS.

We will use ClamAV, a free and open source antimalware toolkit, to perform virus scans on uploaded files.


## Consequences

 - Antimalware applications rely on very large and frequently-updated sets of virus definitions. This means that the cloud infrastructure supporting the ClamAV instance will require a significant memory allocation, which increases hosting costs.
 - The maximum allowed size for an uploaded file will need to be determined.
 - The set of allowed file types will need to be determined.
