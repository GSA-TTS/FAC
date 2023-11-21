app_name = "census_historical_migration"
db_name = "census-to-gsafac-db"


class DBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == app_name:
            return db_name
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == app_name:
            return db == db_name
        return db == "default"
