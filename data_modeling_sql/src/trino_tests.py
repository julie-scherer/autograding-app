import os
from util import get_logger, get_submissions, get_submission_dir, get_trino_creds, get_runtime_env
from trino.dbapi import connect
from trino.auth import BasicAuthentication

logger = get_logger()
submission_dir = get_submission_dir()
testing = get_runtime_env()
trino_host, trino_port, trino_username, trino_password, trino_catalog, trino_schema = get_trino_creds()

assignment_schema = os.environ.get('ASSIGNMENT_SCHEMA')
drop_sql = f"DROP SCHEMA IF EXISTS {assignment_schema} CASCADE"
create_sql = f"CREATE SCHEMA {assignment_schema}"
use_sql = f"USE {assignment_schema}"

def init_trino():
  try:
    conn = connect(
      host=trino_host,
      port=trino_port,
      user=trino_username,
      catalog=trino_catalog,
      schema=trino_schema,
      auth=BasicAuthentication(trino_username, trino_password),
    )
    cur = conn.cursor()
    cur.execute(drop_sql)
    cur.execute(create_sql)
    cur.execute(use_sql)
    logger.info(f"Successfully executed queries: \n{drop_sql}\n{create_sql}\n{use_sql}\n")
    return True, 'Success'
  except Exception as e:
    error_message = f"Failed to initialize Trino! Error message: {str(e)}. You may need to wait a couple minutes and then try again."
    logger.info(error_message)
    return False, error_message

def execute_sql(query):
  try:
    conn = connect(
      host=trino_host,
      port=trino_port,
      user=trino_username,
      catalog=trino_catalog,
      schema=trino_schema,
      auth=BasicAuthentication(trino_username, trino_password),
    )
    cur = conn.cursor()
    cur.execute(use_sql)
    cur.execute(query)
    return True, 'Success'
  except Exception as e:
    error_message = f'{str(e.message)}'
    return False, error_message

def run_tests(filename, submission):
  passed, results = execute_sql(submission)
  if not passed:
    comment = f'Failed to run `{filename}` ➡️ "{results}"'
    return passed, comment
  return passed, results

def main(submissions: dict):
  if not submissions:
    logger.info('WARNING: No submissions found')
    return None
  
  initialized, results = init_trino()
  if not initialized:
    return False, results
  
  valid_submissions = {}
  comments = []
  for filename, submission in submissions.items():
    passed, comment = run_tests(filename, submission)
    if not passed:
      comments.append(comment)
    else:
      valid_submissions[filename] = submission
  
  if comments:
    formatted_text = '\n'.join(comments)
    return False, formatted_text
  else:
    return True, "All tests passed successfully"

if __name__ == "__main__":
  submissions = get_submissions(submission_dir)
  passed, comment = main(submissions)
  print(comment)
