#!/usr/bin/env python3

from socket import *
from struct import *
import struct  
import sys
import threading as thread
import time

TamanhoMAX = 65535
flagEnvio = "00"
flagACK = "80"

def carry_around_add(a, b):
    c = a + b
    return(c &0xffff)+(c >>16)

def checksum(msg):
    s = 0
    for i in range(0, len(msg)-1,2):
        w =((msg[i])<<8)+((msg[i+1]))
        s = carry_around_add(s, w)
    if(len(msg) %2 != 0):
        s = s+ msg[len(msg) -1]
        s = carry_around_add(s,0)
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

    if(id > 0):
        idFinal = cvtHEX("01")
    else:
        idFinal = cvtHEX("00")


    lengthHEX = '{:04x}'.format(len(mensagem))
    lengthHEX = ' '.join(lengthHEX[i:i+2] for i in range(0, len(lengthHEX), 2))
    length = cvtHEX(lengthHEX)

    chksum = cvtHEX("00 00")

    if(flag == flagACK):
        flagFinal = cvtHEX(flagACK)
    else:
        flagFinal = cvtHEX(flagEnvio)

    # print(sincFinal, length, chksum, idFinal, flagFinal)
    enquadramento = sincFinal + sincFinal + length + chksum + idFinal + flagFinal

    return enquadramento     

#codificar
def encode16(enquadrado):
    codificado = "".join('%02x' %x  for x in enquadrado)
    return codificado

#decodificae
def decode16(codificado):
    codificado = ' '.join(codificado[i:i+2] for i in range(0, len(codificado), 2))
    decodificado = cvtHEX(codificado)
    return decodificado



def TransmiteDados(input_file, conn):
    #Abre o arquivo
    file = open(input_file, 'rb')
    idDeEnvio = 0

    while True:
        dados = file.read(TamanhoMAX)
        if not dados: #EOF

            msgFinal = "EOF"
            conn.send(struct.pack("!i", len(msgFinal)))
            conn.send(struct.pack("!" + str(len(msgFinal)) + "s", msgFinal.encode("ascii")))
            conn.settimeout(1)
            return

        else:
            enquadramento = enquadra(dados, idDeEnvio, flagEnvio)
            dadosHEX = "".join("{:02x}".format(c) for c in dados)
            dadosHEX = ' '.join(dadosHEX[i:i+2] for i in range(0, len(dadosHEX), 2))
            msgAux = enquadramento + cvtHEX(dadosHEX)

            print(msgAux)
            #---------------Cria CHECKSUM-------------------
            checksumHEX = "%04x" % checksum(msgAux)
            checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
            checksumHEX = cvtHEX(checksumHEX)
            msgAux = encode16(msgAux)
            msgAux = msgAux[:20] + encode16(checksumHEX) + msgAux[24:]
            msgAux = decode16(msgAux)
            msgFinal = str(encode16(msgAux))



            print("Transmitindo")
            #conn.send(msgFinal) nao funcionaria?
            conn.send(struct.pack("!i", len(msgFinal)))
            conn.send(struct.pack("!" + str(len(msgFinal)) + "s", msgFinal.encode("ascii")))

            print("Recebendo Confirmacao")
            conn.settimeout(1)
            confirmacao = conn.recv(4096*32)
            
            #-----------------------------manda o ACK

            enquadramentoACK = enquadra('', idDeEnvio, flagACK)


            checksumHEX = "%04x" % checksum(enquadramentoACK)
            checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
            checksumHEX = cvtHEX(checksumHEX)
            enquadramentoACK = encode16(enquadramentoACK)
            enquadramentoACK = enquadramentoACK[:20] + encode16(checksumHEX) + enquadramentoACK[24:]
            enquadramentoACK = decode16(enquadramentoACK)

            if (confirmacao != enquadramentoACK):
                print("[ERRO] Transmissao de dados")
                return
            if (confirmacao == enquadramentoACK):
                if(idDeEnvio == 1):
                    idDeEnvio = 0
                else:
                    idDeEnvio = 1


def RecebeDados(output, conn):
    #primeira coisa de tudo, cria um id =1 pra ter controle de envio/recibo
    idrecebido = 0
    #abre o arquivo como WB, vamos escrever no arquivo
    file = open(output, 'wb')

    while True:
        #recebe
        recebe_num = int(struct.unpack("!i", conn.recv(4))[0])
        string_byte = struct.unpack("!" + str(recebe_num) + "s", conn.recv(recebe_num))[0]
        string_byte = string_byte.decode("ascii")

        if(string_byte == "EOF"):
            print("Conexao com o arquivo terminada, esperando outra conexao...")
            return
        #confere o checksum.
        confereChecksum = string_byte[:28]
        #pega os dados em uma variavel
        dados = string_byte[28:]

        #cria dois cabecalhos: um com id de envio 1, outro com 0
        enquadramento1 = enquadra(decode16(dados), 1, flagEnvio)
        enquadramento1 = encode16(enquadramento1) + dados
        enquadramento1 = decode16(enquadramento1)
        #---------------Cria CHECKSUM-------------------
        checksumHEX = "%04x" % checksum(enquadramento1)
        checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
        checksumHEX = cvtHEX(checksumHEX)
        enquadramento1 = encode16(enquadramento1)
        enquadramento1 = enquadramento1[:20] + encode16(checksumHEX) + enquadramento1[24:]
        enquadramento1 = decode16(enquadramento1)


        enquadramento0 = enquadra(decode16(dados), 0, flagEnvio)
        enquadramento0 = encode16(enquadramento0) + dados
        enquadramento0 = decode16(enquadramento0)
        #---------------Cria CHECKSUM-------------------
        checksumHEX = "%04x" % checksum(enquadramento0)
        checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
        checksumHEX = cvtHEX(checksumHEX)
        enquadramento0 = encode16(enquadramento0)
        enquadramento0 = enquadramento0[:20] + encode16(checksumHEX) + enquadramento0[24:]
        enquadramento0 = decode16(enquadramento0)

        enquadramento0 = encode16(enquadramento0)
        enquadramento1 = encode16(enquadramento1)

        if (enquadramento1[:28] == confereChecksum and idrecebido == 1):
            #manda o enquadramento com ACK e ID = 1
            criaACK = enquadra('',1, flagACK)
            print(criaACK)

            #---------------Cria CHECKSUM-------------------
            checksumHEX = "%04x" % checksum(criaACK)
            checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
            checksumHEX = cvtHEX(checksumHEX)
            criaACK = encode16(criaACK)
            criaACK = criaACK[:20] + encode16(checksumHEX) + criaACK[24:]
            criaACK = decode16(criaACK)


            conn.send(criaACK)
            file.write(decode16(dados))
            idrecebido = 0
            print("Enviando confirmacao com id = 1")
        elif (enquadramento0[:28] == confereChecksum and idrecebido == 0):
            #manda o enquadramento com ACK e ID = 0
            criaACK = enquadra('', 0, flagACK)
            print(criaACK)

            #---------------Cria CHECKSUM-------------------
            checksumHEX = "%04x" % checksum(criaACK)
            checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
            checksumHEX = cvtHEX(checksumHEX)
            criaACK = encode16(criaACK)
            criaACK = criaACK[:20] + encode16(checksumHEX) + criaACK[24:]
            criaACK = decode16(criaACK)


            conn.send(criaACK)
            file.write(decode16(dados))
            idrecebido = 1
            print("Enviando confirmacao com id = 0")

        else:
            return
    return

    
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
    # Thread1 = thread(target=TransmiteDados(input_file, conn))
    # Thread2 = thread(target=RecebeDados(output_file, conn))
    #----------Starta a thread---------------
    # Thread1.start()
    # Thread2.start()
    TransmiteDados(input_file, conn)
    #-------------Fecha a conexao----------------------
    # conn.close()


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
    # conn.listen(1)
    # connection, address = conn.accept()
    # connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    # connection.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack('ll', 15, 0))

    # RecebeDados(output_file, connection)
    #-------------Criar thread para Transmitir/Receber dados------------------
    while True:
        conn.listen(1)
        connection, address = conn.accept()
        connection.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        connection.setsockopt(SOL_SOCKET, SO_RCVTIMEO, struct.pack('ll', 15, 0))

        RecebeDados(output_file, connection)
        #---------------thread start()----------------------
        # Thread1 = thread(target=RecebeDados(output_file, connection))
        # Thread2 = thread(target=TransmiteDados(input_file, connection))
        # Thread1.start()
        # Thread2.start()
        # RecebeDados(output_file, connection)
        # threads.start()