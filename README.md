# Welcome to IntelliGraderAI

IntelliGraderAI is an innovative tool designed to provide students with immediate, AI-generated feedback on their homework assignments. By increasing students' revision performance before any human grading occurs, IntelliGraderAI saves time and effort for educators. 

Embrace the dynamic world of education with IntelliGraderAI, where creativity meets efficiency and the transformative impact of AI-driven insights elevates the teaching experience.

> ⚠️ *Please note this project is licensed under a proprietary license. For more details, please refer to the `LICENSE` file.*

## Quick Technical Summary

- **Containerization and Deployment**:
    - The autograding application runs in a Docker container and is deployed via a GitHub workflow.
    - It operates on the assumption that Pull Requests (PRs) are opened from forked repositories, utilizing the `pull_request_target` event in GitHub Actions to access secrets from the original repository.
- **Secrets Management**:
    - AWS Secrets Manager is used to store and retrieve necessary secrets for the application, although it is not used to run the GitHub workflow.
- **Integration with Homework Repositories**:
    - The current version requires integration and configuration within a template homework repository that sets up the environment for students' homework solutions.
- **Core Functionality**:
    - The main script is located in `src/generator.py`.
        - It retrieves homework solutions and user prompts from S3 (keeping these hidden).
        - Generates responses using ChatGPT.
        - Posts feedback as comments through the GitHub API.
- **Customization and Testing**:
    - The `src/tests` files can be customized, with test commands added in the `entrypoint.sh` script.
    - The Docker environment can be configured to install necessary packages and system requirements to run the test files.
    - The autograding application can be tested locally in Docker before deploying to the GitHub Action environment.
