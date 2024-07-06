from helpers.migrations import test, fetch, create, apply, upgrade, downgrade, status
from helpers.config import set_credentials
import sys
import os

PALEMBIC_DIR = os.path.dirname(os.path.abspath(__file__))
MIGRATIONS_DIR = os.path.join(PALEMBIC_DIR, "migrations")

help = """
* palembic.py test -> test db connection, migrations table and migrations directory
* palembic.py fetch -> updates the migrations directory
* palembic.py create -> creates migration template
* palembic.py apply "label" -> registers migration to the database
* palembic.py upgrade "label" -> upgrades database
* palembic.py downgrade "label" -> downgrades database
* palembic.py status -> shows current migration status
"""


def main():
    # Set database credentials
    set_credentials()

    if len(sys.argv) < 2:
        print("Usage: palembic <command> [label]")
        print(help)
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "fetch":
        fetch(MIGRATIONS_DIR)
    elif command == "test":
        test(MIGRATIONS_DIR)
    elif command == "status":
        status()
    elif command == "create":
        if len(sys.argv) < 3:
            print("Usage: palembic create <migration_label>")
            sys.exit(1)
        label = sys.argv[2]
        create(MIGRATIONS_DIR, label)
    elif command == "apply":
        if len(sys.argv) < 3:
            print("Usage: palembic apply <migration_label>")
            sys.exit(1)
        label = sys.argv[2]
        apply(MIGRATIONS_DIR, label)
    elif command == "upgrade":
        if len(sys.argv) < 3:
            print("Usage: palembic upgrade <migration_label>")
            sys.exit(1)
        label = sys.argv[2]
        upgrade(MIGRATIONS_DIR, label)
    elif command == "downgrade":
        if len(sys.argv) < 3:
            print("Usage: palembic downgrade <migration_label>")
            sys.exit(1)
        label = sys.argv[2]
        downgrade(MIGRATIONS_DIR, label)
    else:
        print(f"Unknown command: {command}")
        print("Available commands: fetch, test, create, apply, upgrade, downgrade")
        sys.exit(1)


if __name__ == "__main__":
    main()
