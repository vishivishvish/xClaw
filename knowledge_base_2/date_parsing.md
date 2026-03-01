# Date Parsing and Timestamp Validation

Summary:
Parses ISO formatted timestamps.
Validates date strings and converts to datetime objects.
Handles timezone-aware conversions.

---

## Example

from datetime import datetime

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")