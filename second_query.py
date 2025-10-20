import sqlite3
import pandas as pd

conn = sqlite3.connect('snapp_dataset.db')

query = """
        WITH hire_fire_dates AS (
            SELECT HireDate AS the_date
            FROM employee
            WHERE HireDate IS NOT NULL
            UNION
            SELECT TerminationDate AS the_date
            FROM employee
            WHERE TerminationDate IS NOT NULL
        ),

         ordered_dates AS (
             SELECT the_date
             FROM hire_fire_dates
             ORDER BY the_date
         ),

        date_pairs AS (
        SELECT
            first_date.the_date AS from_date,
             next_date.the_date AS to_date,
             JULIANDAY(next_date.the_date) - JULIANDAY(first_date.the_date) AS days_diff
         FROM ordered_dates first_date
                 JOIN ordered_dates next_date ON next_date.the_date = (
             SELECT MIN(the_date)
             FROM ordered_dates
             WHERE the_date > first_date.the_date
         )
     )

    SELECT MAX(days_diff) AS max_days_between_changes
    FROM date_pairs; 
    """

df = pd.read_sql_query(query, conn)
print(df.to_string(index=False))
conn.close()