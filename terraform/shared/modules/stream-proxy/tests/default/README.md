# Test the stream-proxy module
1. Authenticate with cloud.gov (`cf login -a api.fr.cloud.gov --sso`)
2. Copy `terraform.tfvars-template` to `terraform.tfvars` and edit to taste
3. Run `terraform init` to initialize the test Terraform environment
4. Run `terraform apply` to deploy a test fixture app and the proxy
5. Verify "PASSED" in the output
6. Run `terraform destroy` to tear everything down

## Test sequence

```mermaid
sequenceDiagram
    autonumber
    box test resources
        participant terraform
        participant validate.sh
        participant staticapp as stream-client
    end
    box module resources
        participant stream-proxy-creds
        participant stream-proxy
    end
    terraform->>staticapp: provision cloudfoundry_app
    terraform->>stream-proxy: provision 
    terraform->>stream-proxy-creds: provision cloudfoundry_user_provided_service
    terraform->>validate.sh: provision data.external.validate
    activate validate.sh
    validate.sh->>+staticapp: cf ssh staticapp -C /home/vcap/app/.profile
    activate staticapp
    staticapp->>stream-proxy-creds: get proxy domain:port [VCAP_SERVICES]
    activate staticapp
    staticapp->>+stream-proxy: GET / HTTP/1.1 [domain:port]
    stream-proxy->>+staticapp: TCP write [streamdomain:streamport]
    staticapp-->>-stream-proxy: TCP read [response bytes]
    stream-proxy-->>-staticapp: TCP write [response bytes]
    deactivate staticapp
    staticapp->>staticapp: compare response<br />bytes to index.html

    alt same
        staticapp-->>validate.sh: PASSED
    else different
        staticapp-->>validate.sh: FAILED
    end
    deactivate staticapp
    validate.sh-->>terraform: provision data.external.validate
    deactivate validate.sh
```

In summary:

1. Create a client that will also act as a mock-server
2. Create a stream proxy pointing to the mock-server
3. Have the client make a curl request to the proxy, then check that the bytes returned match the file that it served.