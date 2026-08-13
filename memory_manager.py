import json
import os
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PERMANENT_MEMORY_FILE = os.path.join(
    BASE_DIR,
    "permanent_memory.json"
)

SUMMARY_MEMORY_FILE = os.path.join(
    BASE_DIR,
    "chat_summary_memory.json"
)


# =========================================================
# PERMANENT MEMORY
# =========================================================

def load_permanent_memory():

    if not os.path.exists(PERMANENT_MEMORY_FILE):
        return {
            "files": {},
            "applications": {},
            "contacts": {},
            "personal_facts": {}
        }

    try:
        with open(
            PERMANENT_MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            memory = json.load(f)

            memory.setdefault("files", {})
            memory.setdefault("applications", {})
            memory.setdefault("contacts", {})
            memory.setdefault("personal_facts", {})

        return memory

    except (json.JSONDecodeError, OSError):

        return {
            "files": {},
            "applications": {},
            "contacts": {},
            "personal_facts": {}
        }


def save_permanent_memory(memory):

    with open(
        PERMANENT_MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            memory,
            f,
            indent=4
        )


# =========================================================
# FILES
# =========================================================

def remember_file(name, path):

    memory = load_permanent_memory()

    memory["files"][name.lower().strip()] = path

    save_permanent_memory(memory)


def get_file(name):

    memory = load_permanent_memory()

    return memory["files"].get(
        name.lower().strip()
    )


# =========================================================
# APPLICATIONS
# =========================================================

def remember_application(name, path):

    memory = load_permanent_memory()

    memory["applications"][name.lower().strip()] = path

    save_permanent_memory(memory)


def get_application(name):

    memory = load_permanent_memory()

    return memory["applications"].get(
        name.lower().strip()
    )


# =========================================================
# CONTACTS
# =========================================================

def remember_contact(name, phone):

    memory = load_permanent_memory()

    memory["contacts"][name.lower().strip()] = phone

    save_permanent_memory(memory)


def get_contact(name):

    memory = load_permanent_memory()

    return memory["contacts"].get(
        name.lower().strip()
    )


# =========================================================
# PERSONAL FACTS
# =========================================================

def remember_personal_fact(key, value):

    memory = load_permanent_memory()

    memory["personal_facts"][
        key.lower().strip()
    ] = value.strip()

    save_permanent_memory(memory)


def get_personal_fact(key):

    memory = load_permanent_memory()

    return memory["personal_facts"].get(
        key.lower().strip()
    )


def get_personal_facts():

    memory = load_permanent_memory()

    return memory.get(
        "personal_facts",
        {}
    )

# =========================================================
# CHAT SUMMARY MEMORY
# =========================================================

def load_summaries():

    if not os.path.exists(SUMMARY_MEMORY_FILE):
        return {
            "summaries": []
        }

    try:

        with open(
            SUMMARY_MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except (json.JSONDecodeError, OSError):

        return {
            "summaries": []
        }


def save_chat_summary(summary):

    data = load_summaries()

    data["summaries"].append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": summary
    })

    with open(
        SUMMARY_MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            indent=4
        )


def get_last_summary():

    data = load_summaries()

    if not data["summaries"]:
        return None

    return data["summaries"][-1]["summary"]