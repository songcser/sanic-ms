from sanicms.migrations import (
    MigrationModel,
    info,
    db_manager,
)
from models import Role

class RoleMigration(MigrationModel):
    _model = Role


if __name__ == '__main__':
    rm = RoleMigration()
    with db_manager.transaction():
        rm.auto_migrate()
    print("Success Migration")