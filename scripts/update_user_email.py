"""
Script to update random users' emails via a FastAPI endpoint.

Connects to a PostgreSQL database to fetch existing users,
then sends PUT requests to update their email addresses.

Usage:
    python update_user_email.py --count 5
"""
import argparse
import hashlib
import random
import time
from typing import Optional, Tuple

import psycopg2
import requests
from faker import Faker


# ---- CONFIG ----
API_URL_BASE = "http://localhost:8080/users"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mock_data_generator_api",
    "user": "postgres",
    "password": "postgres",
}
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "icloud.com"]

faker = Faker()


# ---- FUNCTIONS ----
def unique_email(name: str) -> str:
    """
    Generate a unique email by hashing the name and current time.

    Args:
        name (str): Full name of the user.

    Returns:
        str: Unique email address.
    """
    domain = random.choice(EMAIL_DOMAINS)
    unique_str = f"{name}-{time.time_ns()}"
    hash_digest = hashlib.md5(unique_str.encode()).hexdigest()[:8]

    return f"{hash_digest}@{domain}".lower()


def get_random_user() -> Optional[Tuple[int, str]]:
    """
    Connect to PostgreSQL and get a random user.

    Returns:
        Tuple[int, str] | None: (user_id, name) or None if no users found.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM users ORDER BY RANDOM() LIMIT 1;")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return row if row else None
    except Exception as e:
        print(f"❌ Failed to query database: {e}")
        return None


def update_user_email(user_id: int, new_email: str) -> bool:
    """
    Send a PUT request to update the user's email.

    Args:
        user_id (int): User's ID.
        new_email (str): New email address.

    Returns:
        bool: True if successful, False otherwise.
    """
    url = f"{API_URL_BASE}/{user_id}?email={new_email}"
    try:
        response = requests.put(url)
        if response.status_code == 200:
            print(f"✅ Updated user {user_id} to email: {new_email}")
            return True
        else:
            print(f"❌ Failed to update user {user_id}: {response.status_code}")
            print(response.text)
            return False
    except requests.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def main() -> None:
    """
    Parse CLI arguments and update the specified number of user emails.
    """
    parser = argparse.ArgumentParser(description="Update user emails via FastAPI.")
    parser.add_argument("--count", type=int, default=1, help="Number of user email updates to perform")
    args = parser.parse_args()

    for _ in range(args.count):
        user = get_random_user()
        if not user:
            print("⚠️ No users found or DB error.")
            break

        user_id, name = user
        new_email = unique_email(name)
        update_user_email(user_id, new_email)


if __name__ == "__main__":
    main()
