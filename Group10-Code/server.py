import tkinter as tk
import socket
import threading
from table import list_messages, authorise_user, add_message, update_password, list_users, list_messages
import sys

server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8080
client_name = " "
clients = []
clients_usernames = []

connections = dict()
users = dict()
online_users = dict()

for user in list_users():
    user_id = user['pid']
    users[user_id] = user

# glock = threading.Lock()

def start_server():
    global server, HOST_ADDR, HOST_PORT

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))

    # server is listening for client connection
    server.listen(5)

    accept_clients(server)


def accept_clients(the_server):
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        threading._start_new_thread(
            send_receive_client_message, (client, addr))


# Function to receive message from current client
def send_receive_client_message(client_connection, client_ip_addr):
    global server, clients
    client_msg = " "

    # Authentication method
    client_info = client_connection.recv(4096)
    client_name = str(client_info, "utf-8").split('\n')[1]
    client_password = str(client_info, "utf-8").split('\n')[2]

    print(client_name, client_password)
    try:
        user_info = authorise_user(client_name, client_password)
    except Exception as error:
        print(error)
        client_connection.send(bytes("LOGIN_FAIL\n\n", "utf-8"))
        client_connection.close()
        sys.exit()

    client_name = user_info["name"]
    user_id = user_info["pid"]
    user_is_admin = user_info["is_admin"]

    # clients_names.append(client_name)
    add_client_connection(user_id, user_info, client_connection)

    # Successful authentication
    client_connection.send(
        bytes(f"LOGIN_SUCCESS\n{client_name}\n\n", "utf-8"))
    online_users[user_id] = user_info["name"]
    
    send_online_users()

    # Send previous messages
    messages = list_messages()
    for message in messages:
        client_connection.send(bytes(
            f"{users.get(message['sid'], {'name': 'Anonymous'})['name']} -> {message['data']}\n\n", "utf-8"))

    while True:
        message = client_connection.recv(4096)

        if not message:
            break
        if str(message, "utf-8") == "exit":
            break

        message = str(message, "utf-8")
        fields = message.split("\n")

        if len(fields) > 1:  # Header is present
            header = fields[0]
            data = fields[1]
            message = handle_control_message(user_info, header, data)
            client_connection.send(bytes(message, "utf-8"))
            continue
        else:
            data = fields[0]

        client_msg = data
        add_message(user_id, data)
        # idx = get_client_index(clients, client_connection)
        sending_client_name = client_name

        for user_id, connection in connections.items():
            if connection != client_connection:
                connection.send(bytes(sending_client_name +
                                      "->" + client_msg + "\n\n", "utf-8"))

    # users.pop(user_id)
    if connections.get(user_id, None): connections.pop(user_id)
    if online_users.get(user_id, None): online_users.pop(user_id)
    client_connection.close()

    send_online_users()

def send_online_users():
    for connection in connections.values(): # Update other users about online users
        user_words = "\n".join(list(online_users.values()))
        try:
            connection.send(bytes(f'ONLINE_USERS\n{user_words}\n\n', "utf-8"))
        except: # To avoid multiple connection closes at the same time
            pass

def get_client_connection(user_id):
    return connections[user_id]


def add_client_connection(user_id, user_info, connection):
    connections[user_id] = connection
    if user_id not in users:
        users[user_id] = user_info


def handle_control_message(user_info, header, data):
    if header == "CHANGE_PASS":
        user_id = user_info["pid"]
        password = data
        try:
            update_password(user_id, password)
            return "CHANGE_PWD_SUCCESS\n\n"
        except Exception as error:
            print(error)
            return "CHANGE_PWD_FAIL\n\n"


def main():
    print("Server File Started")
    start_server()


if __name__ == "__main__":
    main()




