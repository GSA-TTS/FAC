### Make sure to have CF CLI on WSL2 Ubuntu

You must be running version 8+ of the CF client for the helper scripts to work.

```bash
cf --version
```

Will likely report v8.8 or higher. Version 7 will not work.

```bash
# ...first add the Cloud Foundry Foundation public key and package repository to your system
wget -q -O - https://packages.cloudfoundry.org/debian/cli.cloudfoundry.org.key | sudo apt-key add -
echo "deb https://packages.cloudfoundry.org/debian stable main" | sudo tee /etc/apt/sources.list.d/cloudfoundry-cli.list
# ...then, update your local package index, then finally install the cf CLI
sudo apt-get update
sudo apt-get install cf8-cli
```

### Make sure to have awscli installed
```bash
curl -x $https_proxy -L "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && rm awscliv2.zip
./aws/install -i ~/usr -b ~/bin


# Alternative
pip install awscli --upgrade --user

# aws doesnt work with an x509 error? This fixed it on my WSL2 Ubuntu
pip install --upgrade cryptography==36.0.2
```

### Create a deployer account
If a deployer account **has not been created**, then simply run the following:
```bash
cd terraform/sandbox
../../bin/ops/create_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will create a `secrets.auto.tfvars` in the directory for use with terraform.

In the event that a deployer account **has already been created**:
```bash
cd terraform/sandbox
../../bin/ops/get_service_account.sh -o gsa-tts-oros-fac -s sandbox -u sandbox-deployer >> secrets.auto.tfvars
```
This will update a `secrets.auto.tfvars` in the directory for use with terraform.


### Give the deployer account permissions in the ${ENV}-egress space

*This has already been done. This section is for documentation only.*

You must have a role of SpaceManager to assign the deployer service account. Ask Alex, Bret or Matt to do this for you (but the assumption is it will be done for you. The space will only have this service account and will not need to be done more than once, unless the account gets deleted from the sandbox space)
```bash
cf space-users gsa-tts-oros-fac sandbox
cf set-space-role <uaa_unique_id> gsa-tts-oros-fac sandbox-egress SpaceDeveloper
```

### ASGS

*This has already been done. This section is for documentation only.*

Since we do not rely on the github meta workflow (yet) to handle ASGS, we must explictly ensure they are there. This operation will only need to be done once.

Security Groups:
```bash
cf bind-security-group trusted_local_networks gsa-tts-oros-fac --lifecycle running --space sandbox
cf bind-security-group trusted_local_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox

cf bind-security-group public_networks_egress gsa-tts-oros-fac --lifecycle running --space sandbox-egress
```

### Pre-Configuration

Since this is operating under the belief that you do not have a `shared/config/sandbox.tfvars` file, a helper script in `terraform/sandbox` has been provided. This will create a secrets file that we will edit before attempting a deployment.
```bash
cd terraform/sandbox/helper/
./create_tfvars.sh
```

```t
branch_name             = "" # There is no default branch. This value should be the name of your branch. (ex <initials>/<feature> [as/terraform-work])
new_relic_license_key   = ""
pgrst_jwt_secret        = ""
sam_api_key             = ""
login_client_id         = ""
login_secret_key        = ""
django_secret_login_key = ""
```

Next, navigate to `terraform/shared/config` and create a `backend.tfvars` file. This will be used for the s3 partial configuration to store the terraform state. This will alleviate storing the `terraform.tfstate` on any one local file system, and when you run `terraform init` for the first time, it will read from the state, and inform terraform what resources already exist.

Populate these values from the output of `cf service-key sandbox-terraform-state sandbox-terraform-state-key`. This is a manually created s3 bucket, outside of terraforms knowledge, for the explicit purpose of storing the `terraform.tfstate`.
```t
bucket     = "" # bucket value (non friendly name)
key        = "/"
region     = "us-gov-west-1"
access_key = "" # access_key_id value
secret_key = "" # secret_access_key value

```

Navigate to `terraform/shared/modules/sandbox-proxy`, and run the following two commands.

```bash
terraform init --backend-config=../shared/config/sandbox.tfvars
```

This will issue a warning. Then run:

```bash
terraform plan
```

You'll be prompted for values; hit enter to leave them blank. When you are done, you should have `proxy.zip` in your current folder.

Then, navigate to `terraform/shared/modules/stream-proxy` (or `cd ../../modules/stream-proxy`) and run the same two commands:

```bash
terraform init --backend-config=../shared/config/sandbox.tfvars

terraform plan
```

Again, leave the prompts blank. Check you have a `proxy.zip`.

### First Deployment

Make sure you are in the sandbox environment.

```bash
cf t -s sandbox
```

... FIXME ... destroy on clean environment?

Navigate to `terraform/sandbox/helper_scripts` and then run the `./init.sh` script. This assumes you have a `sandbox.tfvars` in `terraform/shared/config/` from previous steps.

Now, run `./destroy.sh`. This tears down anything in the `sandbox` environment that may have been left from previous deploys (by you or others).

Next, run `./plan.sh` script. You should see it creating ~20 resources.
Finally, run `./apply.sh` script and wait.

### Discoveries:
- It was discovered that the compiled css assets in the public s3 must be in the `backend/static/` folder when collectstatic is being run. Due to this, when it is run via github actions.. the `/static/compiled/` folder exists on the local file system, since the github runner does these steps, and handles keeping them in the local file system. To mitigate this for the terraform, we handle this in the `prepare_app.sh` script.
- When registering the application with login.gov, perform the following:
```bash
# Generate a public and private key
openssl req -nodes -x509 -days 365 -newkey rsa:2048 -keyout private.pem -out public.crt

# Upload the public.crt to login.gov application page

# Convert the private key to base64
cat private.pem | base64 -w 0 > django_key.txt

# The value in the django_key.txt will be your DJANGO_SECRET_LOGIN_KEY for shared/modules/config/sandbox.tfvars
```

### Investigate Further:
- It appears, that after getting the successful generation of the `compiled` staticfiles, we are running into an issue where the boot sequence collectstatic is taking > 3 minutes to process. I would imagine that under normal sequences, there are no updates, so it simply skips over everything. But, if for some reason it is actually processing and uploading them to the s3 bucket every time, this operation is causing us to trigger the "3 minute timeout" on cloud.gov. Since an operation is "hanging" and the health check fails due to the 3 minutes, it gets caught in a crash loop.
