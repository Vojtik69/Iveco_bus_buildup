
====import include =====
*start_batch_import 2
*createinclude 0 "front_mid.inc" "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/02_reduced_BIW_model/first_includes/front_mid.inc" 0
*cardcreate "BEGIN_CARD"
*setvalue cards id=5 STATUS=2 4604=kg
*setvalue cards id=5 STATUS=2 4606=m
*setvalue cards id=5 STATUS=2 4608=s
*setvalue cards id=5 STATUS=0 4610=kg
*setvalue cards id=5 STATUS=0 4612=m
*setvalue cards id=5 STATUS=0 4614=s
*attributeupdatestring cards 5 5015 20 1 0 "front_mid.inc"
*createstringarray 23 "RadiossBlock " "Radioss2023 " "~D01_OPTION 1 " "ASSIGNPROP_BYHMCOMMENTS " \
  "CREATE_PART_HIERARCHY" "IMPORT_MATERIAL_METADATA" "~FE_READ_OPTIMIZATION_FILE 0 " \
  "READ_INITIAL_SHELL_Data " "READ_INITIAL_BRICK_Data " "SingleCollector " \
  "SKIP_HYPERBEAM_MESSAGES " "ACCELEROMETERS_DISPLAY_SKIP" "PRIMITIVES_DISPLAY_SKIP" \
  "CONSTRAINTS_DISPLAY_SKIP " "CONTACTSURF_DISPLAY_SKIP" "CROSSSECTION_DISPLAY_SKIP" \
  "LOADCOLS_DISPLAY_SKIP" "RIGIDWALLS_DISPLAY_SKIP" "RETRACTORS_DISPLAY_SKIP" \
  "SOLVERMASSES_DISPLAY_SKIP" "SYSTCOLS_DISPLAY_SKIP" "INITIALGEOMETRIES_DISPLAY_SKIP" \
  "SLIPRINGS_DISPLAY_SKIP "
*feinputwithdata2 "\#radioss\\radiossblk" "N:/01_DATA/01_PROJECTS/103_Iveco_Model_Buildup/01_data/02_reduced_BIW_model/first_includes/front_mid.inc" 0 0 0 0 0 1 23 1 0
*setcurrentinclude 0 ""
*end_batch_import


======position ======
*positionentity nodes mark=1 "source_coords={-8938.2431640625 -926.2951049805 3203.4934082031}" "target_coords={-9177.6240234375 -926.2906494141 3203.4904785156}"



======get coordinations =====
hm_getentityvalue NODE 3853876 y 0