#!/usr/bin/env python3
import sqlite3
import os
import shutil
import subprocess
import hashlib
import getpass
from datetime import datetime

# Constants
DB_PATH = "/var/lib/casaos/db/user.db"
BACKUP_PATH = "/var/lib/casaos/db/user_backup.db"
SERVICE_NAME = "casaos-user-service.service"

# Helper Functions
def check_casaos_installation():
    """Check if CasaOS is installed by verifying the database and service existence."""
    if not os.path.exists(DB_PATH):
        print(f"Error: CasaOS database file '{DB_PATH}' not found. Is CasaOS installed?")
        return False

    service_status = subprocess.run(
        ["systemctl", "status", SERVICE_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if service_status.returncode != 0:
        print(f"Error: CasaOS service '{SERVICE_NAME}' not found or not running.")
        return False

    return True

def backup_database():
    """Create a backup of the database."""
    try:
        shutil.copy(DB_PATH, BACKUP_PATH)
        print(f"Backup created at {BACKUP_PATH}")
    except Exception as e:
        print(f"Failed to create backup: {e}")
        exit(1)

def hash_password(password):
    """Hash the password using MD5."""
    return hashlib.md5(password.encode()).hexdigest()

def connect_db():
    """Connect to the SQLite database."""
    try:
        return sqlite3.connect(DB_PATH)
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        exit(1)

def manage_service(action):
    """Start or stop the CasaOS user service."""
    subprocess.run(["sudo", "systemctl", action, SERVICE_NAME], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def list_users():
    """List all users in the database."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, role FROM o_users")
        users = cursor.fetchall()
        if users:
            print("\nUsers in the database:")
            for user in users:
                print(f"ID: {user[0]}, Username: {user[1]}, Role: {user[2]}")
        else:
            print("\nNo users found.")
    except sqlite3.Error as e:
        print(f"Error fetching users: {e}")
    finally:
        conn.close()

def add_user():
    """Add a new user to the database."""
    username = input("Enter new username: ").strip()
    password = getpass.getpass("Enter new password: ").strip()

    if not username or not password:
        print("Username and password cannot be empty.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    try:
        # Check for duplicate username
        cursor.execute("SELECT 1 FROM o_users WHERE username = ?", (username,))
        if cursor.fetchone():
            print(f"Error: A user with the username '{username}' already exists.")
            return

        hashed_password = hash_password(password)
        created_at = datetime.now().isoformat()

        # Insert the user into the database
        cursor.execute(
            "INSERT INTO o_users (username, password, role, created_at) VALUES (?, ?, ?, ?)",
            (username, hashed_password, "admin", created_at),
        )
        conn.commit()
        print(f"User '{username}' added successfully.")
    except sqlite3.Error as e:
        print(f"Error adding user: {e}")
    finally:
        conn.close()

def edit_password():
    """Edit the password of an existing user."""
    user_id = input("Enter the ID of the user to edit: ").strip()
    new_password = getpass.getpass("Enter the new password: ").strip()

    if not user_id or not new_password:
        print("User ID and new password cannot be empty.")
        return

    hashed_password = hash_password(new_password)
    updated_at = datetime.now().isoformat()

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE o_users SET password = ?, updated_at = ? WHERE id = ?",
            (hashed_password, updated_at, user_id),
        )
        if cursor.rowcount > 0:
            conn.commit()
            print("Password updated successfully.")
        else:
            print("User ID not found.")
    except sqlite3.Error as e:
        print(f"Error updating password: {e}")
    finally:
        conn.close()

def remove_user():
    """Remove a user from the database."""
    user_id = input("Enter the ID of the user to remove: ").strip()

    if not user_id:
        print("User ID cannot be empty.")
        return

    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM o_users WHERE id = ?", (user_id,))
        if cursor.rowcount > 0:
            conn.commit()
            print("User removed successfully.")
        else:
            print("User ID not found.")
    except sqlite3.Error as e:
        print(f"Error removing user: {e}")
    finally:
        conn.close()

def reset_database():
    """Reset the database by deleting the user.db file."""
    confirm = input("Are you sure you want to reset the database? This will delete all users! (yes/no): ").strip().lower()
    if confirm == "yes":
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
                print("Database reset successfully.")
                manage_service("restart")  # Restart CasaOS to recreate the database
                print("CasaOS service restarted.")
            except Exception as e:
                print(f"Failed to reset the database: {e}")
        else:
            print("Database file not found.")
    else:
        print("Database reset canceled.")

# Main Menu
def main():
    # Check if CasaOS is installed
    if not check_casaos_installation():
        exit(1)

    # Backup the database before any operations
    backup_database()

    while True:
        print("\nCasaOS User Management")
        print("1. List all users")
        print("2. Edit password")
        print("3. Add user")
        print("4. Remove user")
        print("5. Reset database")
        print("6. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            list_users()
        elif choice == "2":
            manage_service("stop")
            edit_password()
            manage_service("start")
        elif choice == "3":
            manage_service("stop")
            add_user()
            manage_service("start")
        elif choice == "4":
            manage_service("stop")
            remove_user()
            manage_service("start")
        elif choice == "5":
            manage_service("stop")
            reset_database()
            manage_service("start")
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
