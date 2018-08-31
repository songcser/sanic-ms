import logging
from playhouse.migrate import *

from sanicms.migrations import (
    MigrationModel,
    info,
    db_manager,
)
from models import User


class UserMigration(MigrationModel):
    _model = User

    #  @info(version="v1")
    #  def migrate_v1(self):
    #      migrate(self.add_column('hospital_id'))

def migrations():
    um = UserMigration()
    try:
        with db_manager.transaction():
            um.auto_migrate()
            print("Success Migration")
    except Exception as e:
        raise e

if __name__ == "__main__":
    migrations()
