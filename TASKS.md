# Задание: реализация ABD в шаблоне KeyValueStorageProject

План составлен по ТЗ «Реализация ABD алгоритма» (8 стр.) и шаблону проекта.
Отказоустойчивость (ретраи, `try/except` по ТЗ стр. 8) **в объём не входит**.

## Объём и границы

Меняем только 2 файла и 4 метода:

| # | Файл | Метод |
|---|---|---|
| 1 | `storage_node.py` | `process_write_request` |
| 2 | `storage_node.py` | `process_read_request` |
| 3 | `access_point_node.py` | `process_set_request` |
| 4 | `access_point_node.py` | `process_get_request` |

**Не трогаем:** `kvs.py`, `message_protocol.py`, `base_node.py`, `kvs_test1.py`,
`kvs_test2.py`, `get_quorum()`, формат сообщений.

**Не делаем:** отказоустойчивость/ретраи, многопоточность, сохранение на диск,
TTL, удаление ключей, изменение JSON-протокола.

**Допущения:**

- A1. Хранение по ключу: кортеж `(ts, writer_uuid, value)` в `self.data_dict`.
- A2. `ts` — целое, начинается с `1`.
- A3. Сравнение `writer_uuid` — лексикографическое (строки Python).
- A4. Кворум — существующий `get_quorum()` (`ceil(n/2)`); корректен для 3 и 5
  узлов, поэтому в тестах используем 3 storage-ноды.
- A5. `set` отвечает `True`, только если все узлы кворума подтвердили запись.
- A6. `writer_uuid` в `WriteRequest` от AP = `self._uuid` (id AccessPointNode).
- A7. Read-repair в `get` — только если ключ найден хотя бы на одном узле кворума.

---

## Этап 1. StorageNode — хранение и запись

**S1. Представление данных.**
`self.data_dict[key] = (ts, writer_uuid, value)`; инициализация `{}` уже есть.

**S2. `process_write_request(wr)`** — 4 ветки по блок-схеме ТЗ (стр. 2):

```
если key нет в data_dict:
    data_dict[key] = (wr.ts, wr.writer_uuid, wr.data_value)     -> ack=True
иначе (cur_ts, cur_uuid, cur_val) = data_dict[key]:
    wr.ts >  cur_ts  -> перезаписать                            -> ack=True
    wr.ts <  cur_ts  -> ничего не делать                        -> ack=True
    wr.ts == cur_ts  -> если wr.writer_uuid < cur_uuid:
                            перезаписать                        -> ack=True
                        иначе ничего не делать                  -> ack=True
вернуть WriteResponse(True)
```

Запись никогда не возвращает `False`: она либо применяется, либо игнорируется
как устаревшая.

**S3. `process_read_request(rr)`:**

```
если rr.data_key в data_dict:
    (ts, uuid, val) = data_dict[rr.data_key]
    вернуть ReadResponse(True, uuid, ts, rr.data_key, val)
иначе:
    вернуть ReadResponse(False, '', 0, rr.data_key, '')
```

Порядок аргументов: `ReadResponse(is_key_exist, writer_uuid, ts, key, value)`.

**S4. Критерий готовности:** проверка без сокетов по 5 сценариям (новый ключ;
больший ts; меньший ts; равный ts + меньший uuid; равный ts + больший uuid).

---

## Этап 2. AccessPointNode — операция `set`

**A1.** `q = self.get_quorum()`.

**A2.** Фаза чтения: каждому узлу из `q` — `ReadRequest(key)`, ответы в список `l`.

**A3.** `new_ts = max(ts по записям из l, где is_key_exist) + 1`; ключа нет нигде —
`new_ts = 1`. Брать просто `max(ts)` нельзя: повторная запись того же AP с тем же
`ts` и тем же uuid не пройдёт тай-брейк, и `kvs_test2.py` упадёт.

**A4.** Фаза записи: каждому узлу из `q` — `WriteRequest(self._uuid, new_ts, key, value)`,
собрать `is_ack`.

**A5.** Ответ: `SetResponse(all(acks))`.

**A6. Критерий готовности:** после `set` значение лежит на ≥2 из 3 storage-нод.

---

## Этап 3. AccessPointNode — операция `get`

**G1.** Кворум и чтение — как A1–A2 (можно вынести в `_read_from_quorum`).

**G2.** Отбор актуальной версии среди ответов с `is_key_exist`:

- `max_ts = max(ts)`;
- `min_uuid = min(writer_uuid среди записей с ts == max_ts)`;
- `valid_val = value` записи `(max_ts, min_uuid)`;
- `is_key_exist = список непуст`.

**G3.** Read-repair: если ключ найден — каждому узлу из `q`
`WriteRequest(min_uuid, max_ts, key, valid_val)` (ответы не проверяем).

**G4.** Ответ: найден → `GetResponse(key, valid_val, True)`, иначе
`GetResponse(key, '', False)`.

**G5. Критерий готовности:** `set` через AP1, `get` через AP2 → то же значение.

---

## Этап 4. Проверка по критериям приёма

- **T1.** 3 storage-ноды (`40001-40003`) + 2 AP (`50001`, `50002`).
- **T2.** `python kvs_test1.py` — без `AssertionError`.
- **T3.** `python kvs_test2.py` — 250 итераций, читается ровно записанное.
- **T4.** Краевые случаи: `get` несуществующего ключа; 5 перезаписей подряд;
  чтение через оба AP; остановка storage-ноды — ожидаемая ошибка (вне объёма,
  известное ограничение).

---

## Этап 5. Фиксация в git

1. Коммит S1–S3 → «StorageNode: логика write/read по ABD».
2. Коммит A1–A5, G1–G4 → «AccessPointNode: set/get через кворум + read-repair».
3. Тег `abd-works` на состоянии, где оба теста зелёные.
4. `git diff baseline` — сравнение с исходником.

---

## Итоговая матрица

| Метод | Вход | Результат |
|---|---|---|
| `process_write_request` | `WriteRequest(ts, uuid, key, value)` | применить/проигнорировать по ts→uuid, `WriteResponse(True)` |
| `process_read_request` | `ReadRequest(key)` | `ReadResponse(True, uuid, ts, key, value)` или `(False, '', 0, key, '')` |
| `process_set_request` | `SetRequest(key, value)` | read-кворум → `ts=max+1` → write-кворум → `SetResponse(True/False)` |
| `process_get_request` | `GetRequest(key)` | read-кворум → (max ts, min uuid) → read-repair → `GetResponse` |
