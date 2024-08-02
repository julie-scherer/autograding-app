import os
import requests
import boto3
from util import get_logger, get_api_key, check_aws_creds, get_git_creds, get_assignment, get_submission_dir, get_submissions, get_changed_files, get_runtime_env
from openai import OpenAI

logger = get_logger()
submission_dir = get_submission_dir()
testing = get_runtime_env()

client = OpenAI(api_key=get_api_key())
assignment = get_assignment()
git_token, repo, pr_number = get_git_creds()
s3_bucket = check_aws_creds()

user_prompt = """
{homework_prompt}

Here is the student's submission (please note the SQL syntax should be Trino SQL):
```sql
{submission}
```
"""

def download_from_s3(s3_bucket: str, s3_path: str, local_path: str):
  s3 = boto3.client('s3')
  try:
    s3.download_file(s3_bucket, s3_path, local_path)
  except Exception as e:
    raise Exception(f"Failed to download from S3: {e}")


def get_system_prompt(s3_solutions_dir: str, local_solutions_dir: str) -> str:
  s3_path = f"{s3_solutions_dir}/system_prompt.md"
  local_path = os.path.join(local_solutions_dir, 'system_prompt.md')
  download_from_s3(s3_bucket, s3_path, local_path)
  if not os.path.exists(local_path):
    raise ValueError(f"Path does not exist: {local_path}")
  system_prompt = open(local_path, "r").read()
  return system_prompt


def get_homework_prompt(s3_solutions_dir: str, local_solutions_dir: str, submission_filename: str) -> dict:
  markdown_filename = f"{submission_filename.split('.')[0]}.md"
  s3_path = f"{s3_solutions_dir}/{markdown_filename}"
  local_path = os.path.join(local_solutions_dir, markdown_filename)
  download_from_s3(s3_bucket, s3_path, local_path)
  if not os.path.exists(local_path):
    raise ValueError(f"Path does not exist: {local_path}")
  homework_prompt = open(local_path, "r").read().format(student_schema='<ADD_SCHEMA_HERE>')
  return homework_prompt


def get_feedback(filename: str, system_prompt: str, user_prompt: str, testing: bool) -> str:
  comment = ''
  if not testing:
      response = client.chat.completions.create(
          model="gpt-4",
          messages=[
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_prompt},
          ],
          temperature=0,
      )
      comment = response.choices[0].message.content
  text = f"This is a LLM-generated comment for `{filename}`: \n{comment if comment else 'Tests passed. No feedback generated for testing purposes.'}"
  return text


def post_github_comment(git_token, repo, pr_number, comment, filename):
  url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments" 
  headers = {
      "Accept": "application/vnd.github+json",
      "Authorization": f"Bearer {git_token}",
      "X-GitHub-Api-Version": "2022-11-28"
  }
  data = {"body": comment}
  response = requests.post(url, headers=headers, json=data)
  if response.status_code != 201:
    logger.error(f"Failed to create comment. Status code: {response.status_code} \n{response.text}")
    raise Exception(f"Failed to create comment. Status code: {response.status_code} \n{response.text}")
  logger.info(f"✅ Added review comment for {filename} at https://github.com/{repo}/pull/{pr_number}")


def main(testing: bool, submissions: dict, files_to_process: list):    
  if not submissions:
    logger.warning('No submissions found.')
    return None
  if not files_to_process:
    logger.warning('No file changes were detected in the current push so no comments were generated. Please modify one or more of your submission files to receive LLM-generated feedback.')
    return None
  s3_solutions_dir = f"s3_bucket/homework-keys/{assignment}"
  local_solutions_dir = os.path.join(os.getcwd(), 'solutions', assignment)
  os.makedirs(local_solutions_dir, exist_ok=True)
  system_prompt = get_system_prompt(s3_solutions_dir, local_solutions_dir)
  for filename, submission in submissions.items():
    file_path = os.path.join(submission_dir, filename)
    if file_path in files_to_process:
      homework_prompt = get_homework_prompt(s3_solutions_dir, local_solutions_dir, filename)
      custom_user_prompt = user_prompt.format(homework_prompt=homework_prompt, submission=submission)
      comment = get_feedback(filename, system_prompt, custom_user_prompt, testing)
      if git_token and repo and pr_number:
          post_github_comment(git_token, repo, pr_number, comment, filename)

if __name__ == "__main__":
  submissions = get_submissions(submission_dir)
  files_to_process = get_changed_files()
  main(testing, submissions, files_to_process)
