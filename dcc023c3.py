#!/usr/bin/env python3

from socket import *
from struct import *
import struct  
import sys
import _thread as thread
import time

TamanhoMAX = 65535
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

    if(id > 0):
        idFinal = cvtHEX("01")
    else:
        idFinal = cvtHEX("00")


    lengthHEX = '{:04x}'.format(len(mensagem))
    lengthHEX = ' '.join(lengthHEX[i:i+2] for i in range(0, len(lengthHEX), 2))
    length = cvtHEX(lengthHEX)


    if(flag == flagACK):
        flagFinal = cvtHEX(flagACK)
    else:
        flagFinal = cvtHEX(flagEnvio)

    chksum = cvtHEX("00 00")    
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
    idDeEnvio = 1

    while True:
        dados = file.read(TamanhoMAX)
        if not dados: #EOF
            print("END OF FILE")
            #cria enquadramento
            #cria mensagem final
            #conn.send mensagem final
            #conn.recv( confirmacao)

            #if confirmacao = enquadramento
            #   return, tudo certo
            #if confirmacao != enquadramento
            #printa ^azedou^
            return

        else:
            enquadramento = enquadra(dados, idDeEnvio, flagEnvio)
            dadosHEX = "".join("{:02x}".format(c) for c in dados)
            dadosHEX = ' '.join(dadosHEX[i:i+2] for i in range(0, len(dadosHEX), 2))
            msgAux = enquadramento + cvtHEX(dadosHEX)
            print(msgAux)
            checksumHEX = "%04x" % checksum(msgAux)
            checksumHEX = ' '.join(checksumHEX[i:i+2] for i in range(0, len(checksumHEX), 2))
            checksumHEX = cvtHEX(checksumHEX)
            print(checksumHEX)
            print(msgAux)
            msgFinal = str(encode16(msgAux))
            print(msgFinal)


            print("Transmitindo")
            #conn.send(msgFinal) nao funcionaria?
            conn.send(struct.pack("!i", len(msgFinal)))
            conn.send(struct.pack("!" + str(len(msgFinal)) + "s", msgFinal.encode("ascii")))

            #confirmacao = conn.recv(qualTamanho?)
            
            #-----------------------------manda o ACK

            # enquadramentoACK = enquadra('', idDeEnvio, flagACK)

            # if (confirmacao == enquadramentoACK):
            #     if(idDeEnvio == 1):
            #         idDeEnvio = 0
            #     else:
            #         idDeEnvio = 1
            # if (confirmacao != enquadramentoACK):
            #     print("ACK recebido esta errado")
            #     return


        return


def RecebeDados(output, conn):

    #primeira coisa de tudo, cria um id =1 pra ter controle de envio/recibo
    idrecebido = 1
    #abre o arquivo como WB, vamos escrever no arquivo
    file = open(output, 'wb')

    while True:
        #recebe
        print("Recebendo")
        recebe_num = int(struct.unpack("!i", connection.recv(4))[0])
        string_byte = struct.unpack("!" + str(recebe_num) + "s", connection.recv(recebe_num))[0]
        string_byte = string_byte.decode("ascii")

        #confere o checksum.
        confereChecksum = string_byte[20:24]
        print(confereChecksum)
        #pega os dados em uma variavel
        dados = string_byte[28:]
        print(dados)

        #cria dois cabecalhos: um com id de envio 1, outro com 0
        enquadramento1 = enquadra(dados, 1, flagEnvio)
        enquadramento1 = encode16(enquadramento1) + dados
        enquadramento0 = enquadra(dados, 0, flagEnvio)
        enquadramento0 = encode16(enquadramento0) + dados


        if (enquadramento1[20:24] == confereChecksum and idrecebido == 1):
            print("oi")
            #manda o enquadramento com ACK e ID = 1
            criaACK = enquadra('',1, flagACK)
            print(criaACK)
            # conn.send(criaACK)
            #file.write(dados) (escreve no arquivo de saida)
            #identificador = 0

        if (enquadramento0[20:24] == confereChecksum and idrecebido == 0):
            print("oi2")
            #manda o enquadramento com ACK e ID = 0
            #file.write(dados)
            #identificador = 1

        else:
            print("nao bateu nenhum checksum")
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
    #Thread1 = thread...transmite dados()
    #Thread2 = thread...recebe dados()
    #thread start()
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
        RecebeDados(output_file, connection) 
