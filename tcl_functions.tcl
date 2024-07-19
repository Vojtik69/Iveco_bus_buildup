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

proc equivalence {} {
    *createmark nodes 1 "all"
    *equivalence nodes 1 0.01 1 0 0 0
}

proc relink_connectors {} {
    *clearmark connectors 1
    *createmark connectors 1 "all"
    set inputList [hm_ce_datalist 1]

    set createarrayCmd "*createarray"
    set num_elements [llength $inputList]
    # Append the count of elements in inputList multiplied by 2 (each ID followed by -1)
    append createarrayCmd " [expr {$num_elements * 2}]"
    foreach item $inputList {
        set id [lindex $item 0]
        append createarrayCmd " $id -1"
    }
    eval $createarrayCmd

    *createmark components 2 "displayed"

    set createdoublearrayCmd "*createdoublearray $num_elements"
    # Append the required number of zeros
    for {set i 0} {$i < $num_elements} {incr i} {
        append createdoublearrayCmd " 0"
    }
    # Evaluate the final command
    eval $createdoublearrayCmd

    *createstringarray 5 "ce_spot_extralinknum=0" "ce_seam_extralinknum=0" "ce_spot_non_normal=1" \
      "ce_area_non_normal=0" "ce_preferdifflinksperlayer=0"
    *CE_AddLinkEntitiesWithArrays 1 [expr {$num_elements * 2}] components 2 1 1 1 1 1 $num_elements 0 1 5

}

proc realize_in_order {what} {
    *clearmark connectors 1
    *createmark connectors 1 "all"
    set inputList [hm_ce_datalist 1]
    set stitch {}
    set others {}
    set unrealized {}

    if {$what == "unrealized"} {
        foreach item $inputList {
            set id [lindex $item 0]
            set state [lindex $item end]
            if {$state == "realized"} {
                lappend unrealized $id
            }
        }
        *createmark connectors 1 $unrealized
    }

    foreach item $inputList {
        set id [lindex $item 0]
        set config [lindex $item 4]
        if {$config == "stitch"} {
            lappend stitch $id
        } else {
            lappend others $id
        }
    }

    *clearmark connectors 1
    if {[llength $stitch] > 0} {
        eval *createmark connectors 1 $stitch
        *CE_Realize 1
    }
    if {[llength $others] > 0} {
        eval *createmark connectors 2 $others
        *CE_Realize 2
    }
}

proc realize_connectors {} {
    *setoption g_ce_elem_org_option=4
    relink_connectors
    *clearmark connectors 1
    *createmark connectors 1 "all"
    *CE_ConnectorRemoveDuplicates 1 0.1
    realize_in_order "all"
    *clearmark connectors 1
    equivalence
    *modelcheck_applyautocorrection Multiple Rigids or RBE3s sharing nodes ALL ALL 0
}

proc unrealize_connectors {} {
    *clearmark connectors 1
    *createmark connectors 1 all
    *CE_Unrealize 1
}

proc move_include {new_name id x y z} {
    *createmark nodes 1 "by include" $id
    *createmark connectors 1 "by include" $id

    *createvector 1 $x $y $z

    set magnitude [expr {sqrt($x*$x + $y*$y + $z*$z)}]
    if {[hm_marklength nodes 1] > 0} {
        *translatemark nodes 1 1 $magnitude
        }
    if {[hm_marklength connectors 1] > 0} {
        *translatemark connectors 1 1 $magnitude
        }

    *updateinclude $id 1 $new_name 0 0 0 0
}




#======position ======
#*positionentity nodes mark=1 "source_coords={-8938.2431640625 -926.2951049805 3203.4934082031}" "target_coords={-9177.6240234375 -926.2906494141 3203.4904785156}"

#======connector type ========
#% hm_ce_info 131 fetypename
#stitch
#% hm_ce_type 131
#seam
#% hm_ce_getconnectorcontrol 131
#connectorcontrols 5 connectorcontrol2


#======get coordinations =====
#hm_getentityvalue NODE 3853876 y 0

#hm_ce_datalist 1
#{5 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {6 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {127 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {130 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {129 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {128 3 {} point/node {rigidlnk (midnode)} comp 1087 elems use-id unrealized} {7 3 {} point/node {rigidlnk (midnode)} comp 1634 elems use-id unrealized} {8 3 {} point/node {rigidlnk (midnode)} comp 1634 elems use-id comp 1087 elems use-id unrealized} {9 3 {} point/node {rigidlnk (midnode)} comp 1634 elems use-id comp 1087 elems use-id unrealized} {10 3 {} point/node {rigidlnk (midnode)} comp 1634 elems use-id comp 1087 elems use-id unrealized} {11 3 {} point/node {rigidlnk (midnode)} comp 1634 elems use-id unrealized} {12 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id unrealized} {13 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id unrealized} {14 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id unrealized} {15 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id unrealized} {16 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id unrealized} {17 2 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id comp 1087 elems use-id realized} {18 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {19 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {20 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {21 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {22 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {23 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {24 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {25 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {26 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {27 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {28 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {29 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {30 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {31 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {32 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id comp 1087 elems use-id unrealized} {33 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {34 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {35 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {36 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {37 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {38 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {39 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {40 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {41 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {42 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {43 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {44 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {45 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {46 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {47 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {48 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {49 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {50 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {51 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {52 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {53 3 {} point/node {rigidlnk (midnode)} comp 1638 elems use-id unrealized} {54 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id unrealized} {55 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {56 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {57 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {58 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {59 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {60 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {61 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {62 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {63 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {64 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {65 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {66 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {67 3 {} point/node {rigidlnk (midnode)} comp 1067 elems use-id unrealized} {68 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {69 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {70 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {71 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {72 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {73 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {74 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {75 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {76 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {77 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {78 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {79 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {80 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {81 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {82 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {83 3 {} point/node {rigidlnk (midnode)} comp 1633 elems use-id unrealized} {84 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {85 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {86 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {87 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {88 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {89 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {90 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {91 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {92 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {93 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {94 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {95 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {96 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {97 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {98 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {99 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {100 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {101 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {102 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {103 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {104 3 {} point/node {rigidlnk (midnode)} comp 1023 elems use-id unrealized} {105 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {106 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {107 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {108 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {109 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {110 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {111 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {112 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {113 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {114 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized} {115 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized}


#{115 3 {} point/node {rigidlnk (midnode)} comp 1033 elems use-id comp 1012 elems use-id unrealized}
#{131 2 {} seam       stitch               comp 1087 elems use-id {failed:  Only 0 projections could be made for one or more of the test points, layers specified is 2.}}