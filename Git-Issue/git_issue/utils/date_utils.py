from datetime import datetime

"""Any date-related functionality for git-issue is found here to ensure
       all modules are using the same date functionality."""

def get_date_now():
    return datetime.utcnow().isoformat()
