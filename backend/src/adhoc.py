import polars as pl

# Query SQLite database using proper URI format
tables_df = pl.read_database_uri(
    query="select * from action_log order by 1 desc",
    uri="sqlite:///Users/jordangoodman/programming/powernode/backend/data/log.db"
)

print(tables_df)
