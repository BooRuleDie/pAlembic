from .database import get_all_migrations, insert_new_migration
import shutil
import os
import re

def check_migration_dir(migrations_dir):
    # check if migrations directory exists, create if not
    if not os.path.exists(migrations_dir):
        print("[!] No Migrations Directory, Creating...")
        os.makedirs(migrations_dir, exist_ok=True)

def remove_migrations(migrations_dir, overwrite):
    if not overwrite:
        answer = input("[!] fetch overwrites the migrations directory, are you sure you want to continue: (y/n)")
        if answer.lower() != "y":
            print("[!] Aborting...")
            exit()
    
    # remove migrations directory if existed
    if os.path.exists(migrations_dir):
        shutil.rmtree(migrations_dir)


def create_migrations(migrations_dir):
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)

    migrations = get_all_migrations()
    if not migrations:
        print("[!] No Migrations Directory, Creating...")
        os.makedirs(migrations_dir, exist_ok=True)
        exit()

    for m in migrations:
        m_dir_name = f"{m['id']}-{m['label']}"
        m_dir_path = os.path.join(migrations_dir, m_dir_name)

        # create migration directory
        os.makedirs(m_dir_path, exist_ok=True)

        # create upgrade and downgrade sql files
        upgrade_file_path = os.path.join(m_dir_path, "upgrade.sql")
        downgrade_file_path = os.path.join(m_dir_path, "downgrade.sql")
        
        # Create and write to the files
        with open(upgrade_file_path, "w") as upgrade_file:
            upgrade_file.write(m["upgrade"] or "")
        
        with open(downgrade_file_path, "w") as downgrade_file:
            downgrade_file.write(m["downgrade"] or "")

def create_new_migration(migrations_dir, label):
    if len(label) > 50:
        print("[x] Label Can't Be Bigger Than 50 Chars")
        exit()

    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir, exist_ok=True)

    migrations = get_all_migrations()
    if not migrations:
        new_migration_name = f"{1}-{label}"
    else:
        last_migration_id = migrations[0]["id"]
        new_migration_name = f"{last_migration_id + 1}-{label}"

    # create the new_migration dir and sql files
    m_dir_path = os.path.join(migrations_dir, new_migration_name)
    os.makedirs(m_dir_path, exist_ok=True)
        
    upgrade_file_path = os.path.join(m_dir_path, "upgrade.sql")
    downgrade_file_path = os.path.join(m_dir_path, "downgrade.sql")

    with open(upgrade_file_path, "w") as upgrade_file:
            upgrade_file.write("")
        
    with open(downgrade_file_path, "w") as downgrade_file:
        downgrade_file.write("")

def apply_new_migration(migrations_dir, label):

    dir_found = False
    for dir_name in os.listdir(migrations_dir):
        dir_path = os.path.join(migrations_dir, dir_name)
        dir_label = dir_name[dir_name.find("-")+1:]
        
        if dir_label == label and os.path.isdir(dir_path):    
            # get upgrade, downgrade content
            upgrade_file_path = os.path.join(dir_path, 'upgrade.sql')
            downgrade_file_path = os.path.join(dir_path, 'downgrade.sql')

            # get the contents of upgrade.sql
            if os.path.exists(upgrade_file_path) and os.path.exists(downgrade_file_path):
                with open(upgrade_file_path, 'r') as upgrade_file:
                    upgrade_content = upgrade_file.read()

                with open(downgrade_file_path, 'r') as downgrade_file:
                    downgrade_content = downgrade_file.read()

                dir_found = True
                break
    
    if dir_found:
        insert_new_migration(upgrade_content, downgrade_content, label)
    else:
        print("[x] Wrong or Non-Existed Label Specified")
        exit()
        
