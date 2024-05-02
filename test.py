
import yaml
import os.path
import pandas as pd

parts = pd.read_csv('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/compatibility.csv', index_col=1,
                    header=[0, 1, 2])
with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchie_typu = yaml.safe_load(file)


def find_path_to_name(data_structure, name, current_path=[]):
    if isinstance(data_structure, list):
        for index, item in enumerate(data_structure):
            new_path = current_path + [index]
            result = find_path_to_name(item, name, new_path)
            if result is not None:
                return result
    elif isinstance(data_structure, dict):
        for key, value in data_structure.items():
            new_path = current_path + [key]
            if key == "name" and value == name:
                return new_path[:-1]
            result = find_path_to_name(value, name, new_path)
            if result is not None:
                return result
    return None

def get_element_by_path(data_structure, path):
    element = data_structure
    try:
        for key_or_index in path:
            element = element[key_or_index]
        return element
    except (KeyError, IndexError):
        return None

def find_superordinant_fts(data_structure, name, superordinants = []):
    path = find_path_to_name(data_structure, name)

    if path is None:
        return superordinants

    # if it first level under header, use header as superordinant
    if path[-4] == "FT groups":
        for header in get_element_by_path(data_structure, ["groups", "headers"]):
            superordinants.append(header.get("name",""))
        return superordinants

    level_up = -4 if path[-2] == "FTs" else -2

    path_level_up = path[:level_up]
    superordinant_element = get_element_by_path(data_structure, path_level_up)
    superordinant_name = get_element_by_path(data_structure, path_level_up[:-2]).get("name","")
    for ft in superordinant_element.get("FTs", []):
        superordinants.append(ft.get("name", ""))
    if superordinant_element.get("skippable", False):
        find_superordinant_fts(data_structure, superordinant_name, superordinants)

    return superordinants


def find_all_of_type(searched_type, remove_empty=False):
    all_of_type = ["---"]
    # print(searched_type)
    if remove_empty:
        all_of_type = []
    for index, row in parts.iterrows():
        # print(index)
        if row.iloc[0] == searched_type and not pd.isna(row.iloc[1]):
            all_of_type.append(index)
    return all_of_type


def find_subordinant_fts(data_structure, name, subordinants = []):
    path = find_path_to_name(data_structure, name)
    if path is None:
        return subordinants

    level_up = -2 if path[-2] == "FTs" else None

    superodinant_element = get_element_by_path(data_structure, path[:level_up])

    for group in superodinant_element.get("groups", []):
        for ft in group.get("FTs", []):
            subordinants.append(ft.get("name",""))

        if group.get("skippable", False):
            find_subordinant_fts(data_structure, group.get("name", ""), subordinants)

    return subordinants


def find_compatible_parts(data_structure, name, removeEmpty = False):
    compatibles = [] if removeEmpty else [("---", "---")]
    superordinants = find_superordinant_fts(data_structure, name, superordinants=[])
    all_of_type = find_all_of_type(name, remove_empty=True)

    for part in all_of_type:
        compatible = True
        for superordinant in superordinants:
            if pd.isna(parts.loc[part, widgetyBuildup[f'vyber_{superordinant}'].get()]):
                compatible = False
                break
        if compatible:
            compatibles.append(part)

    return compatibles



# print(find_path_to_name(hierarchie_typu, "FT 6"))
# adresa = find_path_to_name(hierarchie_typu, "FT 6")
#
# print(get_element_by_path(hierarchie_typu,adresa))

print(find_compatible_parts(hierarchie_typu, "FT 2"))




