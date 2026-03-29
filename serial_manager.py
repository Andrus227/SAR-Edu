import time
import serial
import serial.tools.list_ports


class GerenciadorSerial:
    def __init__(self, baudrate=115200, timeout=1):
        self.conexao = None
        self.baudrate = baudrate
        self.timeout = timeout

    def listar_portas(self):
        portas = [porta.device for porta in serial.tools.list_ports.comports()]
        return portas if portas else ["Nenhuma porta"]

    def esta_conectado(self):
        return self.conexao is not None and self.conexao.is_open

    def conectar(self, porta):
        try:
            self.desconectar()
            self.conexao = serial.Serial(porta, self.baudrate, timeout=self.timeout)
            time.sleep(1.5)  # tempo para estabilização/reset do Arduino
            return True, f"Conectado em {porta}"
        except serial.SerialException as e:
            return False, f"Erro serial ao conectar: {e}"
        except Exception as e:
            return False, f"Erro inesperado ao conectar: {e}"

    def desconectar(self):
        if self.esta_conectado():
            self.conexao.close()

    def enviar(self, pacote_string):
        if not self.esta_conectado():
            return False

        try:
            self.conexao.write(pacote_string.encode("utf-8"))
            return True
        except serial.SerialTimeoutException:
            return False
        except serial.SerialException:
            return False
        except Exception:
            return False