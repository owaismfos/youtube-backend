class ExcludeFromDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return 'exclude_db'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in ['auth', 'contenttypes', 'sessions']:
            return 'exclude_db'
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in ['auth', 'contenttypes', 'sessions']:
            return db == 'exclude_db'
        return None