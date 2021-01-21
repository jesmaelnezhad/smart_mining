from data_bank.database import Database

DB = None


def get_database():
    global DB
    """
    :return: the database object
    """
    if DB is None:
        DB = Database()
    return DB
