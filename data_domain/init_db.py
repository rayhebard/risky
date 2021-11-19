"""
Verify a connection and if table already exists.
If they do not, create them and populate them with data. 
    
Authors: Raymond Hebard <raymond.hebard@gtri.gatech.edu>"""


import os
from enum import Enum
from rethinkdb import RethinkDB

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")

table_names = [
   'client'
]

db_name="Risky"

def rethinkdb_wrap():
    return RethinkDB()


def create_table(db_name, name):
    with rethinkdb_wrap().connect(host=db_host, port=db_port) as conn:
        if name not in RethinkDB().db(db_name).table_list().run(conn):
            print('Creating table "' + name + '" in database "' + db_name + '".')
            RethinkDB().db(db_name).table_create(name).run(conn)

def create_tables(db_name, names):
    for name in names:
        create_table(db_name, name)


def create_database():
    with rethinkdb_wrap().connect(host=db_host, port=db_port) as conn:
            if  db_name in RethinkDB().db_list().run(conn):
                print("Creating Risky Database " + db_name)
                RethinkDB().db_create(db_name).run(conn)
                create_tables(db_name, table_names)
               
    return True

def init():
    create_database()

if __name__ == "__main__":
    create_database()

