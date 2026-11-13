-- Создаём базу basketball, если её ещё нет, и выбираем её для следующих команд.
CREATE DATABASE IF NOT EXISTS basketball;
USE basketball;

-- QuickStart запускает HDFS и Hive, но YARN ResourceManager может быть выключен.
SET mapred.job.tracker=local;
SET mapreduce.framework.name=local;

-- При повторном запуске удаляем описание внешней таблицы. CSV остаётся в HDFS.
DROP TABLE IF EXISTS shot_logs;

-- Объявляем колонки внешней таблицы в том же порядке, что и в CSV.
CREATE EXTERNAL TABLE shot_logs (
    game_id STRING,
    matchup STRING,
    location STRING,
    win STRING,
    final_margin INT,
    shot_number INT,
    period INT,
    game_clock STRING,
    shot_clock DOUBLE,
    dribbles INT,
    touch_time DOUBLE,
    shot_dist DOUBLE,
    pts_type INT,
    shot_result STRING,
    closest_defender STRING,
    closest_defender_player_id BIGINT,
    close_def_dist DOUBLE,
    fgm INT,
    pts INT,
    player_name STRING,
    player_id BIGINT
)
-- OpenCSVSerde разбирает поля с учётом запятых и кавычек.
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"'
)
STORED AS TEXTFILE
-- Hive читает файлы из этого каталога HDFS и пропускает строку заголовка.
LOCATION '/user/cloudera/basketball/shot_logs'
TBLPROPERTIES ('skip.header.line.count'='1');

-- Проверяем, сколько записей видит Hive. Для исходного CSV ожидаем 128069.
SELECT COUNT(*) AS shot_count FROM shot_logs;
