import json
import os
from datetime import datetime, timedelta

LICENSE_FILE = "licenses.json"

class LicenseManager:
    def __init__(self):
        self.licenses = {}
        self.load()

    def load(self):
        if os.path.exists(LICENSE_FILE):
            with open(LICENSE_FILE, "r") as f:
                self.licenses = json.load(f)
        else:
            self.licenses = {}

    def save(self):
        with open(LICENSE_FILE, "w") as f:
            json.dump(self.licenses, f, indent=2)

    def add_time(self, user_id, days):
        user_id = str(user_id)
        if user_id == str(os.getenv("OWNER_ID")):
            return "The owner always has a license."
        now = datetime.utcnow()
        user_license = self.licenses.get(user_id)
        if user_license and user_license.get("lifetime"):
            return "User already has lifetime access."
        if user_license and user_license.get("expires_at"):
            expires = datetime.fromisoformat(user_license["expires_at"])
            if expires < now:
                expires = now
            expires += timedelta(days=days)
        else:
            expires = now + timedelta(days=days)
        self.licenses[user_id] = {"expires_at": expires.isoformat(), "lifetime": False}
        self.save()
        return f"Added {days} days. New expiry: {expires} UTC."

    def remove_time(self, user_id, days):
        user_id = str(user_id)
        if user_id == str(os.getenv("OWNER_ID")):
            return "You cannot modify the owner's license."
        user_license = self.licenses.get(user_id)
        if not user_license or user_license.get("lifetime"):
            return "User does not have a timed license."
        expires = datetime.fromisoformat(user_license["expires_at"])
        expires -= timedelta(days=days)
        if expires < datetime.utcnow():
            del self.licenses[user_id]
            self.save()
            return "License expired and removed."
        self.licenses[user_id]["expires_at"] = expires.isoformat()
        self.save()
        return f"Removed {days} days. New expiry: {expires} UTC."

    def grant_lifetime(self, user_id):
        user_id = str(user_id)
        if user_id == str(os.getenv("OWNER_ID")):
            return "The owner always has a license."
        self.licenses[user_id] = {"lifetime": True}
        self.save()
        return "Lifetime access granted."

    def revoke(self, user_id):
        user_id = str(user_id)
        if user_id == str(os.getenv("OWNER_ID")):
            return "You cannot revoke the owner's license."
        if user_id in self.licenses:
            del self.licenses[user_id]
            self.save()
            return "License revoked."
        return "No license to revoke."

    def has_access(self, user_id):
        user_id = str(user_id)
        if user_id == str(os.getenv("OWNER_ID")):
            return True
        user_license = self.licenses.get(user_id)
        if not user_license:
            return False
        if user_license.get("lifetime"):
            return True
        expires_at = user_license.get("expires_at")
        if expires_at and datetime.fromisoformat(expires_at) > datetime.utcnow():
            return True
        return False

    def get_expiry(self, user_id):
        user_id = str(user_id)
        user_license = self.licenses.get(user_id)
        if not user_license:
            return "No license."
        if user_license.get("lifetime"):
            return "Lifetime access."
        expires_at = user_license.get("expires_at")
        return f"Expires at: {expires_at} UTC" if expires_at else "No expiry."

manager = LicenseManager()
