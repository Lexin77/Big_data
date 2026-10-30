import sys
from base_node import BaseNode
import message_protocol as mp


class StorageNode (BaseNode):
    """
    Сервер хранения данных
    """

    def __init__(self, port: int):
        """
        Конструктор сервера

        :param port: порт, который будет слушать сервер
        """

        super(StorageNode, self).__init__(port)
        self.data_dict = {}

    def process_request(self, request: mp.BaseMessage) -> mp.BaseMessage:
        """
        Функция обработки запросов к ноде

        :param request: объект запроса
        :return: объект ответа на запрос
        """

        if type(request) == mp.WriteRequest:
            return self.process_write_request(request)

        elif type(request) == mp.ReadRequest:
            return self.process_read_request(request)

        else:
            raise ValueError('Unsupported request type')

    def process_write_request(self, wr: mp.WriteRequest) -> mp.WriteResponse:
        """
        Функция обработки запроса на запись

        :param wr: запрос на запись
        :return: ответ на запрос на запись
        """

        print('Storage node - write request: %s' % mp.Serializer.to_json(wr))

        return mp.WriteResponse(True)

    def process_read_request(self, rr: mp.ReadRequest) -> mp.ReadResponse:
        """
        Функция обработки запроса на чтение

        :param rr: запрос на чтение
        :return: ответ на запрос на чтение
        """

        print('Storage node - read request: %s' % mp.Serializer.to_json(rr))

        return mp.ReadResponse(False, '', 0, rr.data_key, "")


def main(argv):
    """
    Запуск сервера

    :param argv: массив параметров: 1 - порт сервера
    """
    ss = StorageNode(int(argv[1]))
    ss.run()


if __name__ == "__main__":
    main(sys.argv)
