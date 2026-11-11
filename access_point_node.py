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

        quorum = self.get_quorum()
        read_responses = [
            mp.send_message(node['host'], node['port'], mp.ReadRequest(set_request.data_key))
            for node in quorum
        ]
        existing_ts = [response.ts for response in read_responses if response.is_key_exist]
        new_ts = max(existing_ts, default=0) + 1

        write_responses = [
            mp.send_message(
                node['host'], node['port'],
                mp.WriteRequest(self._uuid, new_ts, set_request.data_key, set_request.data_value)
            )
            for node in quorum
        ]
        return mp.SetResponse(all(response.is_ack for response in write_responses))

    def process_get_request(self, get_request: mp.GetRequest) -> mp.GetResponse:
        """
        Обработка сообщения на получение значения
        :param get_request: запрос на получение значения
        :return: ответ на запрос
        """

        print('Access Point node - get request: %s' % mp.Serializer.to_json(get_request))

        quorum = self.get_quorum()
        read_responses = [
            mp.send_message(node['host'], node['port'], mp.ReadRequest(get_request.data_key))
            for node in quorum
        ]
        existing = [response for response in read_responses if response.is_key_exist]
        if not existing:
            return mp.GetResponse(get_request.data_key, '', False)

        latest_ts = max(response.ts for response in existing)
        latest = min(
            (response for response in existing if response.ts == latest_ts),
            key=lambda response: response.writer_uuid
        )
        for node in quorum:
            mp.send_message(
                node['host'], node['port'],
                mp.WriteRequest(latest.writer_uuid, latest_ts, get_request.data_key, latest.data_value)
            )
        return mp.GetResponse(get_request.data_key, latest.data_value, True)

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
