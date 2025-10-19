import sqlite3
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

conn = sqlite3.connect('snapp_dataset.db')

query = """
        SELECT
            service_type,
            status_order,
            COUNT(*) AS count,
            SUM(COUNT(*)) OVER (PARTITION BY service_type) AS total_count,
            SUM(COALESCE(booking_value, 0)) AS status_booking_value,
            SUM(SUM(COALESCE(booking_value, 0))) OVER (PARTITION BY service_type) AS total_booking_value,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY service_type), 2) AS percentage
        FROM dataset_1
        GROUP BY service_type, status_order
        ORDER BY service_type, status_order
        """

df = pd.read_sql_query(query, conn)

pivot_count = df.pivot_table(
    index='service_type',
    columns='status_order',
    values='count',
    aggfunc='sum',
    fill_value=0
)

pivot_percentage = df.pivot_table(
    index='service_type',
    columns='status_order',
    values='percentage',
    aggfunc='first',
    fill_value=0
)

pivot_value = df.pivot_table(
    index='service_type',
    columns='status_order',
    values='status_booking_value',
    aggfunc='sum',
    fill_value=0
)

total_counts = df.groupby('service_type')['total_count'].first()
total_values = df.groupby('service_type')['total_booking_value'].first()

pivot_percentage_formatted = pivot_percentage.copy()
for col in pivot_percentage_formatted.columns:
    pivot_percentage_formatted[col] = pivot_percentage_formatted[col].apply(lambda x: f"{x:.2f}%" if x > 0 else "0.00%")
pivot_percentage_formatted.insert(0, 'Total_Orders', total_counts.astype(int))

pivot_value_formatted = pivot_value.copy()
for col in pivot_value_formatted.columns:
    pivot_value_formatted[col] = pivot_value_formatted[col].apply(lambda x: f"{x:,.0f}" if x > 0 else "0")
pivot_value_formatted.insert(0, 'Total_Orders', total_counts.astype(int))
pivot_value_formatted.insert(1, 'Total_Value', total_values.apply(lambda x: f"{x:,.0f}"))

pivot_value_pct = pivot_value.copy()
for col in pivot_value_pct.columns:
    pivot_value_pct[col] = (pivot_value_pct[col] / total_values * 100).apply(lambda x: f"{x:.2f}%" if x > 0 else "0.00%")
pivot_value_pct.insert(0, 'Total_Orders', total_counts.astype(int))
pivot_value_pct.insert(1, 'Total_Value', total_values.apply(lambda x: f"{x:,.0f}"))

print("ORDER COUNT & PERCENTAGE BY SERVICE TYPE AND STATUS:")
print(pivot_percentage_formatted)


print("\n\nBOOKING VALUE PERCENTAGE BY SERVICE TYPE AND STATUS:")
print(pivot_value_pct)



conn.close()