import tkinter as tk
import socket
import threading


server = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8080
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT 
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))

    # server is listening for client connection
    server.listen(5)  
    accept_clients(server)    
    # threading._start_new_thread(accept_clients, (server," "))

def accept_clients(the_server):
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        threading._start_new_thread(send_receive_client_message,(client,addr))

        
# Function to receive message from current client and
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    client_name  = client_connection.recv(4096)
    clients_names.append(client_name)

    # sending Welcome message to client
    client_connection.send(bytes("Welcome " + str(client_name, "utf-8") + ". Use 'exit' to quit", "utf-8"))

    while True:
        data = client_connection.recv(4096)

        if not data: 
            break
        if str(data,"utf-8") == "exit": 
            break

        client_msg = data

        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                c.send(bytes(str(sending_client_name,"utf-8") + "->" + str(client_msg,"utf-8"),"utf-8"))

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    client_connection.close()


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


def main():
    print("Server File Started")
    start_server()


if __name__ == "__main__":
    main()