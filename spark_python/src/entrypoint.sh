#!/bin/bash

set -e 

aws configure set aws_access_key_id "$AWS_ACCESS_KEY_ID"
aws configure set aws_secret_access_key "$AWS_SECRET_ACCESS_KEY"
aws configure set default.region us-west-2

values=$(aws secretsmanager get-secret-value --secret-id "${SECRET_NAME}" --query 'SecretString' --output text)
for val in $(echo "${values}" | jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]" ); do
    echo "$val" >> .env
done

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

echo "Generating feedback..."
COMMENT=$(python src/generate_comment.py)
if [[ $COMMENT ]]; then
  echo "---------------------------------------------------------------------------------"
  echo "---------------------------- LLM GENERATED RESPONSE -----------------------------"
  echo "$COMMENT"
  echo "---------------------------------------------------------------------------------"
  echo "---------------------------------------------------------------------------------"
fi
echo "Done!"
