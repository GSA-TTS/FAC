# 10. File Uploads

Date: 2022-08-01

## Status

Pending review

## Context

The FAC will need to support file uploads and file storage. In order to support this, the FAC backend will need to validate the size and type of uploaded files, and scan each file with an antimalware tool. The frontend will need to provide a file upload UI component, a success/failure indication, and client side validation.

## Decision

We will use the file upload and storage backend that was built for the [DOJ Civil Rights Portal](https://github.com/usdoj-crt/crt-portal) as a reference for our implementation. Because the Civil Rights Portal backend is built on the same technical stack as the FAC (Django, DRF, PostgreSQL, Cloud.gov), we expect few, if any, significant setbacks during implementation - we know that this approach works well for a similar use case on a similar system.

The Civil Rights Portal file attachment backend includes file type validation, file size validation, and antivirus scanning of uploaded files.

We will use Amazon S3 as our underlying file storage mechanism for several reasons:
 - It is simple to use for basic upload and download functionality
 - It can be extended with more robust functionality if needed (bulk downloads, pre-signed URLs, etc).
 - It is available as a managed service at cloud.gov

We will use the Boto3 library to interact with S3 from the Django application, as this is the official Python SDK provided and maintained by AWS.

We will use ClamAV, a free and open source antimalware toolkit, to perform virus scans on uploaded files.

For the frontend portion of this, we will:
- use the USWDS file upload component
- provide a success/fail indication for the file upload (Need to meet wtih UX on this.)
- provide client side validation


## Consequences

 - Antimalware applications rely on very large and frequently-updated sets of virus definitions. This means that the cloud infrastructure supporting the ClamAV instance will require a significant memory allocation, which increases hosting costs.
 - The maximum allowed size for an uploaded file will need to be determined.
 - The set of allowed file types will need to be determined.
 - The placement of the file upload component needs to be confirmed or designed. (Check with UX/Design teams)
 - The success/failure indicator needs to be confirmed or designed. (Check with UX/Design teams)
 - The destination on succcessful upload needs to be confirmed or designed. (Check with UX/Design teams)
