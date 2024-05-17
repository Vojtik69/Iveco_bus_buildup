import yaml
import inspect
def findPathToName(hierarchy, name, currentPath=[]):
    # print(f"name: {name}")
    # print(f"hierarchy: {hierarchy}")
    if isinstance(hierarchy, list):
        for index, item in enumerate(hierarchy):
            newPath = currentPath + [index]
            result = findPathToName(item, name, newPath)
            if result is not None:
                return result
    elif isinstance(hierarchy, dict):
        for key, value in hierarchy.items():
            newPath = currentPath + [key]
            if key == "name" and value == name:
                return newPath[:-1]
            result = findPathToName(value, name, newPath)
            if result is not None:
                return result
    return None

def getElementByPath(hierarchy, path):
    element = hierarchy
    try:
        for keyOrIndex in path:
            element = element[keyOrIndex]
        return element
    except (KeyError, IndexError):
        return None

with open('N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/types_hierarchy.yaml', 'r') as file:
    hierarchyOfTypes = yaml.safe_load(file)
tclPath = "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/01_python/tcl_functions.tcl"

def findSubordinantFts(hierarchy, name, subordinants = None):
    subordinants = [] if subordinants is None else subordinants
    caller = inspect.stack()[1]
    caller_name = caller.function
    print(f"{caller_name} called my_function")
    print(f"name: {name} - subordinants: {subordinants}")
    path = findPathToName(hierarchy, name)
    print(f"name: {name} - path: {path}")
    if path is None:
        return subordinants

    if path[-2] == "FTs":
        levelUp = -2
        superordinantElement = getElementByPath(hierarchy, path[:levelUp])
        groupsForSearching = superordinantElement.get("groups", [])
    elif path[-2] == "vehicle_spec":
        groupsForSearching = hierarchy["groups"]["FT groups"]
    elif path[-2] == "groups":
        levelUp = -4
        superordinantElement = getElementByPath(hierarchy, path[:levelUp])
        groupsForSearching = superordinantElement.get("groups", [])
    elif path[-2] == "FT groups":
        levelUp = 0
        superordinantElement = getElementByPath(hierarchy, path)
        groupsForSearching = superordinantElement.get("groups", [])


    for group in groupsForSearching:
        for ft in group.get("FTs", []):
            subordinants.append(ft.get("name",""))

        if group.get("skippable", False):
            findSubordinantFts(hierarchy, group.get("name", ""), subordinants)

    return subordinants



print(findSubordinantFts(hierarchyOfTypes, "FT 2"))