"""
PySpark Feature Engineering Script for ML Training
Processes raw data and creates features for failure prediction
"""
import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, datediff, current_date, count, avg, max as spark_max,
    when, lit, coalesce
)
from pyspark.sql.types import DoubleType

def create_spark_session(app_name="CMMS Feature Engineering"):
    """Create and configure Spark session"""
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.adaptive.enabled", "true") \
        .getOrCreate()

def load_data(spark, bucket, date):
    """Load raw data from GCS"""
    assets_path = f"gs://{bucket}/raw_data/assets_{date}.csv"
    work_orders_path = f"gs://{bucket}/raw_data/work_orders_{date}.csv"
    
    assets_df = spark.read.csv(assets_path, header=True, inferSchema=True)
    work_orders_df = spark.read.csv(work_orders_path, header=True, inferSchema=True)
    
    return assets_df, work_orders_df

def engineer_features(assets_df, work_orders_df):
    """Create features for ML model"""
    
    # Calculate asset age in days
    assets_df = assets_df.withColumn(
        "asset_age_days",
        datediff(current_date(), col("acquisition_date"))
    )
    
    # Calculate days since last maintenance
    assets_df = assets_df.withColumn(
        "days_since_last_maintenance",
        datediff(current_date(), col("last_maintenance_date"))
    )
    
    # Calculate work order statistics
    wo_stats = work_orders_df.groupBy("asset_id").agg(
        count("id").alias("total_work_orders"),
        count(when(col("status") == "COMPLETED", 1)).alias("completed_work_orders"),
        count(when(col("priority") == "HIGH", 1)).alias("high_priority_work_orders"),
        count(when(col("priority") == "CRITICAL", 1)).alias("critical_work_orders"),
        avg("actual_hours").alias("avg_repair_hours"),
        spark_max("created_at").alias("last_work_order_date")
    )
    
    # Join features
    features_df = assets_df.join(wo_stats, assets_df.id == wo_stats.asset_id, "left")
    
    # Fill null values
    features_df = features_df.fillna({
        "total_work_orders": 0,
        "completed_work_orders": 0,
        "high_priority_work_orders": 0,
        "critical_work_orders": 0,
        "avg_repair_hours": 0,
        "maintenance_plans_count": 0
    })
    
    # Calculate derived features
    features_df = features_df.withColumn(
        "work_order_completion_rate",
        when(col("total_work_orders") > 0, 
             col("completed_work_orders") / col("total_work_orders"))
        .otherwise(lit(1.0))
    )
    
    features_df = features_df.withColumn(
        "high_priority_ratio",
        when(col("total_work_orders") > 0,
             col("high_priority_work_orders") / col("total_work_orders"))
        .otherwise(lit(0.0))
    )
    
    # Select final features
    final_features = features_df.select(
        "id",
        "asset_code",
        "vehicle_type",
        "asset_age_days",
        "days_since_last_maintenance",
        "total_work_orders",
        "completed_work_orders",
        "high_priority_work_orders",
        "critical_work_orders",
        "avg_repair_hours",
        "maintenance_plans_count",
        "work_order_completion_rate",
        "high_priority_ratio"
    )
    
    return final_features

def save_features(features_df, bucket, date):
    """Save processed features to GCS"""
    output_path = f"gs://{bucket}/processed_data/features_{date}.parquet"
    
    features_df.write \
        .mode("overwrite") \
        .parquet(output_path)
    
    print(f"Features saved to {output_path}")
    print(f"Total records: {features_df.count()}")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Feature Engineering for ML Training')
    parser.add_argument('--input-bucket', required=True, help='GCS bucket for input data')
    parser.add_argument('--output-bucket', required=True, help='GCS bucket for output data')
    parser.add_argument('--date', required=True, help='Execution date (YYYY-MM-DD)')
    
    args = parser.parse_args()
    
    # Create Spark session
    spark = create_spark_session()
    
    try:
        print(f"Loading data for date: {args.date}")
        assets_df, work_orders_df = load_data(spark, args.input_bucket, args.date)
        
        print("Engineering features...")
        features_df = engineer_features(assets_df, work_orders_df)
        
        print("Saving features...")
        save_features(features_df, args.output_bucket, args.date)
        
        print("Feature engineering completed successfully!")
        
    except Exception as e:
        print(f"Error during feature engineering: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
