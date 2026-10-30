import random
import math
import json
import sys
import message_protocol as mp
from base_node import BaseNode


class AccessPointNode(BaseNode):
    """
    Сервер точка-доступа к хранилищу
    """

    def __init__(self, port: int, setting_file_path: str):
        """
        Конструктор

        :param port: порт
        :param setting_file_path: путь к файлу конфигурации
        """

        super(AccessPointNode, self).__init__(port)

        settings_json_str = open(setting_file_path, 'r').read()
        self.settings = json.loads(settings_json_str)

    def process_request(self, req: mp.BaseMessage) -> mp.BaseMessage:

        if type(req) == mp.SetRequest:
            return self.process_set_request(req)

        elif type(req) == mp.GetRequest:
            return self.process_get_request(req)

        else:
            raise ValueError('Unsupported request type')

    def process_set_request(self, set_request: mp.SetRequest) -> mp.SetResponse:
        """
        Обработка сообщения на установку значения

        :param set_request: сообщение-запрос на установку значения
        :return: сообщение ответ на запрос
        """

        print('Access Point node - set request: %s' % mp.Serializer.to_json(set_request))

        return mp.SetResponse(False)

    def process_get_request(self, get_request: mp.GetRequest) -> mp.GetResponse:
        """
        Обработка сообщения на получение значения
        :param get_request: запрос на получение значения
        :return: ответ на запрос
        """

        print('Access Point node - get request: %s' % mp.Serializer.to_json(get_request))

        return mp.GetResponse('', '', False)

    def get_quorum(self) -> list:
        """
        Вспомогательная функция получения кворума серверов

        :return: список словарей вида {'host': '<host>', 'port': <port>}
        """

        sn_list = self.settings['storage_node_list']
        sn_list_copy = sn_list.copy()
        random.shuffle(sn_list_copy)

        quorum_number = int(math.ceil(len(sn_list_copy)/2))

        return sn_list_copy[0:quorum_number]


def main(argv):
    """
    Запуск сервера (узла)
    :param argv: массив параметров запуска: 1 - порт, 2 - путь к файлу конфигурации
    """
    aps = AccessPointNode(int(argv[1]), str(argv[2]))
    aps.run()


if __name__ == "__main__":
    main(sys.argv)
