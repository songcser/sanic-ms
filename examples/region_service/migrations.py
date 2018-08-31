from sanicms.migrations import (
    MigrationModel,
    info,
    db_manager,
)
from models import Province, City

class ProvinceMigration(MigrationModel):
    _model = Province


class CityMigration(MigrationModel):
    _model = City


if __name__ == '__main__':
    pm = ProvinceMigration()
    cm = CityMigration()
    with db_manager.transaction():
        pm.auto_migrate()
        cm.auto_migrate()
    print("Success Migration")