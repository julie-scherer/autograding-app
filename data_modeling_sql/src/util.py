import sys
import logging
import os
import re
from dotenv import load_dotenv

load_dotenv()

def get_logger():
  logger = logging.getLogger()
  formatter = logging.Formatter("%(message)s")
  stream_handler = logging.StreamHandler(sys.stdout)
  stream_handler.setFormatter(formatter)
  logger.addHandler(stream_handler)
  logger.setLevel(logging.INFO)
  return logger

def get_api_key():
  API_KEY = os.environ.get("OPENAI_API_KEY")
  if API_KEY is None:
    raise ValueError("You need to specify OPENAI_API_KEY environment variable!")
  return API_KEY

def check_aws_creds():
  AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
  AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
  AWS_S3_BUCKET = os.environ.get('AWS_S3_BUCKET')
  if AWS_ACCESS_KEY_ID is None:
    raise ValueError("You need to specify AWS_ACCESS_KEY_ID environment variable!")
  if AWS_SECRET_ACCESS_KEY is None:
    raise ValueError("You need to specify AWS_SECRET_ACCESS_KEY environment variable!")
  if AWS_S3_BUCKET is None:
    raise ValueError("You need to specify AWS_S3_BUCKET environment variable!")
  return AWS_S3_BUCKET
  
def get_git_creds():
  GIT_TOKEN = os.getenv("GIT_TOKEN")
  GITHUB_REPO = os.getenv("GITHUB_REPO")
  PR_NUMBER = os.getenv("PR_NUMBER")
  if GIT_TOKEN is None:
    raise ValueError("You need to specify GIT_TOKEN environment variable!")
  if GITHUB_REPO is None:
    raise ValueError("You need to specify GITHUB_REPO environment variable!")
  if PR_NUMBER is None:
    raise ValueError("You need to specify PR_NUMBER environment variable!")
  return GIT_TOKEN, GITHUB_REPO, PR_NUMBER

def get_trino_creds():
  TRINO_SERVER = os.environ.get('TRINO_SERVER')
  TRINO_PORT = int(os.environ.get('TRINO_PORT', 443))
  TRINO_USERNAME = os.environ.get('TRINO_USERNAME')
  TRINO_PASSWORD = os.environ.get('TRINO_PASSWORD')
  TRINO_PASSWORD = os.environ.get('TRINO_PASSWORD')
  TRINO_CATALOG = os.environ.get('TRINO_CATALOG')
  TRINO_SCHEMA = os.environ.get('TRINO_SCHEMA')
  return TRINO_SERVER, TRINO_PORT, TRINO_USERNAME, TRINO_PASSWORD, TRINO_CATALOG, TRINO_SCHEMA

def get_runtime_env():
  TESTING = bool(os.environ.get('TESTING', False))
  return TESTING
  
def get_assignment():
  ASSIGNMENT = os.environ.get("ASSIGNMENT")
  if ASSIGNMENT is None:
    raise ValueError("You need to specify ASSIGNMENT environment variable!")
  return ASSIGNMENT

def get_submission_dir():
  SUBMISSION_DIR = os.environ.get("SUBMISSION_DIR")
  if SUBMISSION_DIR is None:
    raise ValueError("You need to specify SUBMISSION_DIR environment variable!")
  if not os.path.exists(os.path.join(os.getcwd(), SUBMISSION_DIR)):
    raise ValueError(f"`{SUBMISSION_DIR}/` not found. Please update the SUBMISSION_DIR environment variable with a valid directory.")
  return SUBMISSION_DIR

def get_changed_files():
  CHANGED_FILES = os.environ.get("CHANGED_FILES")
  if CHANGED_FILES is None:
    raise ValueError("You need to specify CHANGED_FILES environment variable!")
  if not CHANGED_FILES:
    return []
  changed_files_list = CHANGED_FILES.split(',')
  for file in changed_files_list:
    if not os.path.exists(file):
      raise ValueError(f"`{file}` not found. Please make sure all files exist.")
  return changed_files_list

## Get the student's answers from the `submission` folder
def get_submissions(submission_dir: str) -> dict:
  submissions = {}
  submission_files = [f for f in os.listdir(submission_dir)]
  for filename in submission_files:
    file_path = os.path.join(submission_dir, filename)
    with open(file_path, "r") as file:
      file_content = file.read()
    if re.search(r'\S', file_content):
      submissions[filename] = file_content
  if not submissions:
    logging.warning('no submissions found')
    return None
  sorted_submissions = dict(sorted(submissions.items()))
  return sorted_submissions
