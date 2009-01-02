from django.core.management.base import NoArgsCommand
import os
import string

def module_to_dict(module, omittable=lambda k: k.startswith('_')):
    "Converts a module namespace to a Python dictionary. Used by get_settings_diff."
    return dict([(k, repr(v)) for k, v in module.__dict__.items() if not omittable(k)])

class Command(NoArgsCommand):
    help = "Delete all databases! Be careful about using this!"
    
    def handle_noargs(self, **options):
        """Delete the old database."""
        from django.conf import settings
        # Because settings are imported lazily, we need to explicitly load them.
        settings._import_settings()
        engine = settings.DATABASE_ENGINE
        db_host = settings.DATABASE_HOST 
        db_port = settings.DATABASE_PORT 
        db_pass = settings.DATABASE_PASSWORD 
        db_name = settings.DATABASE_NAME 
        db_user = settings.DATABASE_USER 
        
        response_erase_all = string.lower(raw_input("Type 'yes' to erase ALL of the data in your %s db named %s: " % (engine,db_name)))
        if response_erase_all != 'yes':
            print "Aborting..."
            return None
        if engine == 'sqlite3':
            try:
                os.unlink(db_name)
            except OSError:
                pass
        elif engine == 'mysql':
            import _mysql
            s = _mysql.connect(host=db_host,
                               user=db_user,
                               passwd=db_pass)
            for cmd in ['drop database if exists %s',
                        'create database %s CHARACTER SET utf8 COLLATE utf8_general_ci']:
                s.query(cmd % db_name)

        elif engine in ("postgresql_psycopg2", "postgresql"):
            if db_name == '':
                raise AssertionError("You must specify a value for DATABASE_NAME in local_settings.py.")
            if db_user == '':
                raise AssertionError("You must specify a value for DATABASE_USER in local_settings.py.")
            params=" --username=%s  --password" % db_user
            if db_host:
                params += " --host=%s" % db_host
            if db_port:
                params += " --port=%s" % db_port
            params += " %s" % db_name
            print("""You will be prompted for the password for the user '%s' twice.
            Once to drop the existing database and then a second time to create
            the database.""" % db_user)
            for cmd in ['dropdb %s', 'createdb %s']:
                os.system(cmd % params)
        else:
            raise AssertionError("Unknown database engine %s" % engine)
