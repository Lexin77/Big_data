"""
Модуль реализации протокола взаимодействия между узлами

Идейно содержит несколько блоков:
* Классы, реализующие типы сообщений
* Статический класс, реализующий функции сериализации-десериализации
* Набор функций, обеспечивающий обмен сообщениями на техническом уровне
"""

import json
import socket

"""Разделитель сообщений. Нужен для создания фреймов при сокетном взаимодействии процессов"""
MESSAGE_SEP_STR = u'62afa5dd2c73fadc1c37f23ee1d21f73689edc54d0fe59ba53f40c0128577c1c'


class BaseMessage:
    """
    Базовый класс все сообщений
    """

    SET_REQUEST_TYPE_STR = 'set_request'
    SET_RESPONSE_TYPE_STR = 'set_response'
    GET_REQUEST_TYPE_STR = 'get_request'
    GET_RESPONSE_TYPE_STR = 'get_response'
    WRITE_REQUEST_TYPE_STR = 'write_request'
    WRITE_RESPONSE_TYPE_STR = 'write_response'
    READ_REQUEST_TYPE_STR = 'read_request'
    READ_RESPONSE_TYPE_STR = 'read_response'

    def __init__(self, type_str: str):
        self.message_type = type_str


class SetRequest(BaseMessage):
    """
    Сообщение о запросе на установку занчения по ключу (передаётся от KVS к AccessPointNode)
    """

    def __init__(self, key: str, value: str):
        """
        Конструктор

        :param key: ключ, по которому устанавливается значение
        :param value: устанавливаемое значение
        """
        super(SetRequest, self).__init__(BaseMessage.SET_REQUEST_TYPE_STR)
        self.data_key = key
        self.data_value = value


class SetResponse(BaseMessage):
    """
    Ответ на сообщение о запросе на установку значения по ключу (передаётся от AccessPointNode к KVS)
    """

    def __init__(self, is_ack: bool):
        """
        Конструктор

        :param is_ack: флаг подверждения выполнения установки значения (True - значение установлено, иначе нет)
        """
        super(SetResponse, self).__init__(BaseMessage.SET_RESPONSE_TYPE_STR)
        self.is_ack = is_ack


class GetRequest(BaseMessage):
    """
    Сообщение запрос на получение данных (передаётся от KVS к AccessPointNode)
    """

    def __init__(self, key: str):
        """
        Конструктор

        :param key: ключ, по которому запрашивается значение
        """
        super(GetRequest, self).__init__(BaseMessage.GET_REQUEST_TYPE_STR)
        self.data_key = key


class GetResponse(BaseMessage):
    """
    Сообщение-ответ на запрос на получение данных (передаётся от AccessPointNode к KVS)
    """

    def __init__(self, key: str, value: str, is_key_exist: bool):
        """
        Конструктор

        :param key: ключ, по которому запрашивались значения
        :param value: значение (в случае если данный ключ не устанавливался - пустая строка)
        :param is_key_exist: флаг наличия ключа в хранилище (True если ключ есть и False если нет)
        """
        super(GetResponse, self).__init__(BaseMessage.GET_RESPONSE_TYPE_STR)
        self.is_key_exist = is_key_exist
        self.data_key = key
        self.data_value = value


class WriteRequest(BaseMessage):
    """
    Запрос на запись данных (передаётся от AccessPointNode к StorageNode)
    """

    def __init__(self, writer_uuid: str, ts: int, key: str, value: str):
        """
        Конструктор

        :param writer_uuid: идентификатор сервера, делающего запись
        :param ts: номер сообщения (линейно возрастающая последовательность для каждого ключа)
        :param key: ключ, по которому осуществляется запись
        :param value: записываемое значение
        """
        super(WriteRequest, self).__init__(BaseMessage.WRITE_REQUEST_TYPE_STR)
        self.writer_uuid = writer_uuid
        self.ts = ts
        self.data_key = key
        self.data_value = value


class WriteResponse(BaseMessage):
    """
    Ответ на запрос на запись данных (передаётся от StorageNode к AccessPointNode)
    """

    def __init__(self, is_ack: bool):
        """
        Конструктор

        :param is_ack: подверждение записи (если True, то запись удалась, если False то нет)
        """

        super(WriteResponse, self).__init__(BaseMessage.WRITE_RESPONSE_TYPE_STR)
        self.is_ack = is_ack


class ReadRequest(BaseMessage):
    """
    Сообщение запрос на получение данных (передаётся от AccessPointNode к StorageNode)
    """

    def __init__(self, key: str):
        """
        Конструктор

        :param key: ключ, по которому запрашивается значение
        """

        super(ReadRequest, self).__init__(BaseMessage.READ_REQUEST_TYPE_STR)
        self.data_key = key


class ReadResponse(BaseMessage):
    """
    Сообщение-ответ на запрос на получение данных (передаётся от StorageNode к AccessPointNode)
    """

    def __init__(self, is_key_exist: bool, writer_uuid: str, ts: int, key: str, value: str):
        """
        Конструктор

        :param writer_uuid: идентификатор сервера, сделавшего запись
        :param is_key_exist: был ли данный ключ пустым
        :param ts: номер сообщения по данному ключу, по которому была осуществлена запись
        :param key: ключ запрашиваемого значения
        :param value: значение
        """
        super(ReadResponse, self).__init__(BaseMessage.READ_RESPONSE_TYPE_STR)
        self.data_key = key
        self.writer_uuid = writer_uuid
        self.ts = ts
        self.is_key_exist = is_key_exist
        self.data_value = value
        self.writer_uuid = writer_uuid


class Serializer:
    """
    Статичный класс, осуществляющий сериализацию-десериализацию сообщений
    """

    @staticmethod
    def to_json(message: BaseMessage) -> str:
        """
        Сериализация сообщения в json строку

        :param message: сообщение, которое необходимо сериализовать
        :return: сериализованное сообщение (json строка)
        """

        if message.message_type == BaseMessage.SET_REQUEST_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "data_key": message.data_key,
                "data_value": message.data_value
            }
        elif message.message_type == BaseMessage.SET_RESPONSE_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "is_ack": message.is_ack
            }
        elif message.message_type == BaseMessage.GET_REQUEST_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "data_key": message.data_key
            }
        elif message.message_type == BaseMessage.GET_RESPONSE_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "data_key": message.data_key,
                "data_value": message.data_value,
                "is_key_exist": message.is_key_exist
            }
        elif message.message_type == BaseMessage.WRITE_REQUEST_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "ts": message.ts,
                "writer_uuid": message.writer_uuid,
                "data_key": message.data_key,
                "data_value": message.data_value
            }
        elif message.message_type == BaseMessage.WRITE_RESPONSE_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "is_ack": message.is_ack
            }
        elif message.message_type == BaseMessage.READ_REQUEST_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "data_key": message.data_key
            }
        elif message.message_type == BaseMessage.READ_RESPONSE_TYPE_STR:
            obj_dict = {
                "message_type": message.message_type,
                "is_key_exist": message.is_key_exist,
                "ts": message.ts,
                "writer_uuid": message.writer_uuid,
                "data_key": message.data_key,
                "data_value": message.data_value
            }
        else:
            raise ValueError('Unsupported message type')

        return json.dumps(obj_dict)

    @staticmethod
    def from_json(json_str: str) -> BaseMessage:
        """
        Десериализация сообщения из json строки

        :param json_str: json представление сообщения
        :return: сообщение в виде объекта Python
        """

        obj_dict = json.loads(json_str)
        message_type = obj_dict['message_type']

        if message_type == BaseMessage.SET_REQUEST_TYPE_STR:
            return SetRequest(obj_dict['data_key'], obj_dict['data_value'])

        elif message_type == BaseMessage.SET_RESPONSE_TYPE_STR:
            return SetResponse(obj_dict['is_ack'])

        elif message_type == BaseMessage.GET_REQUEST_TYPE_STR:
            return GetRequest(obj_dict['data_key'])

        elif message_type == BaseMessage.GET_RESPONSE_TYPE_STR:
            return GetResponse(obj_dict['data_key'], obj_dict['data_value'], obj_dict['is_key_exist'])

        elif message_type == BaseMessage.WRITE_REQUEST_TYPE_STR:
            return WriteRequest(obj_dict['writer_uuid'],
                                int(obj_dict['ts']),
                                obj_dict['data_key'],
                                obj_dict['data_value'])
        elif message_type == BaseMessage.WRITE_RESPONSE_TYPE_STR:
            return WriteResponse(obj_dict['is_ack'])

        elif message_type == BaseMessage.READ_REQUEST_TYPE_STR:
            return ReadRequest(obj_dict['data_key'])

        elif message_type == BaseMessage.READ_RESPONSE_TYPE_STR:
            return ReadResponse(obj_dict['is_key_exist'],
                                obj_dict['writer_uuid'],
                                obj_dict['ts'],
                                obj_dict['data_key'],
                                obj_dict['data_value'])

        else:
            raise ValueError('Unsupported message type')


def socket_receive_message(sock: socket.socket) -> str:
    """
    Вспомогательная функция получения сообщения из сокета. Сообщение преобразуется в строку (используется utf-8)

    :param sock: открытый сокет
    :return: полученное сообщение
    """

    res = u''

    while True:
        d = sock.recv(1024)
        res = res + d.decode('utf-8')
        if MESSAGE_SEP_STR in res:
            break
    res = res.replace(MESSAGE_SEP_STR, '')
    return res


def socket_send_message(client_socket: socket.socket, message: str):
    """
    Вспомогательная функция отправки сообщения по сокету

    :param client_socket: открытый клиенсткий сокет
    :param message: сообщение в виде строки utf-8
    """

    msg_with_sep = message + MESSAGE_SEP_STR
    byte_msg = bytes(msg_with_sep, 'utf-8')
    client_socket.send(byte_msg)


def send_message(host: str, port: int, message: BaseMessage) -> BaseMessage:
    """
    Функция отправки сообщения от ноды к ноде и получения ответа (все взаимодействия по схеме: запрос - ответ)

    :param host: хост, на котором расположена нода
    :param port: порт, который слушает нода
    :param message: передаваемое сообщения
    :return: сообщение полученное в ответ
    """
    message_json_str = Serializer.to_json(message)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    socket_send_message(client_socket, message_json_str)
    response_json_str = socket_receive_message(client_socket)
    client_socket.close()

    result = Serializer.from_json(response_json_str)

    return result
