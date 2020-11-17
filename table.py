import sqlite3
from datetime import timezone 
import datetime 

connection = sqlite3.connect("data.db", check_same_thread=False)

print("Opened database")


def execute_statement(statement):
    cursor = None
    try:
        cursor = connection.execute(statement)
    except sqlite3.OperationalError as error:
        print("update: ", error)
    return cursor


execute_statement(
    """
CREATE TABLE users (
    pid             INTEGER PRIMARY KEY NOT NULL,
    name            TEXT NOT NULL,
    enr_no          INT, 
    password        CHAR(50) NOT NULL,
    is_admin        BIT
);"""
)

execute_statement(
    """
CREATE TABLE messages (
    mid             INTEGER PRIMARY KEY NOT NULL,
    sender          INT NOT NULL,
    data            CHAR(256),
    FOREIGN KEY     (sender) REFERENCES users(pid) ON DELETE CASCADE
);"""
)


def authorise_user(name, password, enr_no=None):
    """
    Login the user using the enrollment number or the username
    """
    cursor = execute_statement(f"""
        SELECT * FROM users
        WHERE name='{name}' AND password='{password}'
    """)

    if cursor.rowcount == 0:
        raise Exception("No such user")

    for row in cursor:
        pid, name, enr_no, is_admin = row[0], row[1], row[2], row[3]
        break

    return {"pid": pid, "name": name, "enr_no": enr_no, "is_admin": bool(is_admin)}
  

def add_user(*args, **kwargs):
    name = kwargs.get("name", None)
    enr_no = kwargs.get("enr_no", -1)
    password = kwargs.get("password", None)
    is_admin = kwargs.get("is_admin", False)

    if name is None or password is None:
        raise Exception("Please give proper name and password")

    if not enr_no and not is_admin:
        raise Exception("Users without enrolmment number must be admins")

    execute_statement(
        f"""
    INSERT INTO users
    VALUES (NULL, '{name}', '{enr_no}', '{password}', {is_admin})
    """
    )
    connection.commit()


def remove_user(*args, **kwargs):
    """
    Remove user based on the enrolment number
    """
    enr_no = kwargs.get("enr_no", None)
    if enr_no is None:
        raise Exception("No enrollment number was passed")

    execute_statement(
        f"""
        DELETE FROM users
        WHERE enr_no={enr_no};
    """
    )
    connection.commit()
    print("User deleted successfully")


def update_password(pid, password):
    """
    Update the password for a user
    """

    if pid is None:
        raise Exception("No user id was passed")
    elif password is None:
        raise Exception("Empty passwords aren't allowed")

    cursor = execute_statement(
        f"""
        UPDATE users
        SET password='{password}'
        WHERE pid={pid}
        """
    )
    connection.commit()


def list_users():
    """
    List all the users
    """
    cursor = execute_statement(
        """
        SELECT * FROM users
        """
    )
    users = []
    for row in cursor:
        pid, name, enr_no, is_admin = row[0], row[1], row[2], row[3]
        users.append(
            {"pid": pid, "name": name, "enr_no": enr_no,
                "is_admin": bool(is_admin)}
        )
    return users


def list_messages():  # Can add time range based message lists afterwards
    """
    List all the messages
    """
    cursor = execute_statement(
        """
        SELECT * FROM messages
        ORDER BY mid
        """
    )
    messages = []
    for row in cursor:
        mid, sid, data = row[0], row[1], row[2]
        messages.append({"mid": mid, "sid": sid, "data": data})
    return messages

def add_message(user_id, message):
    """
    Add a new message to the database
    """

    execute_statement(
        f"""
        INSERT INTO messages 
        VALUES (NULL, '{user_id}', '{message}')
        """
    )
    connection.commit()
