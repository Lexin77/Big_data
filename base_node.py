import uuid
import socket
import sys
import time
import signal
import message_protocol as mp


class BaseNode:
    """
    Базовый класс узлов key-value хранилища
    """

    @staticmethod
    def signal_handler(sig, frame):
        """
        Обработчик сигнала Ctrl+C
        :param sig: код сигнала
        :param frame: объект данных исполнения
        """

        print('Ctrl+C received in server.py')
        time.sleep(1)
        sys.exit(0)

    def __init__(self, port: int):
        """
        Создание объекта сервера (узла)
        :param port: порт, который сервер слушает
        """

        self._port = port
        self._uuid = str(uuid.uuid4())
        signal.signal(signal.SIGINT, BaseNode.signal_handler)

    def run(self):
        """
        Запуск сервера
        """

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self._port))
        server_socket.listen(10)
        print('Start node on port %s' % str(self._port))

        while True:
            client_socket, address = server_socket.accept()

            message_str = mp.socket_receive_message(client_socket)
            message = mp.Serializer.from_json(message_str)

            response_str = self.process_request(message)

            mp.socket_send_message(client_socket, mp.Serializer.to_json(response_str))

            client_socket.close()

    def process_request(self, req: mp.BaseMessage) -> mp.BaseMessage:
        raise NotImplemented('Not implemented process_request of BaseNode')
