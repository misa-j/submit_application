import os
import sys
import json
import requests
from datetime import datetime


def main():
    # Get inputs from environment variables (set in GitHub Actions)
    name = os.getenv("NAME")
    email = os.getenv("EMAIL")
    resume_link = os.getenv("RESUME_LINK")
    repository_link = os.getenv("REPOSITORY_LINK")

    if not all([name, email, resume_link, repository_link]):
        print(
            "Error: Missing required environment variables (NAME, EMAIL, RESUME_LINK, REPOSITORY_LINK)"
        )
        sys.exit(1)

    # Generate current ISO 8601 timestamp with milliseconds
    timestamp = datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

    # GitHub provides these automatically in Actions
    action_run_link = (
        os.getenv("GITHUB_SERVER_URL")
        + "/"
        + os.getenv("GITHUB_REPOSITORY")
        + "/actions/runs/"
        + os.getenv("GITHUB_RUN_ID")
    )

    payload = {
        "timestamp": timestamp,
        "name": name,
        "email": email,
        "resume_link": resume_link,
        "repository_link": repository_link,
        "action_run_link": action_run_link,
    }

    print("Submitting application with payload:")
    print(json.dumps(payload, indent=2))

    url = "https://b12.io/apply/submission"

    try:
        response = requests.post(url, json=payload, timeout=30)

        print(f"Status code: {response.status_code}")

        if response.ok:
            print("Application submitted successfully!")
            print("Response:", response.text)
        else:
            print("Submission failed")
            print("Response:", response.text)
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
