### Make sure to have CF CLI on WSL2 Ubuntu
```
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```

### Make sure to have awscli installed
```
curl -x $https_proxy -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin


# Alerternative
pip install awscli --upgrade --user

# aws doesnt work with an x509 error? This fixed it on my WSL2 Ubuntu
pip install --upgrade cryptography==36.0.2
```

### Create a deployer account
If a deployer account **has not been created**, then simply run the following:
```
cd terraform/sandbox
../../bin/ops/create_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will create a `secrets.auto.tfvars` in the directory for use with terraform.

In the event that a deployer account **has already been created**:
```
cd terraform/sandbox
../../bin/ops/get_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will update a `secrets.auto.tfvars` in the directory for use with terraform.


### Give the deployer account permissions in the ${ENV}-egress space
You must have a role of SpaceManager to assign the deployer service account. Ask Alex, Bret or Matt to do this for you (but the assumption is it will be done for you. The space will only have this service account and will not need to be done more than once, unless the account gets deleted from the sandbox space)
```
cf space-users gsa-tts-oros-fac sandbox
cf set-space-role <uaa_unique_id> gsa-tts-oros-fac sandbox-egress SpaceDeveloper
```

### ASGS
Since we do not rely on the github meta workflow (yet) to handle ASGS, we must explictly ensure they are there. This operation will only need to be done once, but documenting for documentation purposes.

Security Groups:
```
cf bind-security-group trusted_local_networks gsa-tts-oros-fac --lifecycle running --space sandbox
cf bind-security-group trusted_local_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox

cf bind-security-group public_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox-egress
```

### Pre-Configuration
Navigate to the following folders in cli:
`terraform/shared/modules/sandbox-proxy` & `terraform/shared/modules/stream-proxy`
Run the following commands to generate a local `proxy.zip` so the module is able to see the zip artifact to deploy the applications with
```
terraform init \
  --backend-config=../shared/config/sandbox.tfvars

terraform plan \
  --backend-config=../shared/config/sandbox.tfvars
```
Alternatively, you can run `./prepare-proxy` in each folder.

### Generate a template for sandbox.tfvars
Since this is operating under the belief that you do not have a `shared/config/sandbox.tfvars` file, a helper script in `terraform/sandbox` has been provided. This will create a secrets file that we will edit in the next step.
```
cd terraform/sandbox/helper/
./create_tfvars.sh
```

### First Deployment
Navigate to `terraform/sandbox` and populate the secrets file, and then run the `./init.sh` script. This assumes you have a `sandbox.tfvars` in `terraform/shared/config/`. Below is an example of secrets that will need to have values inside the file:
```
branch_name             = "" # There is no default branch. This value should be the name of your branch. (ex <initials>/<feature> [as/terraform-work])
new_relic_license_key   = ""
pgrst_jwt_secret        = ""
sam_api_key             = ""
login_client_id         = ""
login_secret_key        = ""
django_secret_login_key = ""
```

Next, run `./plan.sh` script. You should see it creating ~20 resources.
Finally, run `./apply.sh` script and wait.

### Discoveries:
- It was discovered that the compiled css assets in the public s3 must be in the `backend/static/` folder when collectstatic is being run. Due to this, when it is run via github actions.. the `/static/compiled/` folder exists on the local file system, since the github runner does these steps, and handles keeping them in the local file system. To mitigate this for the terraform, we handle this in the `prepare_app.sh` script.
- When registering the application with login.gov, perform the following:
```
# Generate a public and private key
openssl req -nodes -x509 -days 365 -newkey rsa:2048 -keyout private.pem -out public.crt

# Upload the public.crt to login.gov application page

# Convert the private key to base64
cat private.pem | base64 -w 0 > django_key.txt

# The value in the django_key.txt will be your DJANGO_SECRET_LOGIN_KEY for shared/modules/config/sandbox.tfvars
```

### Investigate Further:
- It appears, that after getting the successful generation of the `compiled` staticfiles, we are running into an issue where the boot sequence collectstatic is taking > 3 minutes to process. I would imagine that under normal sequences, there are no updates, so it simply skips over everything. But, if for some reason it is actually processing and uploading them to the s3 bucket every time, this operation is causing us to trigger the "3 minute timeout" on cloud.gov. Since an operation is "hanging" and the health check fails due to the 3 minutes, it gets caught in a crash loop.
