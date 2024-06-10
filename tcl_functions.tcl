proc import_data {file_path part_name solver} {
set filename [file tail $file_path]
*createinclude 0 $part_name $file_path 0
*attributeupdatestring cards 1 5015 20 1 0 $part_name
if {$solver == 2} {
    *createstringarray 13 "OptiStruct " " " "ASSIGNPROP_BYHMCOMMENTS " "CREATE_PART_HIERARCHY" \
      "IMPORT_MATERIAL_METADATA" "ANSA " "PATRAN " "EXPAND_IDS_FOR_FORMULA_SETS " \
      "CONTACTSURF_DISPLAY_SKIP " "LOADCOLS_DISPLAY_SKIP " "SYSTCOLS_DISPLAY_SKIP " \
      "VECTORCOLS_DISPLAY_SKIP " "\[DRIVE_MAPPING= \]"
    *feinputwithdata2 "\#optistruct\\optistruct" $file_path 0 0 0 0 0 1 13 1 0
} else {
    *createstringarray 23 "RadiossBlock " "Radioss2023 " "~D01_OPTION 1 " "ASSIGNPROP_BYHMCOMMENTS " \
      "CREATE_PART_HIERARCHY" "IMPORT_MATERIAL_METADATA" "~FE_READ_OPTIMIZATION_FILE 0 " \
      "READ_INITIAL_SHELL_Data " "READ_INITIAL_BRICK_Data " "SingleCollector " \
      "SKIP_HYPERBEAM_MESSAGES " "ACCELEROMETERS_DISPLAY_SKIP" "PRIMITIVES_DISPLAY_SKIP" \
      "CONSTRAINTS_DISPLAY_SKIP " "CONTACTSURF_DISPLAY_SKIP" "CROSSSECTION_DISPLAY_SKIP" \
      "LOADCOLS_DISPLAY_SKIP" "RIGIDWALLS_DISPLAY_SKIP" "RETRACTORS_DISPLAY_SKIP" \
      "SOLVERMASSES_DISPLAY_SKIP" "SYSTCOLS_DISPLAY_SKIP" "INITIALGEOMETRIES_DISPLAY_SKIP" \
      "SLIPRINGS_DISPLAY_SKIP "
    *feinputwithdata2 "\#radioss\\radiossblk" $file_path 0 0 0 0 0 1 23 1 0
}
*setcurrentinclude 0 ""
}

proc changing_interface_finished {} {
    global change_finished
    set change_finished true
}

proc realize_connectors {} {
# TODO: update link
*setoption g_ce_elem_org_option=4
*clearmark connectors 1
*createmark connectors 1 "all"
*CE_MarkUpdateLink 1 comps 4 4
*CE_ConnectorRemoveDuplicates 1 0.1
*CE_Realize 1
*clearmark connectors 1
}


#======position ======
#*positionentity nodes mark=1 "source_coords={-8938.2431640625 -926.2951049805 3203.4934082031}" "target_coords={-9177.6240234375 -926.2906494141 3203.4904785156}"



#======get coordinations =====
#hm_getentityvalue NODE 3853876 y 0