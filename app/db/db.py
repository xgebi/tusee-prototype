import psycopg


class Connector:
    def __init__(self, conn_string: str or None = None):
        if conn_string:
            self.con = psycopg.connect(conn_string)

    def init_db(self, conn_string: str):
        self.__init__(conn_string=conn_string)

    def init_flask(self, app):
        self.__init__(conn_string=app.config["DATABASE_STRING"])