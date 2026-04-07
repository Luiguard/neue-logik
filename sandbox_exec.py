path = 'test_data.csv'
out = 'out_data.json'
import pandas as pd
df = pd.read_csv(path)
with open(path) as f:
    pass
df = df[df['status'] == 'active']
with open(out, 'w') as f:
    f.write(json_data)