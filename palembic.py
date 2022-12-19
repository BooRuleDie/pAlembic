from pydantic import BaseModel, BaseSettings
from colorama import Fore, Back, Style
from os import mkdir, remove
from shutil import rmtree
import json
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
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()      
            
        return dbcreds
            
    elif selectedOption == 2:

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
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()

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
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Got all credentials.")
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.\n")
            print(error)
            sys.exit()
        
        return dbcreds

def createConfJSON(creds):
    confFile = creds.dict()
    confFile["phase"] = 0
    confFile["totalPhase"] = 0
    
    with open("conf.json", "w") as fp:
        json.dump(confFile, fp)
        
    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} conf.json file has been created.")

def testDbConnection(creds):
    try:
        with psycopg.connect(str(creds)) as conn:            
            with conn.cursor():
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

def addPhase():
    with open("./conf.json", "r") as file:
        phaseNumber = int(json.load(file)["totalPhase"]) + 1

    phase = {
        "upgrade" : "raw SQL here",
        "downgrade" : "raw SQL here",
        "label" : "name the phase"
    }

    try:
        with open(f"./Phases/{phaseNumber}.json", "w") as fp:
            json.dump(phase, fp)
            changePhaseStatus("+total")
            print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} phase {phaseNumber} has been added.")
    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when creating phase file.\n")
        print(error)
        sys.exit()
    
def removePhase():
    try:
        with open("./conf.json", "r") as file:
            confJSON = json.load(file)
            phaseNumber = confJSON["totalPhase"]
            currentPhase = confJSON["phase"]
        
        if currentPhase == phaseNumber:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} You can't remove the phase you're on.\n")
            print(error)
            sys.exit()
    
        remove(f'./Phases/{phaseNumber}.json')  
        changePhaseStatus("-total")

        print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} phase {phaseNumber} has been removed.")

    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when removing the phase file.\n")
        print(error)
        sys.exit()

def changePhaseStatus(change):
    with open("./conf.json", "r") as file:
        conf = json.load(file)
    
    if change == "+phase":
        conf["phase"] += 1
    elif change == "-phase":
        conf["phase"] -= 1
    elif change == "+total":
        conf["totalPhase"] += 1
    elif change == "-total":
        conf["totalPhase"] -= 1

    with open("./conf.json", "w") as file:        
        json.dump(conf, file)

def upgradePhase():
    confJSON = json.load(open("./conf.json"))
    currentState = confJSON["phase"]
    totalPhase = confJSON["totalPhase"]
    stateToUpgrade = None
    
    del confJSON["phase"]
    del confJSON["totalPhase"]
    
    class DBCREDS(BaseModel):
        dbname: str
        user: str
        password: str
        host: str
        port: int
    
    creds = DBCREDS(**confJSON)

    if sys.argv[2].lower() == "head":
        stateToUpgrade = totalPhase
    else:
        try:
            stateToUpgrade = int(sys.argv[2][1::]) + currentState

            if stateToUpgrade > totalPhase:
                print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} There is no such a phase.\n")
                print(error)
                sys.exit()

        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.")
            print(error)
            sys.exit()

    for phase in range(currentState + 1, stateToUpgrade + 1):
        phasefile = json.load(open(f"./Phases/{phase}.json"))
        upgradeSQL = phasefile["upgrade"]
        label = phasefile["label"]
        
        try:
            with psycopg.connect(str(creds)) as conn:            
                with conn.cursor() as cursor:
                    cursor.execute(upgradeSQL)
                    changePhaseStatus("+phase")
                    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Upgraded {Style.BRIGHT}{label}{Style.RESET_ALL}.")
                
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when trying to connect the database.\n")
            print(error)
            sys.exit()

def downgradePhase():
    confJSON = json.load(open("./conf.json"))
    currentState = confJSON["phase"]
    stateToDowngrade = None
    
    del confJSON["phase"]
    del confJSON["totalPhase"]

    class DBCREDS(BaseModel):
            dbname: str
            user: str
            password: str
            host: str
            port: int
    
    creds = DBCREDS(**confJSON)

    if sys.argv[2].lower() == "base":
        stateToDowngrade = 0
    else:
        try:
            stateToDowngrade = currentState - int(sys.argv[2][1::])

        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured.")
            print(error)
            sys.exit()

    for phase in range(currentState, stateToDowngrade, -1):
        phasefile = json.load(open(f"./Phases/{phase}.json"))
        downgradeSQL = phasefile["downgrade"]
        label = phasefile["label"]

        try:
            with psycopg.connect(str(creds)) as conn:            
                with conn.cursor() as cursor:
                    cursor.execute(downgradeSQL)
                    changePhaseStatus("-phase")
                    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Downgraded {Style.BRIGHT}{label}{Style.RESET_ALL}.")
                
        except Exception as error:
            print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when trying to connect the database.\n")
            print(error)
            sys.exit()

def restart():
    try:
        rmtree("./Phases")
        print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Removed Phases directory.")
        remove("./conf.json")
        print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.RESET_ALL} Removed conf.json.")
    except Exception as error:
        print(f"{Fore.RED}{Style.BRIGHT}[-]{Style.RESET_ALL} An error occured when restarting.\n")
        print(error)
        sys.exit()
    
def printUsage():
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

{Style.BRIGHT}{Fore.MAGENTA}=== PHASES ==={Style.RESET_ALL}
{Style.BRIGHT}> python palembic.py add phase{Style.RESET_ALL}
- adds a new phase into the phases directory

{Style.BRIGHT}> python palembic.py remove phase{Style.RESET_ALL}
- removes the last phase

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
    print(usage)

def main():
    # print USAGE if user enter sth wrong
    if len(sys.argv) < 2 or len(sys.argv) > 3 or sys.argv[1].lower() not in ["start", "restart", "upgrade", "downgrade", "add", "remove"]:
        printUsage()
        sys.exit()
    
    # operation that'll be done when user enter start
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "start":
        creds = getDatabaseCredentials()
        testDbConnection(creds)
        createConfJSON(creds)
        createPhasesDirectory() # order is important 
        addPhase() # added first phase
    
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "restart":
        restart()
    
    elif len(sys.argv) == 3 and sys.argv[1].lower() == "upgrade":
        upgradePhase()
    
    elif len(sys.argv) == 3 and sys.argv[1].lower() == "downgrade":
        downgradePhase()

    elif len(sys.argv) == 3 and sys.argv[1].lower() == "add" and sys.argv[2].lower() == "phase":
        addPhase()

    elif len(sys.argv) == 3 and sys.argv[1].lower() == "remove" and sys.argv[2].lower() == "phase":
        removePhase()

if __name__ == "__main__":
    main()