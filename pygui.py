import os
import socket
import threading
import pyzipper
import time
from tkinter import *


#################################################################################################################################################

# PEER-TO-PEER FILE SHARING IN PYTHON [GUI]

#################################################################################################################################################

# SENDING END OF THE PEER

# Used to get the ip address and host name for creating a network to connect
def get_ip():  
    ip = socket.gethostname()
    print("Host name:" + ip)
    try:
        ip = ([l for l in (
            [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [
                [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in
                 [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])
        print("Local ip:" + ip)

        # Sends the IP address to the GUI
        txt0.delete(0, 'end')
        result=ip
        txt0.insert(END, str(result))
        
    except:
        # When no peer IP is found
        print("Not connected to any network")


def continue_connection():
        # Force shuts down the GUI
        print("Exiting server")
        exit()

# Ending connection
def end_connection(conn):
    
    # Force shuts down the sending peer
    print("Disconnected ")
    conn.close()
    continue_connection()

# Selecting file to send
def choose_file(conn):

    # Get the file name from the GUI
    filename = txt1.get()
    # Connection error 
    try:  
        conn.send(filename.encode())
        # The file doesn't exist
        try:  
            file_size = os.path.getsize(filename)
        except:
            print("Unable to find file try again")
            choose_file(conn)
        file_size = str(file_size)
        conn.send(file_size.encode())
        ans = conn.recv(1024)
        ans = str(ans.decode())
        time.sleep(5)
        if ans == 'N':
            print("Ending connection")
            end_connection(conn)
        if ans == 'Y':
            with open(filename, 'rb') as file:
                chunk_size = 1024
                chunk_file = file.read(chunk_size)
                while len(chunk_file) > 0:
                    conn.send(chunk_file)
                    chunk_file = file.read(chunk_size)
            file.close()
            print("Data has been transmitted successfully")
            txt2.delete(0, 'end')
            result="Data has been transmitted successfully"
            txt2.insert(END, str(result))
            end_connection(conn)
    except:
        continue_connection()

# Selecting file to send via encryption

def encchoose_file(conn):  
    # Connection error while communication encryption
    try:  
        filename = txt1.get()

        # AES based ZIP encryption using the pyzipper module
        # pyzipper is an improved fork of the zipfile module with password and AES encryption
        
        with pyzipper.AESZipFile('tobesent.zip','w',compression=pyzipper.ZIP_LZMA,encryption=pyzipper.WZ_AES) as zf:

            try:
                # Gets password from GUI

                secret_password = txt3.get()

                # It is needed that the password is converted to bytes for encryption
                secretpassword = secret_password.encode()

                zf.setpassword(secretpassword)
                f1=str(filename)
                print(f1)
                zf.write(f1)
                filename= 'tobesent.zip'
                conn.send(filename.encode())
                
            # No password found set to 'default'
            except:
                print("Password set to as default")
                txt2.delete(0, 'end')
                result="Password set to as default"
                txt2.insert(END, str(result))

                # Setting password to 'default'
                secret_password = 'default'
                
                secretpassword = secret_password.encode()
                zf.setpassword(secretpassword)
                f1=str(filename)
                print(f1)
                zf.write(f1)
                # Changing the file to be sent as the newly created ZIP file 'tobesent.zip'
                filename= 'tobesent.zip'

                # Sending the new filename to the receiving peer as bytes
                conn.send(filename.encode())

        try:  # File doesn't exist
            file_size = os.path.getsize(filename)
        except:
            print("Unable to find file try again")
            choose_file(conn)
        # Sending info of the file
        file_size = str(file_size)
        conn.send(file_size.encode())
        ans = conn.recv(1024)
        ans = str(ans.decode())
        
        # Listening to the other peers for the next step
        if ans == 'N':

            # Ending connection request from peer
            print("Ending connection")
            end_connection(conn)
        if ans == 'Y':
            
            # Proceed with file transfer request from peer
            with open(filename, 'rb') as file:
                chunk_size = 1024
                chunk_file = file.read(chunk_size)
                
                # Splits the file as bytes to send it over socket
                while len(chunk_file) > 0:
                    conn.send(chunk_file)
                    chunk_file = file.read(chunk_size)
                    
            # Closing the splitter file once transfer is complete        
            file.close()
            time.sleep(5)
            print("Data has been transmitted successfully")
            txt2.delete(0, 'end')
            result="Data has been transmitted successfully"
            txt2.insert(END, str(result))
            end_connection(conn)

    except:
        end_connection(conn)

def send_(conn):
    # Iniates the sending sequence
    conn.send("S".encode())
    choose_file(conn)

def encsend_(conn):
    # Initiates the encrypted file sending sequence
    conn.send("S".encode())
    encchoose_file(conn)

        
def send_or_receive(conn):  # Both peers can send and receive file

    # Button definition for SEND in GUI
    btn3 = Button(root, text = "SEND", command=(lambda: threading.Thread(target=send_(conn)).start()))
    btn3.place(x=100, y=200)
    
    # Button definiton of ENCRYPT + SEND in GUI
    btn4 = Button(root, text = "ENCRYPT + SEND", command=(lambda: threading.Thread(target=encsend_(conn)).start()))
    btn4.place(x=200, y=200)

    # Thread used to prevent GUI window from going to infinite loop

def socket_connection():  # Creating the socket connection
    try:
        
        # Initiate the socket definition for establishing connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 8080
        s.bind(('', port))

        # Time Window for the peer to connect
        s.listen(10)
        
        print("Waiting for a connection")
        txt2.delete(0, 'end')
        result="Waiting for a connection"
        txt2.insert(END, str(result))

        # Peer is connected
        conn, addr = s.accept()

        print(addr, "has connected to the system")
        # Sends status to GUI
        txt2.delete(0, 'end')
        result=(addr, "has connected to the system")
        txt2.insert(END, str(result))

        # Initiate the file sharing sequence
        send_or_receive(conn)
        
    except:
        print("Connection error")
        continue_connection()

# Getting ip and creating socket connection | Called by the CREATE button from GUI
def create_network():  
    get_ip()
    socket_connection()


# SENDING PART OF PEER IS OVER

#################################################################################################################################################
#################################################################################################################################################

# RECEIVING END OF THE PEER


# Writes the transfered bytes into the file
def write_file(s, file_name, file_size):

    # Pieces the bytes into the required file
    with open(file_name, 'wb') as file:
        chunk_size = 1024
        chunk_file = s.recv(chunk_size)
        file.write(chunk_file)
        total_received = len(chunk_file)
        while total_received < file_size:
            chunk_file = s.recv(chunk_size)
            file.write(chunk_file)
            total_received += len(chunk_file)
            
    # Temporary file closes after writing to disk
    file.close()
    
    print("File has been received.")
    # Sends status to GUI
    txt2.delete(0, 'end')
    result="File has been received successfully"
    txt2.insert(END, str(result))

# Starts connection to the host 
def open_connection():  
    try:
        # Opens socket connection to connect to HOST
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        txt2.delete(0, 'end')
        result="Enter address of Peer"
        txt2.insert(END, str(result))

        # Receives HOST address from GUI
        host = str(txt0.get())
        port = 8080
        s.connect((host, port))

        # Sends status to GUI
        print(" Connected to the host... ")
        txt2.delete(0, 'end')
        result="Connected to the host... "
        txt2.insert(END, str(result))
        return s
    
    except:
        # Unable to connect to HOST
        print("Port busy try again later")
        txt2.delete(0, 'end')
        result="Port busy try again later"
        txt2.insert(END, str(result))

# Function needs to be split up to facilitate threading
def receive_file1(s,file_name,file_size):
        s.send('Y'.encode())
        write_file(s, file_name, file_size)
        s.close()

# Receive file from other peer
def receive_file(s):  
    file_name = os.path.basename(s.recv(1024).decode())
    file_size = int(s.recv(1024).decode())
    print("Do you want to download % s of size % s" % (file_name, file_size))
    txt2.delete(0, 'end')
    result="Do you want to Receive?"
    txt2.insert(END, str(result))

    # Button definition for RECEIVE in GUI
    btn5 = Button(root, text = "RECEIVE", command=(lambda: threading.Thread(target=receive_file1(s,file_name,file_size)).start()))
    btn5.place(x=350, y=200)

    # Thread used to prevent GUI window from going to infinite loop    

# Getting know whether this peer should send or receive file
def send_or_recv(s):
    # Listends to the other peer's message
    ans = str(s.recv(1024).decode())
    if ans == "S":
        receive_file(s)
    elif ans == "R":
        choose_file(s)

# Join the network created by create_network() | Triggered by the button JOIN
def join_network():
    # Opens socket connection
    s = open_connection()
    # Initiates transfer sequence
    send_or_recv(s)

# RECEIVING END OF THE PEER IS OVER

#################################################################################################################################################
#################################################################################################################################################

# GUI END OF PEER

# Definition for GUI using tkinter module

# Creates window
root = Tk()
root.title("PEER-TO-PEER FILE SHARING")
root.geometry('600x400')

# Button definitions | Common for both sending and receiving peer

btn1 = Button(root, text = "CREATE", command=(lambda: threading.Thread(target=create_network).start()))
btn1.place(x=100, y=25)

btn2 = Button(root, text = "JOIN", command=(lambda: threading.Thread(target=join_network).start()))
btn2.place(x=250, y=25)

# Common label and text field definitions

# IP LABEL
lb0 = Label(root, text = "IP")
lb0.place(x=100, y=100)
txt0 = Entry(root, width=20)
txt0.place(x=200, y=100)

# FILE NAME LABEL
lb1 = Label(root, text = "FILE NAME")
lb1.place(x=100, y=150)
txt1 = Entry(root, width=50)
txt1.place(x=200, y=150)

# STATUS LABEL
lb2 = Label(root, text = "STATUS")
lb2.place(x=100, y=350)
txt2 = Entry(root, width=50)
txt2.place(x=200, y=350)

# PASSWORD LABEL
lb3 = Label(root, text = "Password")
lb3.place(x=100, y=250)
txt3 = Entry(root, width=20)
txt3.place(x=200, y=250)

# mainloop() to keep GUI running
root.mainloop()

# PEER-TO-PEER FILE SHARING IN PYTHON [GUI]

# END OF SOURCE CODE

#################################################################################################################################################
#################################################################################################################################################

