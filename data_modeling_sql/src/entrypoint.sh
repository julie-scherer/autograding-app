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

echo "Executing SQL queries..."

RETURN_VALUE=$(python src/trino_tests.py)

last_line=$(echo "$RETURN_VALUE" | tail -n 1)

if [[ "$last_line" == 'All tests passed successfully' ]]; then
  echo "Tests passed! Great work! Generating feedback..."
  python src/generate_comment.py
  echo "Done!"
else
  echo "---------------------------------------------------------------------------------"
  echo "------------------------------- ❌ TESTS FAILED ❌ -------------------------------"
  echo "$RETURN_VALUE"
  echo "----------------------------------------------------------------------------------"
  echo "----------------------------------------------------------------------------------"
  echo "Please update your submission and try again."
  exit 1
fi