#!/usr/bin/env bash

DIRECTORY="../../shared/config/"
FILE="../../shared/config/sandbox.tfvars"
if [ ! -d "$DIRECTORY" ]; then
    echo "$DIRECTORY does not exist. Creating.."
    mkdir $DIRECTORY
  else
    echo "$DIRECTORY exists."
    if [ -f "$FILE" ]; then
      echo $FILE "exists, aborting. Update $FILE with the environments secrets."
      exit 1
    else
      echo $FILE "does not exist. Creating..."
    fi
fi
read -p "Enter the name of your working branch: " branch

cat > $FILE << EOM
# Generated with ./create_tfvars.sh
# You are responsible for populating the secrets. None of them will be supplied to you.
# Please reference the drive doc for the sandbox secrets!

branch_name             = "$branch"
new_relic_license_key   = ""
pgrst_jwt_secret        = ""
sam_api_key             = ""
login_client_id         = ""
login_secret_key        = ""
django_secret_login_key = ""
EOM
