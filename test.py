
import yaml
import os.path
import pandas as pd

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

def find_superordinants(data_structure, name, superordinants = []):
    path = find_path_to_name(data_structure, name)[:-4]
    superordinant_element = get_element_by_path(data_structure, path)
    for ft in superordinant_element.get("FTs",[]):
        superordinants.append(ft.get("name",""))
    if superordinant_element.get("skippable", False):
        find_superordinants(superordinant_element, name, superordinants)

    return superordinants

# print(find_path_to_name(hierarchie_typu, "FT 6"))
# adresa = find_path_to_name(hierarchie_typu, "FT 6")
#
# print(get_element_by_path(hierarchie_typu,adresa))

find_superordinants(hierarchie_typu, "FT 6")




