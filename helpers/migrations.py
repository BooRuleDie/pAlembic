from .database import test_connection, check_migrations_table, apply_upgrade, apply_downgrade, get_status
from .utils import (
    check_migration_dir,
    remove_migrations,
    create_migrations,
    create_new_migration,
    apply_new_migration,
)


def test(migrations_dir):
    test_connection()
    check_migration_dir(migrations_dir)
    check_migrations_table()


def fetch(migrations_dir, overwrite=False, verbose=True):
    # make sure everything is alright
    test_connection(verbose=verbose)
    check_migrations_table()

    # get the latest migrations
    remove_migrations(migrations_dir, overwrite=overwrite)
    create_migrations(migrations_dir)

    print("[+] Fetching Done")


def create(migrations_dir, label: str):
    # create an empty migration
    create_new_migration(migrations_dir, label)
    print("[+] New Migration Ready")
    print("[!] Waiting for Upgrade and Downgrade SQLs")


def apply(migrations_dir, label: str):
    apply_new_migration(migrations_dir, label)
    # don't fetch on apply. If you'd like to fetch, you can do it after the apply manually


def upgrade(migrations_dir, label: str):
    error = apply_upgrade(label)
    if not error:
        print("[!] Fetching...")
        fetch(migrations_dir, overwrite=True, verbose=False)


def downgrade(migrations_dir, label: str):
    error = apply_downgrade(label)
    if not error:
        print("[!] Fetching...")
        fetch(migrations_dir, overwrite=True, verbose=False)

def status():
    status = get_status()
    if status:
        print("|  id  |  is_current  |  label  |")
        print("+------+--------------+---------+")
        for s in status:
            print(f"|  {s['id']}  |  {s['is_current']}  |  {s['label']}  ")
    else:
        print("[!] No Migration Found")
        
