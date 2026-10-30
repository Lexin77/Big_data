Инструкция по запуску:
1. Выберите 3 (или более) порта для storage_node (например 40001, 40002, 40003) и 2 (или более порта) для access_point_node (например 50001, 50002)
2. В файл access_point_node_settings.json внесите порты и хосты (если запускаете на разных компьютерах) storage_node
3. Запустите 3 процесса storage_node командами "python storage_node.py 50001", где 40001 порт  (каждый процесс в своём окне cmd)
4. Запустите access_point_node командой "python access_point_node.py 50001 access_point_node_settings.json", где 50001 порт (каждый процесс в своём окне cmd)
5. Повзаимодействуйте с сервером через kvs клиент