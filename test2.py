import pandas as pd

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=1,
                    header=[0, 1, 2])

print(parts.loc["var_35",("header", "Vehicle Type", "Low Entry") ])
