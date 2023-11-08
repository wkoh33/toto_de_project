import json
import os
import duckdb

def get_duckdb_connection():
    # to start an in-memory database
    con = duckdb.connect(database=':memory:')    
    con.execute(f"LOAD httpfs;")

    return con

def handler(event, context):
    duckdb.sql('SELECT 42').show()

    con = get_duckdb_connection()
    
    #3.maping input files to view input_table.
    query = """
        SELECT * 
        FROM read_json(
            's3://jk-toto-project/data/raw/winning_numbers/*.json',
            format='newline_delimited',
            columns={
                winning_num_1: 'TINYINT',
                winning_num_2: 'TINYINT',
                winning_num_3: 'TINYINT',
                winning_num_4: 'TINYINT',
                winning_num_5: 'TINYINT',
                winning_num_6: 'TINYINT',
                additional_num: 'TINYINT',
                draw_date: 'VARCHAR'
            }
        );
    """
    
    print(query)
    con.sql(query).show()

    return {
        'statusCode': 200,
        'body': json.dumps('Query Executed!')
    }
