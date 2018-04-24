#!/usr/bin/env python3

from socket import *
from struct import *
import struct  
import sys
import _thread as thread
import time


flagEnvio = "7f"
flagACK = "80"

def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg),2):
        w =(msg[i])+((msg[i+1])<<8)
        s = carry_around_add(s, w)
    return ~s &0xffff

#Converte em HEXA

def cvtHEX(msg):
    msg = msg.split()
    msg = list(map(lambda x: int(x,16), msg))
    msg = struct.pack("%dB" %len(msg), *msg)
    return msg

    
#coloca no quadro
def enquadra(mensagem, id, flag):
    sincronizacao = "dc c0 23 c2"

    sincFinal = cvtHEX(sincronizacao)
    print(sincFinal)

    if(id > 0):
        idFinal = cvtHEX("01")
    else:
        idFinal = cvtHEX("00")

    length = cvtHEX(str(len(mensagem)))

    if(flag == flagACK):
        flagFinal = cvtHEX(flagACK)
    else:
        flagFinal = cvtHEX(flagEnvio)

    chksum = cvtHEX("00 00")    


    # print(sincFinal, length, chksum, idFinal, flagFinal)
    enquadramento = sincFinal + sincFinal + length + chksum + idFinal + flagFinal
    print(enquadramento)
    return enquadramento     

    # read_data = '0100100001100101011011000110110001101111001011000010000001110111011011110111001001101100011001000010000100001010'
    # read_data1 = 'hello, wolrd!'
    # length = len(read_data)
    # length_bin = format(length, '016b')
    # checksum = format(0, '016b')
    # id = format(0, '08b')
    # flag = format(0, '08b')
    # # enquadrado = sincronizacao +" "+ sincronizacao +" "+ length_bin +" "+ checksum +" "+ id +" "+ flag +" "+ read_data
    # enquadrado = sincronizacao + sincronizacao + length_bin + checksum + id + flag + read_data
    # #checksum
    # data = "45 00 00 47 73 88 40 00 40 06 a2 c4 83 9f 0e 85 83 9f 0e a1"
    # data = data.split()
    # tam = len(data)
    # data = map(lambda x: int(x,16), data)
    # print(data)
    # data = struct.pack("%dB" % tam, *data)

    # print (' '.join('%02X' % ord(x) for x in data))
    # print ("Checksum: 0x%04x" % checksum(data))

#codificar
def encode16(enquadrado):
    codificado = "".join("{:02X}".format(int(n,2)) for n in enquadrado.split(' ') if n)
    decode16(codificado)

#decodificae
def decode16(codificado):
    decodificado = "".join("{:02X}".format(int(n,16)) for n in codificado.split(' ') if n)
    print(decodificado)



def TransmiteDados(input, conn):
    #Abre o arquivo
    file = open(input, 'rb')
    idDeEnvio = 1

    while True:
        dados = file.read()
        enquadramento = enquadra(dados, idDeEnvio, flagEnvio)
        print(enquadramento)
        return



    print("Transmitindo")


def RecebeDados(output, conn):
    print("Recebendo")

    
identificador = sys.argv[1]
if (identificador == "-c") :
    #Cliente
    #--------------Le as entradas-----------------
    ip_port = sys.argv[2]
    ip, port = ip_port.split(":")
    port = int(port)
    input_file = sys.argv[3]
    output_file = sys.argv[4]
    #-------------Cria o socket------------------
    conn = socket(AF_INET, SOCK_STREAM)
    conn.connect((ip, port))
    conn.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    #-------------Criar thread para Transmitir/Receber dados------------------
    #Thread1 = thread...transmite dados()
    #Thread2 = thread...recebe dados()
    #thread start()
    envia_num = "blabla"
    conn.send(struct.pack("!i", len(envia_num)))
    conn.send(struct.pack("!" + str(len(envia_num)) + "s", envia_num.encode("ascii")))
    TransmiteDados(input_file, conn)

    #-------------Fecha a conexao----------------------
    #conn.close()


elif (identificador == "-s") :
    #Servidor
    #--------------Le as entradas-----------------
    ip_address = ''
    port = int(sys.argv[2])
    input_file = sys.argv[3]
    output_file = sys.argv[4]

    #-------------Cria o socket------------------
    conn = socket(AF_INET, SOCK_STREAM)
    conn.bind((ip_address, port))
    conn.listen(5)

    #-------------Criar thread para Transmitir/Receber dados------------------
    #Thread1 = thread...recebe dados()
    #Thread2 = thread...transmite dados()
    while True:
        #---------------thread start()----------------------
        connection, address = conn.accept()
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack('ll', 15, 0))
        recebe_num = int(struct.unpack("!i", connection.recv(4))[0])
        string_byte = struct.unpack("!" + str(recebe_num) + "s", connection.recv(recebe_num))[0]

        print(string_byte.decode("ascii"))

    
