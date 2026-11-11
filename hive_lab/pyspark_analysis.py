"""NBA shot-log analytics with Apache Spark (PySpark)."""

import argparse

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import (
    DoubleType,
    IntegerType,
    LongType,
    StringType,
    StructField,
    StructType,
)


SCHEMA = StructType(
    [
        StructField("game_id", StringType()),
        StructField("matchup", StringType()),
        StructField("location", StringType()),
        StructField("win", StringType()),
        StructField("final_margin", IntegerType()),
        StructField("shot_number", IntegerType()),
        StructField("period", IntegerType()),
        StructField("game_clock", StringType()),
        StructField("shot_clock", DoubleType()),
        StructField("dribbles", IntegerType()),
        StructField("touch_time", DoubleType()),
        StructField("shot_dist", DoubleType()),
        StructField("pts_type", IntegerType()),
        StructField("shot_result", StringType()),
        StructField("closest_defender", StringType()),
        StructField("closest_defender_player_id", LongType()),
        StructField("close_def_dist", DoubleType()),
        StructField("fgm", IntegerType()),
        StructField("pts", IntegerType()),
        StructField("player_name", StringType()),
        StructField("player_id", LongType()),
    ]
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        nargs="?",
        default="hive_lab/shot_logs.csv",
        help="CSV path: local path, file:///... or hdfs:///...",
    )
    parser.add_argument(
        "--output",
        help="Optional output directory (local or HDFS) for Parquet results",
    )
    args = parser.parse_args()

    spark = SparkSession.builder.appName("NBA Shot Log Analytics").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    shots = (
        spark.read.option("header", True)
        .option("multiLine", False)
        .schema(SCHEMA)
        .csv(args.input)
        .filter(F.col("player_id").isNotNull() & F.col("fgm").isin(0, 1))
        .cache()
    )

    print("\n=== Dataset size ===")
    print(f"Valid shot records: {shots.count():,}")

    distance_group = (
        F.when(F.col("shot_dist") < 5, "00-04 ft")
        .when(F.col("shot_dist") < 10, "05-09 ft")
        .when(F.col("shot_dist") < 15, "10-14 ft")
        .when(F.col("shot_dist") < 20, "15-19 ft")
        .when(F.col("shot_dist") < 25, "20-24 ft")
        .otherwise("25+ ft")
    )
    by_distance = (
        shots.where(F.col("shot_dist").isNotNull())
        .withColumn("distance_group", distance_group)
        .groupBy("distance_group")
        .agg(F.count("*").alias("attempts"), F.sum("fgm").alias("made"))
        .withColumn("accuracy_pct", F.round(100 * F.col("made") / F.col("attempts"), 2))
        .orderBy("distance_group")
    )
    print("\n=== Field goal accuracy by shot distance ===")
    by_distance.show(truncate=False)

    defender_group = (
        F.when(F.col("close_def_dist") < 2, "00-1.9 ft")
        .when(F.col("close_def_dist") < 4, "02-3.9 ft")
        .when(F.col("close_def_dist") < 6, "04-5.9 ft")
        .otherwise("06+ ft")
    )
    by_defender_distance = (
        shots.where(F.col("close_def_dist").isNotNull())
        .withColumn("defender_distance_group", defender_group)
        .groupBy("defender_distance_group")
        .agg(F.count("*").alias("attempts"), F.sum("fgm").alias("made"))
        .filter(F.col("attempts") >= 1000)
        .withColumn("accuracy_pct", F.round(100 * F.col("made") / F.col("attempts"), 2))
        .orderBy("defender_distance_group")
    )
    print("\n=== Field goal accuracy by nearest defender distance ===")
    by_defender_distance.show(truncate=False)

    top_players = (
        shots.groupBy("player_name")
        .agg(F.count("*").alias("attempts"), F.sum("fgm").alias("made"))
        .filter(F.col("attempts") >= 500)
        .withColumn("accuracy_pct", F.round(100 * F.col("made") / F.col("attempts"), 2))
        .orderBy(F.desc("accuracy_pct"), F.desc("attempts"))
        .limit(20)
    )
    print("\n=== Most accurate players (at least 500 attempts) ===")
    top_players.show(20, truncate=False)

    if args.output:
        by_distance.write.mode("overwrite").parquet(f"{args.output}/accuracy_by_distance")
        by_defender_distance.write.mode("overwrite").parquet(
            f"{args.output}/accuracy_by_defender_distance"
        )
        top_players.write.mode("overwrite").parquet(f"{args.output}/top_players")
        print(f"Parquet results saved under: {args.output}")

    shots.unpersist()
    spark.stop()


if __name__ == "__main__":
    main()
