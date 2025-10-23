import boto3
from datetime import datetime
from pyspark.sql.types import (
    StringType,
    DateType,
    FloatType,
)
from pyspark.sql.functions import (
    col,
    when,
    trim,
    to_timestamp,
)
from pyspark.sql import SparkSession

# Initialize the Spark session
spark = SparkSession.builder.appName("Currency Batch Job").getOrCreate()

# Load the bank transaction data (parquet format)
df_bank_statement = spark.read.parquet("s3://pysparkapi/banktxn/parquet/")

# Format the value_date column to be a proper timestamp
df_bank_statement = (
    df_bank_statement.withColumn(
        "value_date_formatted",
        to_timestamp(df_bank_statement.value_date, "dd-MMM-yy")
        .cast(DateType())
        .cast(StringType()),
    )
    .drop("value_date")
    .withColumnRenamed("value_date_formatted", "value_date")
)

# Clean up withdrawal_currency column
df_bank_statement = df_bank_statement.withColumn(
    "withdrawal_currency",
    when(trim(col("withdrawal_currency")) == "", None).otherwise(
        col("withdrawal_currency")
    ),
)

# Load the exchange rate data (parquet format)
df_ticker_price_sgd = spark.read.parquet("s3://pysparkapi/api_response/mudra/*/")

# Split the bank statement into rows with null and non-null withdrawal currencies
df_bank_statement_null = df_bank_statement.filter("withdrawal_currency is null")
df_bank_statement_not_null = df_bank_statement.filter("withdrawal_currency is not null")

# Join the bank data with the exchange rates for withdrawal currency
df_bank_statement = (
    df_bank_statement.alias("t1")
    .join(
        df_ticker_price_sgd.alias("t2"),
        (
            (col("t1.value_date") == col("t2.run_date"))
            & (trim(col("t1.withdrawal_currency")) == trim(col("t2.target_currency")))
        ),
        "left",
    )
    .select("t1.*", "t2.rates_base_sgd")
    .withColumnRenamed("rates_base_sgd", "withdrawal_sgd")
)

# Join the bank data with the exchange rates for deposit currency
df_bank_statement = (
    df_bank_statement.alias("t1")
    .join(
        df_ticker_price_sgd.alias("t2"),
        (
            (col("t1.value_date") == col("t2.run_date"))
            & (trim(col("t1.deposit_currency")) == trim(col("t2.target_currency")))
        ),
        "left",
    )
    .select("t1.*", "t2.rates_base_sgd")
    .withColumnRenamed("rates_base_sgd", "deposit_sgd")
)

# Handle the conversion of deposit and withdrawal amounts to SGD
df_bank_statement = df_bank_statement.withColumn(
    "deposit_sgd_amt",
    when(
        col("deposit_sgd").isNotNull(),
        col("deposit_sgd").cast(FloatType()) * col("deposit_amt").cast(FloatType())
    ).otherwise(0)
).withColumn(
    "withdrawal_sgd_amt",
    when(
        col("withdrawal_sgd").isNotNull(),
        col("withdrawal_sgd").cast(FloatType()) * col("withdrawal_amt").cast(FloatType())
    ).otherwise(0)
)

# Write the processed data to S3 in parquet format
df_bank_statement.write.parquet("s3://pysparkapi/banktxn/processed/")
