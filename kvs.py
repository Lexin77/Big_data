import message_protocol as mp


class KVS:
    """
    Класс клиент key-value хранилища
    """

    def __init__(self, access_point_host: str, access_point_port: int):
        """
        Конструктор клиента key-value хранилища

        :param access_point_host: хост точки доступа к AccessPointNode
        :param access_point_port: порт, который слушает AccessPointNode
        """

        self.access_point_host = access_point_host
        self.access_point_port = access_point_port

    def set(self, key: str, value: str) -> bool:
        """
        Установка значения

        :param key: ключ, по которому требуется установить значение
        :param value: значение для установки
        :return: True если удалось установить значение и False, если не удалось
        """

        set_request = mp.SetRequest(key, value)
        response = mp.send_message(self.access_point_host, self.access_point_port, set_request)

        if type(response) == mp.SetResponse:
            return response.is_ack
        else:
            raise ValueError('Unsupported response')

    def get(self, key: str) -> (bool, str):
        """
        Запрос на получения значения

        :param key: ключ получаемого значения
        :return: (is_success, value): is_success равен True если удалось, если нет, то False; value - значение
        """
        get_request = mp.GetRequest(key)
        response = mp.send_message(self.access_point_host, self.access_point_port, get_request)

        if type(response) == mp.GetResponse:
            if response.is_key_exist:
                return True, response.data_value
            else:
                return False, ""
        else:
            raise ValueError('Unsupported response')

