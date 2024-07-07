import mysql.connector
from .config import DB_CONFIG


def has_DDL(upgrade: str, downgrade: str) -> bool:
    DDLs = ["CREATE", "ALTER", "DROP", "TRUNCATE", "RENAME"]

    for DDL in DDLs:
        if DDL in upgrade.upper():
            return True

        if DDL in downgrade.upper():
            return True

    return False


def get_connection():
    try:
        con = mysql.connector.connect(
            host=DB_CONFIG["HOSTNAME"],
            user=DB_CONFIG["USER"],
            password=DB_CONFIG["PASSWORD"],
            database=DB_CONFIG["DATABASE"],
        )
    except Exception as error:
        print("[x] Connection Error")
        print(f"[x] Error: {error}")
        exit()

    return con


# test connection by fetching database version
def test_connection(verbose=True):
    con = get_connection()

    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT VERSION() AS version;")
        version = cursor.fetchone()
    except Exception as error:
        print("[x] Connection Error (test_connection)")
        print(f"[x] Error: {error}")
        exit()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    if verbose:
        print("[+] Connected Successfully")
        print(f"[+] Version: MySQL {version['version']}")


# check if migration table is created if not create it
def check_migrations_table():
    con = get_connection()
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS Palembic_Migrations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                label VARCHAR(50) UNIQUE NOT NULL, -- 50 is the max label length
                upgrade TEXT NOT NULL,
                downgrade TEXT NOT NULL,
                is_current BOOLEAN NOT NULL DEFAULT 0
            );"""
        )
        con.commit()
    except Exception as error:
        print("[x] Database Error (check_migrations_table)")
        print(f"[x] Error: {error}")
        exit()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def get_all_migrations():
    con = get_connection()
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, label, upgrade, downgrade, is_current FROM Palembic_Migrations ORDER BY id DESC;"""
        )
        migrations = cursor.fetchall()
    except Exception as error:
        print("[x] Database Error (get_all_migrations)")
        print(f"[x] Error: {error}")
        exit()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return migrations


def insert_new_migration(upgrade, downgrade, label):
    con = get_connection()
    try:
        cursor = con.cursor()

        # start transaction
        con.start_transaction()

        # execute upgrade SQL
        cursor.execute(upgrade)
        print("[+] Upgraded Successfully")

        # execute downgrade SQL
        cursor.execute(downgrade)
        print("[+] Downgraded Successfully")

        # Insert the new migration
        cursor.execute(
            """
            INSERT INTO Palembic_Migrations (label, upgrade, downgrade, is_current)
            VALUES (%s, %s, %s, %s)
            """,
            (label, upgrade, downgrade, 0),
        )
        print("[+] New Migration Registered")

        # Commit the transaction
        con.commit()
    except Exception as error:
        # Rollback transaction on error
        con.rollback()
        print("[x] Migration Error (insert_new_migration)")
        print(f"[x] Error: {error}")

        if has_DDL(upgrade, downgrade):
            print(
                "[x] Upgrade or Downgrade Has DDL Command, MySQL Doesn't Support DDL Rollback"
            )
            print("[x] Rollback Failed, Take Action Manually")
        else:
            print("[!] Rollbacked")

        return -1

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def apply_upgrade(label):
    con = get_connection()
    try:
        cursor = con.cursor(dictionary=True)

        # Start transaction
        con.start_transaction()

        # Get the id of the current migration
        cursor.execute("""SELECT id FROM Palembic_Migrations WHERE is_current = 1;""")
        current_migration = cursor.fetchone()
        if not current_migration:
            # apply the first migration and quit
            cursor.execute(
                """SELECT id, upgrade, downgrade, label FROM Palembic_Migrations ORDER BY id ASC LIMIT 1;"""
            )
            first_migration = cursor.fetchone()

            cursor.execute(first_migration["upgrade"])
            print(f"[+] Executed upgrade SQL: {first_migration['label']}")

            cursor.execute(
                "UPDATE Palembic_Migrations SET is_current = 1 WHERE id = %s;",
                (first_migration["id"],),
            )

            con.commit()
            print("[+] Database Upgraded Successfully")
            return

        current_id = current_migration["id"]

        # Get the id of the specified label
        cursor.execute(
            """SELECT id FROM Palembic_Migrations WHERE label = %s""",
            (label,),
        )
        target_migration = cursor.fetchone()
        if not target_migration:
            raise Exception(f"No migration found with label {label}.")

        target_id = target_migration["id"]

        # Check that the target id is greater than the current id
        if target_id <= current_id:
            raise Exception(
                "The specified label's id must be greater than the current migration's id."
            )

        # Get all upgrade SQLs between the current id and the target id
        cursor.execute(
            """SELECT upgrade, label FROM Palembic_Migrations
            WHERE id > %s AND id <= %s ORDER BY id ASC;""",
            (current_id, target_id),
        )

        upgrades = cursor.fetchall()

        # Execute all upgrade SQLs one by one
        for upgrade in upgrades:
            cursor.execute(upgrade["upgrade"])
            print(f"[+] Executed upgrade SQL: {upgrade['label']}")

        # Update the current migration
        cursor.execute(
            """UPDATE Palembic_Migrations SET is_current = 0 WHERE is_current = 1"""
        )
        cursor.execute(
            """UPDATE Palembic_Migrations SET is_current = 1 WHERE label = %s""",
            (label,),
        )

        # Commit the transaction
        con.commit()
        print("[+] Database Upgraded Successfully")

    except Exception as error:
        # Rollback transaction on error
        con.rollback()
        print("[x] Migration Error (apply_upgrade)")
        print(f"[x] Error: {error}")
        print("[x] Upgrade Has DDL Command, MySQL Doesn't Support DDL Rollback")
        print("[x] Rollback Fails If Upgrade Has DDL")

        return -1

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def apply_downgrade(label):
    con = get_connection()
    try:
        cursor = con.cursor(dictionary=True)

        # Start transaction
        con.start_transaction()

        # Get the id of the current migration
        cursor.execute("""SELECT id FROM Palembic_Migrations WHERE is_current = 1;""")
        current_migration = cursor.fetchone()
        if not current_migration:
            raise Exception("No current migration found.")

        current_id = current_migration["id"]

        # Get the id of the specified label
        cursor.execute(
            """SELECT id FROM Palembic_Migrations WHERE label = %s""",
            (label,),
        )
        target_migration = cursor.fetchone()
        if not target_migration:
            raise Exception(f"No migration found with label {label}.")

        target_id = target_migration["id"]

        # Check that the target id is smaller than the current id
        if target_id >= current_id:
            raise Exception(
                "The specified label's id must be smaller than the current migration's id."
            )

        # Get all downgrade SQLs between the current id and the target id
        cursor.execute(
            """SELECT downgrade, label FROM Palembic_Migrations
            WHERE id <= %s AND id > %s ORDER BY id DESC;""",
            (current_id, target_id),
        )

        downgrades = cursor.fetchall()

        # Execute all upgrade SQLs one by one
        for downgrade in downgrades:
            cursor.execute(downgrade["downgrade"])
            print(f"[+] Executed downgrade SQL: {downgrade['label']}")

        # Update the current migration
        cursor.execute(
            """UPDATE Palembic_Migrations SET is_current = 0 WHERE is_current = 1"""
        )
        cursor.execute(
            """UPDATE Palembic_Migrations SET is_current = 1 WHERE label = %s""",
            (label,),
        )

        # Commit the transaction
        con.commit()
        print("[+] Database Downgraded Successfully")

    except Exception as error:
        # Rollback transaction on error
        con.rollback()
        print("[x] Migration Error (apply_downgrade)")
        print(f"[x] Error: {error}")
        print("[x] Upgrade Has DDL Command, MySQL Doesn't Support DDL Rollback")
        print("[x] Rollback Fails If Upgrade Has DDL")

        return -1

    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()


def get_status():
    con = get_connection()
    try:
        cursor = con.cursor(dictionary=True)
        cursor.execute(
            """SELECT id, label, is_current FROM Palembic_Migrations ORDER BY id DESC;"""
        )
        status = cursor.fetchall()
    except Exception as error:
        print("[x] Database Error (get_status)")
        print(f"[x] Error: {error}")
        exit()
    finally:
        if cursor:
            cursor.close()
        if con:
            con.close()

    return status
