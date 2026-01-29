import pandas as pd

kaisai_date = "20260124"  # 手元のに変えてOK

path = f"C:/python-script/keiba-lab/data/records/per_race_{kaisai_date}.pkl"
df = pd.read_pickle(path)

print("shape:", df.shape)
print("columns:", df.columns.tolist())
print(df.head(5))
print(df.tail(5))

print("開催 unique:", df["開催"].dropna().unique()[:10])
print("bet_type unique:", df["bet_type"].dropna().unique())
print("axis_col unique:", df["axis_col"].dropna().unique())
