import pandas as pd
import sqlite3

excel_path = "Datasets_-_DER.xlsx"
conn = sqlite3.connect("snapp_dataset.db")

xls = pd.ExcelFile(excel_path)

def clean_columns(df):
    cols = []
    for i, c in enumerate(df.columns):
        if pd.isna(c) or c == "":
            c = f"col_{i+1}"
        c = str(c).strip().replace(" ", "_")
        cols.append(c)
    seen = {}
    unique = []
    for c in cols:
        if c in seen:
            seen[c] += 1
            c = f"{c}_{seen[c]}"
        else:
            seen[c] = 0
        unique.append(c)
    df.columns = unique
    return df

for sheet_name in xls.sheet_names:
    df_full = pd.read_excel(xls, sheet_name=sheet_name, header=None)
    df_full = df_full.dropna(how="all").dropna(how="all", axis=1).reset_index(drop=True)
    if sheet_name.lower() == "dataset_2":
        left_df = df_full.iloc[:, :6]
        left_df.columns = left_df.iloc[2]  # header row
        left_df = left_df[3:].reset_index(drop=True)
        left_df = clean_columns(left_df)
        left_df.to_sql("employee", conn, if_exists="replace", index=False)

        right_df = df_full.iloc[:, 7:]
        right_df.columns = right_df.iloc[2]
        right_df = right_df[3:].reset_index(drop=True)
        right_df = clean_columns(right_df)
        right_df.to_sql("annualreviews", conn, if_exists="replace", index=False)

    else:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        df = clean_columns(df)
        table_name = sheet_name.strip().replace(" ", "_").lower()
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    
conn.close()
