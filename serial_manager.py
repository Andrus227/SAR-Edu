import serial
import serial.tools.list_ports
import time

class GerenciadorSerial:
    def __init__(self, baudrate=115200):
        self.conexao = None
        self.baudrate = baudrate

    def listar_portas(self):
        portas = [porta.device for porta in serial.tools.list_ports.comports()]
        return portas if portas else ["Nenhuma porta"]

    def conectar(self, porta):
        try:
            self.desconectar()
            self.conexao = serial.Serial(porta, self.baudrate, timeout=1)
            time.sleep(1.5) 
            return True, f"Conectado em {porta}"
        except Exception as e:
            return False, str(e)

    def desconectar(self):
        if self.conexao and self.conexao.is_open:
            self.conexao.close()

    def enviar(self, pacote_string):
        if self.conexao and self.conexao.is_open:
            try:
                self.conexao.write(pacote_string.encode('utf-8'))
                return True
            except:
                return False
        return False