STATUSES = [
    "Discovered",
    "Needs Review",
    "Eligible",
    "Not Eligible",
    "Risky",
    "Selected",
    "In Progress",
    "Draft Complete",
    "Ready for Review",
    "Approved to Submit",
    "Submitted",
    "Won",
    "Lost",
    "Archived",
]

ALLOWED_TRANSITIONS = {
    "Discovered": {"Needs Review", "Archived"},
    "Needs Review": {"Eligible", "Not Eligible", "Risky", "Archived"},
    "Eligible": {"Selected", "Archived"},
    "Risky": {"Needs Review", "Selected", "Archived"},
    "Selected": {"In Progress", "Archived"},
    "In Progress": {"Draft Complete", "Ready for Review", "Archived"},
    "Draft Complete": {"Ready for Review", "In Progress", "Archived"},
    "Ready for Review": {"Approved to Submit", "In Progress", "Archived"},
    "Approved to Submit": {"Submitted", "Ready for Review", "Archived"},
    "Submitted": {"Won", "Lost", "Archived"},
    "Not Eligible": {"Needs Review", "Archived"},
    "Won": {"Archived"},
    "Lost": {"Archived"},
    "Archived": set(),
}


def validate_transition(current: str, target: str) -> bool:
    if current == target:
        return True
    return target in ALLOWED_TRANSITIONS.get(current, set())

