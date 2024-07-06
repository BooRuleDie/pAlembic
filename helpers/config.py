import os

# environment variable names
HOSTNAME_NAME = "P_TEST_HOSTNAME"
USER_NAME = "P_TEST_USER"
PASSWORD_NAME = "P_TEST_PASSWORD"
DATABASE_NAME = "P_TEST_DATABASE"


# values that are extracted from specificed names above
DB_CONFIG = {
    "HOSTNAME": None,
    "USER": None,
    "PASSWORD": None,
    "DATABASE": None,
}


def set_credentials():
    # check if names are correct and all env vars have a value
    if not os.getenv(HOSTNAME_NAME):
        print("[x] Wrong HOSTNAME_NAME or Empty Value")
        exit()
    if not os.getenv(USER_NAME):
        print("[x] Wrong USER_NAME or Empty Value")
        exit()
    if not os.getenv(PASSWORD_NAME):
        print("[x] Wrong PASSWORD_NAME or Empty Value")
        exit()
    if not os.getenv(DATABASE_NAME):
        print("[x] Wrong DATABASE_NAME or Empty Value")
        exit()

    # assign env vars
    DB_CONFIG["HOSTNAME"] = os.getenv(HOSTNAME_NAME)
    DB_CONFIG["USER"] = os.getenv(USER_NAME)
    DB_CONFIG["PASSWORD"] = os.getenv(PASSWORD_NAME)
    DB_CONFIG["DATABASE"] = os.getenv(DATABASE_NAME)
