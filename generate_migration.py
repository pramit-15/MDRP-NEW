import alembic.config
import alembic.command
import sys

try:
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic.command.revision(alembic_cfg, message="Initial migration", autogenerate=False)
    print("Success")
except Exception as e:
    import traceback
    with open("alembic_error.txt", "w") as f:
        traceback.print_exc(file=f)
    print("Error")
