"""
Script to create random users via a FastAPI endpoint.

Uses the Faker library to generate realistic names, and generates
unique emails by hashing the name and current timestamp.

Usage:
    python create_users.py --count 5
"""
import argparse
import hashlib
import random
import time
from typing import Optional, Dict

import requests
from faker import Faker


# ---- CONFIG ----
API_URL = "http://localhost:8080/users/"
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com"]

# ---- SETUP ----
faker = Faker()


def unique_email(name: str) -> str:
    """
    Generate a unique email address by hashing the name with the current timestamp.

    Args:
        name (str): Full name of the user.

    Returns:
        str: A unique email address.
    """
    domain = random.choice(EMAIL_DOMAINS)
    unique_str = f"{name}-{time.time_ns()}"  # nanosecond precision for better uniqueness
    hash_digest = hashlib.md5(unique_str.encode()).hexdigest()[:8]

    return f"{hash_digest}@{domain}"


def create_user() -> Optional[Dict]:
    """
    Create a single user via a POST request to the FastAPI endpoint.

    Returns:
        dict | None: The response JSON if successful, else None.
    """
    full_name: str = faker.name()
    email: str = unique_email(full_name)

    payload: Dict[str, str] = {
        "name": full_name,
        "email": email
    }

    try:
        response = requests.post(API_URL, json=payload)
    except requests.RequestException as e:
        print(f"❌ Request failed for {full_name} ({email}): {e}")
        return None

    if response.status_code == 200:
        print(f"✅ Created: {full_name} ({email})")
        return response.json()
    else:
        print(f"❌ Failed to create {full_name} ({email}): {response.status_code}")
        print(response.text)
        return None


def main() -> None:
    """
    Parse CLI arguments and create the specified number of users.
    """
    parser = argparse.ArgumentParser(description="Create random users via FastAPI endpoint.")
    parser.add_argument("--count", type=int, default=1, help="Number of users to create")
    args = parser.parse_args()

    for _ in range(args.count):
        create_user()


if __name__ == "__main__":
    main()
