# What is pAlembic ?

pAlembic stands for pseudo alembic, it's the only raw SQL supported version of alembic. Also it doesn't create a table in the database you're working with.

*(It only supports postgreSQL currently)*

# Dependencies

All dependencies are stated in the requirements.txt file. Only thing you need to do is to execute following command:

```bash
pip install -r requirements.txt
```

# How it works ?

The very first thing that you need to do when working with palembic is to enter following command:

```
python palembic.py start
```

It'll create **conf.json** and **Phases** directory. They're essentials for pAlembic.

- **conf.py**: Configuration file that stores environment variables and status of pAlembic.
- **Phases**: Directory that holds **phase** files, they are the files that pAlembic uses to upgrade and downgrade database.

After starting the pAlembic you can go under the **Phases** and write your own upgrade and downgrade SQLs into the **``<number>``**.json file like that:

*1.json*
```json
{
  "upgrade": "create table users (user_id serial primary key, username varchar(50))",
  "downgrade": "drop table users"
}
```

Now you can upgrade the database:

```bash
python palembic.py upgrade +1
# or
python palembic.py head # upgrades up to last phase
```

And if you want to downgrade the database you can also do it:

```bash
python palembic.py downgrade -1
# or
python palembic.py base # downgrades to the very beginning
```

After you're done with first phase file you can add as much phase file as you want:

```
python palembic.py add phase
```

# !!! IMPORTANT !!!

pAlembic gives you three option to enter database credentials:

```bash
Select an option to specify database credentails: 
    
    (1) From User Input
    (2) From .env File
    (3) From Environment Variables
    
    > 
```

If you're going to choose **2** or **3**, name your environment variables as it's shown below:

```.env
# names are important for pAlembic
dbname=palembic_db
user=palembic
password=palembic
host=localhost
port=5433
```

---

Database credentials are stored plaintext in the conf.json, so if you're using pAlembic in the production environment, give proper permission to the **conf.json** and **palembic.py**.