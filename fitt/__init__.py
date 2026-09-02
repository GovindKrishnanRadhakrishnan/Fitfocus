import pymysql

pymysql.install_as_MySQLdb()

# Bypass Django database version check for older MariaDB (XAMPP runs 10.4)
from django.db.backends.base.base import BaseDatabaseWrapper
BaseDatabaseWrapper.check_database_version_supported = lambda self: None

# Bypass MariaDB RETURNING clause (XAMPP runs MariaDB 10.4 which doesn't support RETURNING)
from django.db.backends.mysql.features import DatabaseFeatures
DatabaseFeatures.can_return_columns_from_insert = False
DatabaseFeatures.can_return_rows_from_bulk_insert = False


