from pyspark.sql import SparkSession

def process_data(input_path, output_path):
    spark = SparkSession.builder \
        .appName("S3DataTransformation") \
        .getOrCreate()

    # Read data from S3
    input_df = spark.read.parquet(input_path)

    # Convert all columns to string
    transformed_df = input_df.select(
        *[input_df[col].cast("string").alias(col) for col in input_df.columns]
    )

    # Write transformed data back to S3
    transformed_df.write.mode("overwrite").parquet(output_path)

    spark.stop()

if __name__ == "__main__":
    input_path = "s3://source-data-bucket/raw_data/"
    output_path = "s3://destination-data-bucket/transformed_data/"
    process_data(input_path, output_path)
