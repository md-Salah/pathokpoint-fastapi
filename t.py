import pandas as pd


df = pd.DataFrame([
    {
        'A': 1,
        'B': 2
    },
    {
        'A': 3,
        'B': 4
    }
])


x = list(df.T.to_dict().values())

print(x)
print(type(x), type(x[0]))