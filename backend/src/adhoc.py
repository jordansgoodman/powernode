import polars as pl

# df = pl.read_parquet('/Users/jordangoodman/programming/powernode/backend/data/test_read_csv/join_sales_features/join_sales_features.parquet').lazy()

df = pl.read_parquet('/Users/jordangoodman/programming/powernode/backend/data/test_read_csv/filter_holidays/filter_holidays.parquet').lazy()

print(df.collect())

