import pandas as pd

df = pd.read_csv(
    "data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
)

df.columns = df.columns.str.strip()

for i, col in enumerate(df.columns):

    print(i, ":", col)