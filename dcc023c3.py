#!/usr/bin/env python3

from socket import *
from struct import *
import struct  
import sys
import _thread as thread
import time

#ler arquivo
def read_file(input_file):
    with open(input_file, 'rb') as f:
        read_data = f.read()
        # read_teste = str(read_data)
        # print(read_data)
        # read_teste = read_teste.replace(' ', '')
        # print(len(read_teste))
        enquadra(read_data)
        #colocar enquadramento

    f.close()

def checksum(enquadrado):
    for i in enquadrado:
        print(i)
        # sum += int(enquadrado[i])
    # print(sum)

    
#coloca no quadro
def enquadra(read_data):
    sincronizacao = "11011100 11000000 00100011 11000010"
    read_data = "00000001 00000010 00000011 00000100"
    length = len(read_data)
    length_bin = format(length, '016b')
    checksum = format(0, '016b')
    id = format(0, '08b')
    flag = format(0, '08b')
    enquadrado = sincronizacao +" "+ sincronizacao +" "+ length_bin +" "+ checksum +" "+ id +" "+ flag +" "+ read_data
    #checksum
    for i in range(len(enquadrado)):
        print(int(enquadrado[i]))
        sum += int(enquadrado[i])
    # print(sum)
    # # checksum(enquadrado)
    encode16(enquadrado)

#codificar
def encode16(enquadrado):
    codificado = "".join("{:02X}".format(int(n,2)) for n in enquadrado.split(' ') if n)
    decode16(codificado)

#decodificae
def decode16(codificado):
    decodificado = "".join("{:02X}".format(int(n,16)) for n in codificado.split(' ') if n)
    print(decodificado)


    
identificador = sys.argv[1]
print(identificador)
if (identificador == "-c") :
    #client
    ip_port = sys.argv[2]
    ip, port = ip_port.split(":")
    port = int(port)
    input_file = sys.argv[3]
    output_file = sys.argv[4]

    #fazer o encode
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((ip, port))
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    envia_num = "blabla"
    conn.send(struct.pack("!i", len(envia_num)))
    conn.send(struct.pack("!" + str(len(envia_num)) + "s", envia_num.encode("ascii")))
    print(envia_num)
    print("\n")
    read_file(input_file)

    #recebe_num = int(struct.unpack("!i", conn.recv(4))[0])
    # print(string_back)
    
elif (identificador == "-s") :
    #server
    ip_address = ''
    port = int(sys.argv[2])
    input_file = sys.argv[3]
    output_file = sys.argv[4]
    conn = socket(AF_INET, SOCK_STREAM)
    conn.bind((ip_address, port))
    conn.listen(5)
    while True:
        connection, address = conn.accept()
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack('ll', 15, 0))
        recebe_num = int(struct.unpack("!i", connection.recv(4))[0])
        string_byte = struct.unpack("!" + str(recebe_num) + "s", connection.recv(recebe_num))[0]

        #FAZER O DECODE
        print(string_byte.decode("ascii"))

    
