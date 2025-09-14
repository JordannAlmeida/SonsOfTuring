from asyncpg import Connection

class ManagerAgentsService:

    def __init__(self, db_connection: Connection):
        self.db_connection = db_connection