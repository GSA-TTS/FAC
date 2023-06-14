Scanning Process
===================

# About this document

This document is a catalog of information related to internal FAC scanning of docker images, and files.

# Information
We use the following tools, and their location relative to the FAC development:

- ClamAV
    - Upstream service: [ajilach/clamav-rest](https://github.com/ajilach/clamav-rest)
    - GSA-TTS ClamAV: [GSA-TTS/clamav-rest](https://github.com/GSA-TTS/clamav-rest)
        - GSA-TTS ClamAV Image: [GSA-TTS/clamav-rest package](https://github.com/GSA-TTS/clamav-rest/pkgs/container/clamav-rest%2Fclamav)
- Trivy
    - Upstream service: [aquasec/trivy](https://github.com/aquasecurity/trivy)
- FAC Scanning
    - [Scan with Trivy and publish as a FAC package](https://github.com/GSA-TTS/FAC/tree/main/.github/workflows/scan-images.yml)
        - Scanned and published image: [FAC/clamav package](https://github.com/GSA-TTS/FAC/pkgs/container/fac%2Fclamav)

# Scheduling
Each week, at `12:30a EST | 9:30p PST | 4:00a UTC` GSA-TTS automates a build of the ClamAV-Rest container and publishes it under the GSA-TTS packages. The package is tagged with the labels of `:YYYYMMDDD and :latest`. Then, at `4:00a EST | 1:30a PST | 8:00a UTC` the FAC repository has a job that, when run, will pull the latest image that was built, scan it with trivy, and, if there are no vulnerabilities, publish the trivy scanned image to the FAC packages.

# Scanning at a fundemental level
## Trivy scans
The trivy scans are automated, run weekly, and available outputs can be seen in the FAC Github Actions.

### Failed scans (Trivy has detected vulnerabilities)
```
┌───────────────────────┬────────────────┬──────────┬───────────────────┬──────────────────┬─────────────────────────────────────────────────────────────┐
│        Library        │ Vulnerability  │ Severity │ Installed Version │  Fixed Version   │                            Title                            │
├───────────────────────┼────────────────┼──────────┼───────────────────┼──────────────────┼─────────────────────────────────────────────────────────────┤
│ libcrypto3            │ CVE-2023-2650  │ HIGH     │ 3.0.8-r3          │ 3.0.9-r0         │ Possible DoS translating ASN.1 object identifiers           │
│                       │                │          │                   │                  │ https://avd.aquasec.com/nvd/cve-2023-2650                   │
├───────────────────────┤                │          │                   │                  │                                                             │
│ libssl3               │                │          │                   │                  │                                                             │
│                       │                │          │                   │                  │                                                             │
├───────────────────────┼────────────────┤          ├───────────────────┼──────────────────┼─────────────────────────────────────────────────────────────┤
│ ncurses-libs          │ CVE-2023-29491 │          │ 6.3_p20221119-r0  │ 6.3_p20221119-r1 │ Local users can trigger security-relevant memory corruption │
│                       │                │          │                   │                  │ via malformed data                                          │
│                       │                │          │                   │                  │ https://avd.aquasec.com/nvd/cve-2023-29491                  │
├───────────────────────┤                │          │                   │                  │                                                             │
│ ncurses-terminfo-base │                │          │                   │                  │                                                             │
│                       │                │          │                   │                  │                                                             │
│                       │                │          │                   │                  │                                                             │
└───────────────────────┴────────────────┴──────────┴───────────────────┴──────────────────┴─────────────────────────────────────────────────────────────┘
```

## ClamAV
The following is a list of status findings that may be returned during the scan:
```
200 - clean file = no KNOWN infections
400 - ClamAV returned general error for file
406 - INFECTED
412 - unable to parse file
501 - unknown request
```

The easiest place to start scanning files with ClamAV is to follow the [Development Documentation](https://github.com/GSA-TTS/FAC/blob/main/docs/development.md) and ensuring that you are able to run the following commands:
```bash
docker compose build
docker compose up
```
Once a the localstack has been build successfully, clamav will be available on `0.0.0.0:9000` for http connections and `0.0.0.0:9443` for https connections. When building the localstack, the scans will occur on port `9000`. Once we have a the clamav image running, we can then submit files for scans. *Note that this will not be covering scanning xls submissions through the FAC app.*

Once the localstack has been built successfully, a scan, in a new terminal can be run with
```bash
curl -i -F "file=@filename" http://localhost:9000/scan
```

### Scanning without the localstack
For some instances, we may want to scan a file without bringing up the entire application stack. In this use case, we will use the following commands:
First, pull the docker image. We can use either image.
```bash
docker pull ghcr.io/gsa-tts/fac/clamav:latest
docker pull ghcr.io/gsa-tts/clamav-rest/clamav:latest
```
Next, run the docker container. Our run command will vary based on the image selected above:
```bash
docker run -p 9000:9000 -p 9443:9443 -itd --name clamav ghcr.io/gsa-tts/fac/clamav:latest
docker run -p 9000:9000 -p 9443:9443 -itd --name clamav ghcr.io/gsa-tts/clamav-rest/clamav:latest
```
The GSA-TTS ClamAV image, along with the FAC ClamAV image support proxy configuration. We can pass the proxy information with `-e VAR="Value"` for use within the [entrypoint.sh](https://github.com/GSA-TTS/clamav-rest/blob/d7a07cb4678cb2c5f495cf8beee793571a4e6670/entrypoint.sh#L19-L32) with the following being used as *optional* environment variables.

`PROXY_SERVER` `PROXY_PORT` `PROXY_USERNAME` `PROXY_PASSWORD`
```bash
docker run -e PROXY_SERVER="https://www.aproxy.com" -p 9000:9000 -p 9443:9443 -itd --name clamav ghcr.io/gsa-tts/clamav-rest/clamav:latest
```

We can see that that the container has been built, and is in the process of running:
```bash
$ docker run -p 9000:9000 -p 9443:9443 -itd --name clamav ghcr.io/gsa-tts/fac/clamav:latest
90439baa0e2fb039c1e5bd6a8c78bbfb75000f4326e9067175ef71554d4a9e0e

$ docker container ls
CONTAINER ID   IMAGE                               COMMAND           CREATED          STATUS          PORTS                                            NAMES
90439baa0e2f   ghcr.io/gsa-tts/fac/clamav:latest   "entrypoint.sh"   38 seconds ago   Up 38 seconds   0.0.0.0:9000->9000/tcp, 0.0.0.0:9443->9443/tcp   clamav
```

Finally, let us scan a file. For ease of demonstration, we will be scanning the `.pa11yci` file at the root of the FAC repository.
```bash
curl -i -F "file=@filename" http://localhost:9000/scan
```
The scan on the file shows that there contains no virus
```bash
$ curl -i -F "file=@.pa11yci" http://localhost:9000/scan
HTTP/1.1 200 OK
Content-Type: application/json; charset=utf-8
Date: Wed, 14 Jun 2023 18:50:46 GMT
Content-Length: 37

{ "Status": "OK", "Description": "" }
```
If you are watching the logs of the container, or have docker desktop, we can view the container logs and validate that the file was scanned, and its result
![](image.png)

## Scanning an xls file through the workflow (Jadud)
