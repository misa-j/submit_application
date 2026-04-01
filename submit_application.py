import os
import sys
import json
import requests
import hmac
import hashlib
from datetime import datetime

def main():
    # Required inputs
    name = os.getenv("NAME")
    email = os.getenv("EMAIL")
    resume_link = os.getenv("RESUME_LINK")
    repository_link = os.getenv("REPOSITORY_LINK")
    secret = bytearray(os.getenv("SECRET"), 'utf-8')

    if not all([name, email, resume_link, repository_link]):
        print("Error: Missing one or more required environment variables.")
        sys.exit(1)

    # Generate current ISO 8601 timestamp (with milliseconds + Z)
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # Build action_run_link automatically (works on GitHub)
    action_run_link = f"{os.getenv('GITHUB_SERVER_URL')}/{os.getenv('GITHUB_REPOSITORY')}/actions/runs/{os.getenv('GITHUB_RUN_ID')}"

    # Prepare payload with keys in alphabetical order
    payload = {
        "action_run_link": action_run_link,
        "email": email,
        "name": name,
        "repository_link": repository_link,
        "resume_link": resume_link,
        "timestamp": timestamp
    }

    # Create canonical compact JSON (no extra whitespace, sorted keys)
    json_body = json.dumps(payload, separators=(',', ':'), sort_keys=True)

    print("Submitting with this exact body:")
    print(json_body)

    # Compute HMAC-SHA256 signature
    signature = hmac.new(secret, json_body.encode("utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Signature-256": f"sha256={signature}"
    }

    url = "https://b12.io/apply/submission"

    try:
        response = requests.post(url, data=json_body, headers=headers, timeout=30)

        print(f"\nStatus code: {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                print("Success!")
                receipt = result.get("receipt")
                print(f"Receipt: {receipt}")
                if receipt:
                    print("\nCopy this receipt and paste it in the application form:")
                    print(receipt)
            except:
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