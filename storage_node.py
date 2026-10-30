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

        # Словарь данных: ключ -> (ts, writer_uuid, значение)
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

        Запись применяется, если она новее уже сохранённой: сравниваем ts,
        при равных ts - идентификаторы записавших серверов (меньший uuid
        выигрывает). Устаревшая запись игнорируется, но подтверждается.

        :param wr: запрос на запись
        :return: ответ на запрос на запись
        """

        print('Storage node - write request: %s' % mp.Serializer.to_json(wr))

        if wr.data_key not in self.data_dict:
            self.data_dict[wr.data_key] = (wr.ts, wr.writer_uuid, wr.data_value)

        else:
            current_ts, current_writer_uuid, current_value = self.data_dict[wr.data_key]

            if wr.ts > current_ts:
                self.data_dict[wr.data_key] = (wr.ts, wr.writer_uuid, wr.data_value)

            elif wr.ts == current_ts and wr.writer_uuid < current_writer_uuid:
                self.data_dict[wr.data_key] = (wr.ts, wr.writer_uuid, wr.data_value)

        return mp.WriteResponse(True)

    def process_read_request(self, rr: mp.ReadRequest) -> mp.ReadResponse:
        """
        Функция обработки запроса на чтение

        :param rr: запрос на чтение
        :return: ответ на запрос на чтение
        """

        print('Storage node - read request: %s' % mp.Serializer.to_json(rr))

        if rr.data_key in self.data_dict:
            ts, writer_uuid, data_value = self.data_dict[rr.data_key]
            return mp.ReadResponse(True, writer_uuid, ts, rr.data_key, data_value)

        return mp.ReadResponse(False, '', 0, rr.data_key, '')


def main(argv):
    """
    Запуск сервера

    :param argv: массив параметров: 1 - порт сервера
    """
    ss = StorageNode(int(argv[1]))
    ss.run()


if __name__ == "__main__":
    main(sys.argv)
