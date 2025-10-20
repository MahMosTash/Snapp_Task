import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

pd.set_option('display.max_columns', None)

conn = sqlite3.connect('snapp_dataset.db')

service_colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

query_service = """
                SELECT
                    service_type,
                    COUNT(*) AS count
                FROM dataset_1
                GROUP BY service_type
                ORDER BY count DESC \
                """

df_service = pd.read_sql_query(query_service, conn)

fig1, ax1 = plt.subplots(figsize=(10, 8))

wedges, texts, autotexts = ax1.pie(
    df_service['count'],
    labels=None,  # Remove labels from pie
    colors=service_colors[:len(df_service)],
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 11, 'weight': 'bold'},
    pctdistance=0.85
)

legend_labels = [f'{service}: {count:,} orders' for service, count in zip(df_service['service_type'], df_service['count'])]
ax1.legend(wedges, legend_labels, title="Service Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

ax1.set_title('Order Distribution by Service Type',
              fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('pie_order_count.png', dpi=300, bbox_inches='tight')
plt.show()

query_value_service = """
                      SELECT
                          service_type,
                          SUM(COALESCE(booking_value, 0)) AS total_value
                      FROM dataset_1
                      GROUP BY service_type
                      ORDER BY total_value DESC \
                      """

df_value_service = pd.read_sql_query(query_value_service, conn)

fig2, ax2 = plt.subplots(figsize=(10, 8))

wedges2, texts2, autotexts2 = ax2.pie(
    df_value_service['total_value'],
    labels=None,
    colors=service_colors[:len(df_value_service)],
    autopct='%1.1f%%',
    startangle=90,
    textprops={'fontsize': 11, 'weight': 'bold'},
    pctdistance=0.85
)

legend_labels = [f'{service}: {value:,.0f}' for service, value in zip(df_value_service['service_type'], df_value_service['total_value'])]
ax2.legend(wedges2, legend_labels, title="Service Types", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=10)

ax2.set_title('Booking Value Distribution by Service Type',
              fontsize=16, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('pie_booking_value.png', dpi=300, bbox_inches='tight')
plt.show()

query_weekly = """
               SELECT
                   strftime('%Y-W%W', order_date) AS week,
                   status_order,
                   COUNT(*) AS count
               FROM dataset_1
               GROUP BY week, status_order
               ORDER BY week \
               """

df_weekly = pd.read_sql_query(query_weekly, conn)

weekly_pivot = df_weekly.pivot_table(
    index='week',
    columns='status_order',
    values='count',
    fill_value=0
)

weekly_totals = weekly_pivot.sum(axis=1)
if 'Completed' in weekly_pivot.columns:
    confirm_rate = (weekly_pivot['Completed'] / weekly_totals * 100)
else:
    confirm_rate = pd.Series(0, index=weekly_pivot.index)

fig3, ax1 = plt.subplots(figsize=(16, 8))

x_pos = np.arange(len(weekly_pivot))
weekly_pivot.plot(kind='bar', stacked=True, ax=ax1, width=0.8, alpha=0.8)
ax1.set_xlabel('Week', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Orders', fontsize=12, fontweight='bold')
ax1.set_title('Weekly Orders by Status with Confirmation Rate', fontsize=16, fontweight='bold')
ax1.legend(title='Status', bbox_to_anchor=(1.15, 1), loc='upper left')
ax1.grid(axis='y', alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(x_pos, confirm_rate.values,
         color='red', linewidth=3, marker='o', markersize=6, label='Confirm Rate (%)')
ax2.set_ylabel('Confirmation Rate (%)', fontsize=12, fontweight='bold', color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.legend(loc='upper right')

ax1.set_xticklabels(weekly_pivot.index, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('weekly_orders_combo_chart.png', dpi=300, bbox_inches='tight')
plt.show()

conn.close()
