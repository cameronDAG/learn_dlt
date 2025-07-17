import duckdb

def run_duckdb_script(sql_file_path, db_path):
    # Connect to DuckDB (in-memory or file-based)
    conn = duckdb.connect(database=db_path)
    print(conn.execute ("select * from information_schema.schemata").fetchall())

    print(db_path)
    # Read SQL script
    with open(sql_file_path, 'r') as file:
        sql_script = file.read()
    print(file)
    try:
        conn.execute(sql_script)
        print("SQL script executed successfully.")
    except Exception as e:
        print("Error executing script:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    run_duckdb_script("BelajarDLT/query.sql", "data_pipeline.duckdb")
