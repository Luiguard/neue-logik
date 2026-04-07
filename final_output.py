import pandas as pd
df = pd.read_csv(path)
with open(path) as f:
    pass
df = df[df['status'] == 'active']
json_data = df.to_json()
with open(out, 'w') as f:
    f.write(json_data)