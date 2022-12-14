from pydantic import BaseModel, BaseSettings
from colorama import Fore, Back, Style
from os import mkdir
import psycopg
import sys

def getDatabaseCredentials():
    question = f"""\
    {Style.BRIGHT}Select an option to specify database credentails:{Style.RESET_ALL} 
    
    {Fore.GREEN}(1){Style.RESET_ALL} From User Input
    {Fore.GREEN}(2){Style.RESET_ALL} From .env File
    {Fore.GREEN}(3){Style.RESET_ALL} From Environment Variables
    
    {Style.BRIGHT}{Fore.GREEN}> {Style.RESET_ALL}"""

    try:
        selectedOption = int(input(question))
    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
        print(error)
        sys.exit()

    if selectedOption not in [1, 2, 3]:
        print(f"{Fore.BLUE}{Style.BRIGHT}[!]{Style.RESET_ALL} You can only select 1, 2 and 3.")
        sys.exit()

    if selectedOption == 1:
        
        class DBCREDS(BaseModel):
            dbname: str
            user: str
            password: str
            host: str
            port: int

        dbcredsdict = dict()
        
        try:
            dbcredsdict["dbname"] = input("Database Name: ")
            dbcredsdict["user"] = input("Username: ")
            dbcredsdict["password"] = input("Password: ")
            dbcredsdict["host"] = input("Hostname: ")
            dbcredsdict["port"] = int(input("Port: "))

            dbcreds = DBCREDS(**dbcredsdict)
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()
        else:
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")
            
            return dbcreds
            
    elif selectedOption == 2:

        print(f"""
{Style.BRIGHT}.env file's format must be as follows:{Style.RESET_ALL}

# you can change the values as you want
dbname=palembic_db
user=palembic
password=palembic
host=192.168.1.46
port=5432""")

        try: 
            class DBCREDS(BaseSettings):
                dbname: str
                user: str
                password: str
                host: str
                port: int

                class Config:
                    env_file = ".env"

            dbcreds = DBCREDS(_env_file=".env") 
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()
        else: 
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")

            return dbcreds
    
    elif selectedOption == 3:

        try:
            class DBCREDS(BaseSettings):
                dbname: str
                user: str
                password: str
                host: str
                port: int

            dbcreds = DBCREDS()
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()
        else: 
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")

            return dbcreds

def testDbConnection(creds):
    try:
        with psycopg.connect(**creds.dict()) as conn:            
            with conn.cursor() as cursor:
                print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Connected to the database successfully")
                
    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when trying to connect the database.\n")
        print(error)
        sys.exit()

def createPhasesDirectory():
    try:
        mkdir("Phases")
    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when trying to create the phases directory..\n")
        print(error)
        sys.exit()
    else:
        print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Phases directory created")

def main():
    usage = f"""
{Back.WHITE}{Fore.RED}{Style.BRIGHT}----- USAGE -----{Style.RESET_ALL}


{Style.BRIGHT}{Fore.YELLOW}=== START ==={Style.RESET_ALL}
{Style.BRIGHT}> python palembic.py start{Style.RESET_ALL}

- creates phases directory
- lets you enter database credentials to establish connection
- creates first phase module

{Style.BRIGHT}{Fore.CYAN}---{Style.RESET_ALL}

{Style.BRIGHT}{Fore.BLUE}=== RESTART ==={Style.RESET_ALL}
{Style.BRIGHT}> python palembic.py restart{Style.RESET_ALL}

- removes the config module and phases directory recursively

{Style.BRIGHT}{Fore.CYAN}---{Style.RESET_ALL}

{Style.BRIGHT}{Fore.GREEN}=== UPGRADE ==={Style.RESET_ALL}
{Style.BRIGHT}> python palembic.py upgrade{Style.RESET_ALL}
- upgrades current phase by 1

{Style.BRIGHT}> python palembic.py upgrade +<positive integer>{Style.RESET_ALL}
- upgrades current phase by the number specified

{Style.BRIGHT}> python palembic.py upgrade head{Style.RESET_ALL}
- upgrades current phase up to the last phase

{Style.BRIGHT}{Fore.CYAN}---{Style.RESET_ALL}

{Style.BRIGHT}{Fore.RED}=== DOWNGRADE ==={Style.RESET_ALL}
{Style.BRIGHT}> python palembic.py downgrade{Style.RESET_ALL}
- downgrades current phase by 1

{Style.BRIGHT}> python palembic.py downgrade -<positive integer>{Style.RESET_ALL}
- downgrades current phase by the number specified

{Style.BRIGHT}> python palembic.py downgrade base{Style.RESET_ALL}
- downgrades current phase to the first phase
"""
    # print USAGE if user enter sth wrong
    if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1].lower() not in ["start", "restart", "upgrade", "downgrade"]:
        print(usage)
        sys.exit()
    
    # operation that'll be done when user enter start
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "start":
        creds = getDatabaseCredentials()
        testDbConnection(creds)
        createPhasesDirectory()

if __name__ == "__main__":
    main()