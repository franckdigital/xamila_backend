# Use PyMySQL as MySQL client (alternative to mysqlclient)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass