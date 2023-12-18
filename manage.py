from init_db.database_init import db_init
from app.registration import init_tkinter

if __name__ == "__main__":
    db_init.init_functions()
    db_init.init_role()
    init_tkinter()
