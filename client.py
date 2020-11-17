import tkinter as tk
from tkinter import messagebox
import socket
import threading

window = tk.Tk()
window.title("Client")
username = " "
password = " "
new_pass = " "

topFrame = tk.Frame(window)
loginName = tk.Label(topFrame, text = "UserName:").pack(side=tk.LEFT)
entNameLogin = tk.Entry(topFrame)
entNameLogin.pack(side=tk.LEFT)
passwordName = tk.Label(topFrame, text = "Password:").pack(side=tk.LEFT)
entNamePass = tk.Entry(topFrame)
entNamePass.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Login", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
btnChangePass = tk.Button(displayFrame, text="Change Password", command=lambda : changePassword())
btnChangePass.pack(side=tk.TOP)
btnChangePass.config(state=tk.DISABLED)
chgPass = tk.Entry(displayFrame)
chgPass.pack(side=tk.TOP)
chgPass.config(state=tk.DISABLED)
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)


def connect():
    global username, password, client
    if len(entNameLogin.get())<1 or len(entNamePass.get())<1:
        tk.messagebox.showerror(title="ERROR!!!", message="Enter Your email/Password correctly")
    else:
        username = entNameLogin.get()
        password = entNamePass.get()
        connect_to_server(username, password)


# network client
client = None
HOST_ADDR = "127.0.0.1"
HOST_PORT = 8080

def connect_to_server(name, pas):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(bytes("LOGINPASS\n"+name+"\n"+pas,"utf-8")) # Send name to server after connecting

        entNameLogin.config(state=tk.DISABLED)
        entNamePass.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # start a thread to keep receiving message from server
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def changePassword():
    try:
        if len(chgPass.get())<1:
            tk.messagebox.showerror(title="ERROR!!!", message="Enter a longer new Password")
        else :
            new_pass = chgPass.get()
            send_mssage_to_server("CHANGE_PASS\n"+new_pass)
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="NOT ABLE TO CHANGE THE PASSWORD. RETRY !!!")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096)

        if not from_server: break

        elif str(from_server,"utf-8").split('\n')[0]=="LOGIN_SUCCESS":
            btnChangePass.config(state=tk.NORMAL)
            chgPass.config(state=tk.NORMAL)

        elif str(from_server,"utf-8").split('\n')[0]=="PWD_CHANGE_SUCCESS":
            password = new_pass

        # display message from server on the chat window


        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ str(from_server,"utf-8"))

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)

        # print("Server says: " +from_server)

    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg)

    if(msg!="exit"):
        tkDisplay.see(tk.END)
        tkMessage.delete('1.0', tk.END)


def send_mssage_to_server(msg):
    client.send(bytes(msg,"utf-8"))
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")


window.mainloop()
