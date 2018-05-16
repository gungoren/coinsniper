import mysql.connector

class Database:

    def __init__(self, host, user, pswd, db):
        self.connection = mysql.connector.connect(host=host, user=user, password=pswd, database=db)
        self.cursor = self.connection.cursor()

    def insert(self, query):
        try:
            self.cursor.execute(query)
            self.connection.commit()
        except:
            self.connection.rollback()

    def insert(self, query, params):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except:
            self.connection.rollback()

    def query(self, query):
        self.cursor.execute(query)
        return self.cursor

    def close(self):
        self.cursor.close()
        self.connection.close()


if __name__ == "__main__":

    db = Database()

    # Data Insert into the table
    query = """
        select version()
        """

    people = db.query(query)

    for person in people:
        print("Found %s " % person)