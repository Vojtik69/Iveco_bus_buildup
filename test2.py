import pandas as pd

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=[0, 1, 2, 3],
                    header=[0, 1, 2], skipinitialspace=True)
parts.columns.names = [None] * len(parts.columns.names)

def findCompatibility(df, name2ndColumn, name3rdRow):
    # Vyhledání řádku na základě názvu ve druhém sloupci (2. úroveň multiindexu)
    idx = df.index.get_level_values(1) == name2ndColumn
    row = df[idx]

    # Vyhledání hodnoty z daného sloupce třetího řádku (součást víceúrovňového záhlaví)
    try:
        value = row.xs(name3rdRow, level=2, axis=1).iloc[0,0]
        if pd.isna(value):
            value = 0  # Nahrazení NaN hodnotou 0
    except KeyError:
        value = 0  # Pokud neexistuje daný sloupec, vrátí None
    print(value)
    return value

print(findCompatibility(parts, "Other2","Diesel"))