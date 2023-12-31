import socket
import sys
import select
import threading

import package
from package import *


def confirm_receive(date):
    global confirmed, first_conn, vol
    aux = date.decode("ascii")

    ack = aux.split("||")
    if ack[0] == "F":
        confirmed = False
        print("final transmisie fisier!")
        first_conn = True
        vol = 1
    if ack[0] == "T":
        confirmed = True


def first_connection():
    global connected, confirmed, connected_client, k
    k = 0
    connected_client = s.recvfrom(1024)
    connected = True
    confirmed = True


def receive_fct():
    global running, connected_client, connected, first_conn
    contor = 0
    while running:
        # Apelam la functia sistem IO -select- pentru a verifca daca socket-ul are date in bufferul de receptie
        # Stabilim un timeout de 1 secunda
        r, _, _ = select.select([s], [], [], 1)
        if not r:
            contor = contor + 1
        else:
            if first_conn:
                first_connection()
                first_conn = False
            else:
                connected_client = s.recvfrom(1024)
                confirm_receive(connected_client[0])
                if confirmed:
                    print("Mesajul catre clientul cu adresa: ", connected_client[0], " a fost transmis cu succes!")
                else:
                    print("Eroare la transmiterea mesajuli catre clientul cu adresa: ", connected_client[1])
                print("Contor= ", contor, "s")

            # s.sendto(bytes("", encoding="ascii"), connecting_server[1])

    # Citire nr port din linia de comanda


# Creare socket UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

s.bind(('127.0.0.1', int(20001)))

to_send = package.pack("fisier.txt", "f", "20001")

running = True
connected = False
confirmed = True
first_conn = True

try:
    receive_thread = threading.Thread(target=receive_fct)
    receive_thread.start()
except:
    print("Eroare la pornirea thread‐ului")
    sys.exit()

print("se asteapta conectarea clientului")

vol = 1
k = 0


# slow start
def send_package():
    global k, confirmed, vol, old_k
    old_k = k  # in caz de eroare (timeout), se va retine ultimul set de pachete care trebuia trimis.
    thresh = 16

    for i in range(0, vol):
        if (k < len(to_send)):
            data = Package.binaryToString(to_send[k])
            s.sendto(bytes(data, encoding="ascii"), connected_client[1])
            k = k + 1
    if vol < thresh:
        vol = vol * 2
    else:
        vol = vol + 1
    confirmed = False

print(len(to_send))
while True:
    while connected:
        try:
            while k < len(to_send) and confirmed:
                send_package()

        except KeyboardInterrupt:
            running = False
            print("Waiting for the thread to close...")
            receive_thread.join()
            sys.exit()
