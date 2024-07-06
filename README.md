# Commands

```
* palembic.py test -> test db connection, migrations table and migrations directory
* palembic.py fetch -> updates the migrations directory
* palembic.py create -> creates migration template
* palembic.py apply "label" -> registers migration to the database
* palembic.py upgrade "label" -> upgrades database
* palembic.py downgrade "label" -> downgrades database
* palembic.py status -> shows current migration status
```