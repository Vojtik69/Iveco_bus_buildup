import pandas as pd

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=[0, 1, 2, 3],
                    header=[0, 1, 2], skipinitialspace=True)
parts.columns.names = [None] * len(parts.columns.names)

# print(('header', 'Vehicle Type', 'Low Floor') in list(parts.columns))
print(parts)
for index, row in parts.iterrows():
    print(index[1])
print(list(parts.columns))

print(parts.loc[(slice(None), 'var_D_10'),(slice(None), slice(None), 'Low Floor')])

# Najděte index sloupců, kde druhý řádek má hodnotu 'vehicle_spec'
vehicle_spec_columns = [idx for idx, col in enumerate(parts.columns) if col[1] == 'Vehicle Type']
print(vehicle_spec_columns)
values = [parts.columns[col][2] for col in vehicle_spec_columns]
print(values)

searched_type="FT2"
selectedSolver = 2
all_of_type = ["---"]
for index, row in parts.iterrows():
    # print(index)
    if index[0] == searched_type and not pd.isna(index[selectedSolver]):
        all_of_type.append(index[1])

print(all_of_type)
