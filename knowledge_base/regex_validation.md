# Input Validation Using Regular Expressions

Summary:
Validates structured strings using regex.
Common for emails, phone numbers, and IDs.
Ensures correct formatting patterns.

---

import re

def validate_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)