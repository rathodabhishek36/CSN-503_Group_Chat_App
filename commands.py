import sys
from table import add_user, list_users, list_messages, remove_user

args = sys.argv

if len(sys.argv) == 1:
    print("Enter some command")
    exit(1)

command_name = args[1]

if command_name == "createsuperuser":
    username = input("username: ")
    password = input("password: ")
    enr_no = input("enrollment number: ")
    try:
        add_user(name=username, password=password, enr_no=enr_no, is_admin=True)
    except Exception as error:
        print(error)

elif command_name == "userlist":
    print(list_users())

elif command_name == "messagelist":
    print(list_messages())

elif command_name == "deleteuser":
    enr_no = input("Enter enrolment number: ")
    remove_user(enr_no=enr_no)

elif command_name == "registerstudent":
    username = input("username: ")
    password = input("password: ")
    enr_no = input("enrollment number: ")

    try:
        add_user(name=username, password=password, enr_no=enr_no, is_admin=False)
    except Exception as error:
        print(error)