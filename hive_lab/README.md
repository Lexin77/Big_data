# Hive лабораторная: броски NBA

## Данные

Kaggle: [NBA Shot Logs](https://www.kaggle.com/datasets/dansbecker/nba-shot-logs). CSV содержит записи о бросках сезона NBA 2014–2015: игрок, матч, дистанция броска, ближайший защитник и результат. В `shot_logs.csv` находится 128 069 записей и одна строка заголовка.

## Загрузка в Cloudera QuickStart

Файлы из этого каталога находятся на Windows-хосте. Если имя контейнера `cloudera`, скопируйте CSV:

```powershell
docker cp .\hive_lab\shot_logs.csv cloudera:/tmp/shot_logs.csv
docker exec -it cloudera bash
```

Внутри контейнера выполните:

```bash
hdfs dfs -mkdir -p /user/cloudera/basketball/shot_logs
hdfs dfs -put -f /tmp/shot_logs.csv /user/cloudera/basketball/shot_logs/
```

Затем в другой команде PowerShell выполните Hive-скрипты из корня проекта:

```powershell
docker cp .\hive_lab\01_create_table.hql cloudera:/tmp/01_create_table.hql
docker cp .\hive_lab\02_analysis.hql cloudera:/tmp/02_analysis.hql
docker exec -it cloudera bash -lc "hive -f /tmp/01_create_table.hql"
docker exec -it cloudera bash -lc "hive -f /tmp/02_analysis.hql"
```

Первый скрипт создаёт внешнюю таблицу и выводит количество загруженных записей. Второй считает точность попаданий по расстоянию до кольца, расстоянию до защитника и игрокам с минимум 500 попытками.

В Cloudera QuickStart можно также выполнить HQL через Hue. Для этого сначала положите CSV в HDFS по указанному пути, затем откройте Hive Editor и скопируйте содержимое `.hql` файлов.

## Вариант лабораторной на PySpark

Для задания по Apache Spark используйте `pyspark_analysis.py`. Скрипт читает CSV с явной схемой через `SparkContext` и `SQLContext` (подходит и для старых Spark 1.x в QuickStart), удаляет записи без `player_id` или с некорректным `fgm`, считает количество записей, точность бросков по расстоянию до кольца и защитника, а также выводит 20 самых точных игроков с не менее чем 500 попытками. По желанию результаты сохраняются в Parquet.

### Запуск локально

Если установлен Apache Spark и настроен PySpark, из корня репозитория выполните:

```bash
spark-submit --master 'local[*]' hive_lab/pyspark_analysis.py
```

Это прочитает `hive_lab/shot_logs.csv` с локального диска. Можно передать другой путь явно:

```bash
spark-submit --master 'local[*]' hive_lab/pyspark_analysis.py /path/to/shot_logs.csv
```

### Загрузка в HDFS и запуск в Cloudera Docker

В командах ниже предполагается, что контейнер называется `cloudera`. В PowerShell из корня проекта скопируйте CSV в контейнер и запустите shell:

```powershell
docker cp .\hive_lab\shot_logs.csv cloudera:/tmp/shot_logs.csv
docker cp .\hive_lab\pyspark_analysis.py cloudera:/tmp/pyspark_analysis.py
docker exec -it cloudera bash
```

В контейнере загрузите файл в HDFS:

```bash
hdfs dfs -mkdir -p /user/cloudera/basketball/shot_logs
hdfs dfs -put -f /tmp/shot_logs.csv /user/cloudera/basketball/shot_logs/
hdfs dfs -ls /user/cloudera/basketball/shot_logs
```

Запустите обработку, указав HDFS URI (три слэша после `hdfs:`):

```bash
spark-submit --master local[*] /tmp/pyspark_analysis.py hdfs:///user/cloudera/basketball/shot_logs/shot_logs.csv
```

Для сохранения агрегатов в HDFS добавьте аргумент `--output`:

```bash
spark-submit --master local[*] /tmp/pyspark_analysis.py hdfs:///user/cloudera/basketball/shot_logs/shot_logs.csv --output hdfs:///user/cloudera/basketball/pyspark_results
hdfs dfs -ls /user/cloudera/basketball/pyspark_results
```

Если `spark-submit` отсутствует в PATH, проверьте в контейнере `which spark-submit` и `which pyspark`. `pyspark` открывает интерактивную оболочку; в ней можно выполнить те же выражения PySpark из скрипта, создав `SparkSession` и читая `hdfs:///user/cloudera/basketball/shot_logs/shot_logs.csv`. Для запуска готового файла удобнее `spark-submit`. Если запуск ругается на `/user/spark/applicationHistory`, выполните указанные преподавателем команды от пользователя `hdfs`:

```bash
su hdfs
hadoop fs -chmod 777 /user/spark/applicationHistory
exit
```

Затем повторите запуск Spark. Проверьте, что первая строка вывода показывает около 128 тысяч записей, а таблицы агрегатов содержат ненулевое число попыток. В отчёте опишите цель анализа, загрузку CSV в HDFS, действия PySpark (`filter`, `withColumn`, `groupBy`, `agg`, `orderBy`) и полученные наблюдения из таблиц.
