USE basketball;

SET mapred.job.tracker=local;
SET mapreduce.framework.name=local;

-- Процент попаданий по дистанции броска.
-- CASE распределяет броски по диапазонам. Например, 5.0 фута попадает в группу 05-09 ft.
-- COUNT(*) считает попытки, SUM(fgm) считает попадания (1 — попадание, 0 — промах).
SELECT
    CASE
        WHEN shot_dist < 5 THEN '00-04 ft'
        WHEN shot_dist < 10 THEN '05-09 ft'
        WHEN shot_dist < 15 THEN '10-14 ft'
        WHEN shot_dist < 20 THEN '15-19 ft'
        WHEN shot_dist < 25 THEN '20-24 ft'
        ELSE '25+ ft'
    END AS distance_group,
    COUNT(*) AS attempts,
    SUM(fgm) AS made,
    ROUND(100.0 * SUM(fgm) / COUNT(*), 2) AS accuracy_pct
FROM shot_logs
WHERE shot_dist IS NOT NULL
GROUP BY
    CASE
        WHEN shot_dist < 5 THEN '00-04 ft'
        WHEN shot_dist < 10 THEN '05-09 ft'
        WHEN shot_dist < 15 THEN '10-14 ft'
        WHEN shot_dist < 20 THEN '15-19 ft'
        WHEN shot_dist < 25 THEN '20-24 ft'
        ELSE '25+ ft'
    END
ORDER BY distance_group;

-- Процент попаданий по расстоянию до ближайшего защитника.
-- WHERE убирает броски без дистанции, HAVING оставляет группы с 1000 попыток и более.
SELECT
    CASE
        WHEN close_def_dist < 2 THEN '00-1.9 ft'
        WHEN close_def_dist < 4 THEN '02-3.9 ft'
        WHEN close_def_dist < 6 THEN '04-5.9 ft'
        ELSE '06+ ft'
    END AS defender_distance_group,
    COUNT(*) AS attempts,
    SUM(fgm) AS made,
    ROUND(100.0 * SUM(fgm) / COUNT(*), 2) AS accuracy_pct
FROM shot_logs
WHERE close_def_dist IS NOT NULL
GROUP BY
    CASE
        WHEN close_def_dist < 2 THEN '00-1.9 ft'
        WHEN close_def_dist < 4 THEN '02-3.9 ft'
        WHEN close_def_dist < 6 THEN '04-5.9 ft'
        ELSE '06+ ft'
    END
HAVING COUNT(*) >= 1000
ORDER BY defender_distance_group;

-- Самые точные игроки среди тех, у кого не меньше 500 попыток.
-- При равной точности выше игрок с большим числом попыток. Выводим первые 20 строк.
SELECT
    player_name,
    COUNT(*) AS attempts,
    SUM(fgm) AS made,
    ROUND(100.0 * SUM(fgm) / COUNT(*), 2) AS accuracy_pct
FROM shot_logs
GROUP BY player_name
HAVING COUNT(*) >= 500
ORDER BY accuracy_pct DESC, attempts DESC
LIMIT 20;
