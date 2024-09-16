proc import_data {file_path part_name solver} {
    set filename [file tail "$file_path"]
    *createinclude 0 "$part_name" "$file_path" 0
    if {$solver == 2} {
        *createstringarray 13 "OptiStruct " " " "ASSIGNPROP_BYHMCOMMENTS " "CREATE_PART_HIERARCHY" \
          "IMPORT_MATERIAL_METADATA" "ANSA " "PATRAN " "EXPAND_IDS_FOR_FORMULA_SETS " \
          "CONTACTSURF_DISPLAY_SKIP " "LOADCOLS_DISPLAY_SKIP " "SYSTCOLS_DISPLAY_SKIP " \
          "VECTORCOLS_DISPLAY_SKIP " "\[DRIVE_MAPPING= \]"
        *feinputwithdata2 "\#optistruct\\optistruct" "$file_path" 0 0 0 0 0 1 13 1 0
    } else {
        *createstringarray 23 "RadiossBlock " "Radioss2023 " "~D01_OPTION 1 " "ASSIGNPROP_BYHMCOMMENTS " \
          "CREATE_PART_HIERARCHY" "IMPORT_MATERIAL_METADATA" "~FE_READ_OPTIMIZATION_FILE 0 " \
          "READ_INITIAL_SHELL_Data " "READ_INITIAL_BRICK_Data " "SingleCollector " \
          "SKIP_HYPERBEAM_MESSAGES " "ACCELEROMETERS_DISPLAY_SKIP" "PRIMITIVES_DISPLAY_SKIP" \
          "CONSTRAINTS_DISPLAY_SKIP " "CONTACTSURF_DISPLAY_SKIP" "CROSSSECTION_DISPLAY_SKIP" \
          "LOADCOLS_DISPLAY_SKIP" "RIGIDWALLS_DISPLAY_SKIP" "RETRACTORS_DISPLAY_SKIP" \
          "SOLVERMASSES_DISPLAY_SKIP" "SYSTCOLS_DISPLAY_SKIP" "INITIALGEOMETRIES_DISPLAY_SKIP" \
          "SLIPRINGS_DISPLAY_SKIP "
        *feinputwithdata2 "\#radioss\\radiossblk" "$file_path" 0 0 0 0 0 1 23 1 0
    }
    *setcurrentinclude 0 ""
}

proc changing_interface_finished {} {
    global change_finished
    set change_finished true
}

proc equivalence {} {
    *createmark nodes 1 "all"
    *equivalence nodes 1 0.04 1 0 0 0
}

proc relink_connectors {} {
    *clearmark connectors 1
    *createmark connectors 1 "all"
    if {[hm_marklength connectors 1] < 1} {return}
    set inputList [hm_ce_datalist 1]
    set for_components {}
    set for_nodes {}

    foreach item $inputList {
        set id [lindex $item 0]
        set layers [lindex $item 1]
        set config [lindex $item 4]
        if {$layers == 0} {set layers -1}
        if {$config == "spring"} {
            lappend for_nodes $id $layers
        } else {
            lappend for_components $id $layers
        }
    }

    #### FOR_NODES

    set createarrayCmd "*createarray"
    set num_elements [llength $for_nodes]
    set createarrayCmd [concat $createarrayCmd [list $num_elements] $for_nodes]
    eval $createarrayCmd

    *createmark nodes 2 "displayed"

    set createdoublearrayCmd "*createdoublearray $num_elements"
    # Append the required number of zeros
    for {set i 0} {$i < $num_elements} {incr i} {
        append createdoublearrayCmd " 0"
    }
    # Evaluate the final command
    eval $createdoublearrayCmd

    *createstringarray 5 "ce_spot_extralinknum=0" "ce_seam_extralinknum=0" "ce_spot_non_normal=0" \
      "ce_area_non_normal=0" "ce_preferdifflinksperlayer=0"
    *CE_AddLinkEntitiesWithArrays 1 $num_elements nodes 2 1 1 1 1 1 [expr {$num_elements / 2}]  0 1 5
    *clearmark connectors 1

    #### FOR_COMPONENTS

    set createarrayCmd "*createarray"
    set num_elements [llength $for_components]
    set createarrayCmd [concat $createarrayCmd [list $num_elements] $for_components]
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
    *CE_AddLinkEntitiesWithArrays 1 $num_elements components 2 1 1 1 1 1 [expr {$num_elements / 2}]  0 1 5
    *clearmark connectors 1
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
    *clearmark connectors 1
    *clearmark connectors 2
}

proc realize_connectors_by_type {type {id ""}} {
    *clearmark connectors 1
    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - going to realize $type connectors in include $id"
    if {[info exists id] && $id != ""} {
        *createmark connectors 1 "by include" $id
        if {[hm_marklength connectors 1] < 1} {return}
        *setcurrentinclude $id ""
    } else {
        *createmark connectors 1 "all"
        if {[hm_marklength connectors 1] < 1} {return}
    }
    set inputList [hm_ce_datalist 1]
    set stitch {}
    set others {}

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
    *clearmark connectors 2
    if {[llength $stitch] > 0 && [string equal $type "stitch"]} {
        eval *createmark connectors 1 $stitch
        *CE_Realize 1
    }
    if {[llength $others] > 0 && [string equal $type "others"]} {
        eval *createmark connectors 2 $others
        *CE_Realize 2
    }
    *clearmark connectors 1
    *clearmark connectors 2

}

proc change_cardimage_of_rigid_components {} {
    set comp_names [hm_entitylist comps name]

    # Iterate over each item in the list
    foreach item $comp_names {
        # Check if the name contains "rigidlnk (midnode)"
        if {[string first "rigidlnk (midnode)" $item] != -1} {
            eval "*setvalue comps name=\"$item\" cardimage=\"\""
        }
    }

}

proc realize_connectors {} {
    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - in realize_connectors proc"
    set HMversion [hm_info -appinfo VERSION]
    if {$HMversion < 24} {
        *setoption g_ce_elem_org_option=2
    } else {
        *setoption g_ce_org_option=1
    }

    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - going to relink connectors"
    relink_connectors
    *clearmark connectors 1
    *createmark connectors 1 "all"
    *CE_ConnectorRemoveDuplicates 1 0.1

    set includes [hm_getincludes]

    if {$HMversion < 24} {
        foreach include $includes {
            realize_connectors_by_type "stitch" $include
            realize_connectors_by_type "others" $include
         }
    } else {
        realize_connectors_by_type "stitch"
        realize_connectors_by_type "others"
    }

    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - going to equivalence"
    equivalence
    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - going to modelcheck_applyautocorrection"
    *modelcheck_applyautocorrection Multiple Rigids or RBE3s sharing nodes ALL ALL 0
    puts "[clock format [clock seconds] -format "%Y-%m-%d %H:%M:%S"] - going to change_cardimage_of_rigid_components"
    change_cardimage_of_rigid_components
}

proc unrealize_connectors {} {
    *clearmark connectors 1
    *createmark connectors 1 all
    *CE_Unrealize 1
    *clearmark connectors 1
}

proc move_include {new_name id x y z} {
    if { $x != 0 || $y != 0 || $z != 0 } {
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
    }

    *updateinclude $id 1 "$new_name" 0 0 0 0
    *clearmark nodes 1
    *clearmark connectors 1
}

proc create_include {name} {
    *createinclude 0 "$name" "$name" 0
}

proc correct_nodes {} {
    *createmark nodes 1 "by include" 0
    if {[hm_marklength nodes 1] > 0} {
        *findmark nodes 1 1 1 elements 0 2

        foreach include_id [hm_getincludes] {
            *clearmark nodes 2
            *clearmark elems 1
            *createmark elems 1 "by include" $include_id
            *markintersection elems 1 elems 2
            if {[hm_marklength elems 1] > 0} {
                *findmark elems 1 1 1 nodes 0 2
                *markintersection nodes 2 nodes 1
                *markmovetoinclude nodes 2 $include_id
            }

        }
    }

}

proc detach_includes {} {
    set include_list [hm_getincludes]
    foreach include_id $include_list {
        *setcurrentinclude $include_id ""
        puts $include_id
        set remaining_includes [lsearch -all -inline -not $include_list $include_id]

        #it is necessary to convert list to arguments and then evaluate it as cmd
        set cmd "*createmark nodes 1 \"by include\""
        foreach id $remaining_includes {
            append cmd " $id"
        }

        *createmark elems 1 "by include" $include_id
        puts [hm_marklength elems 1]
        eval $cmd
        puts $remaining_includes
        puts [hm_marklength nodes 1]
        if {[hm_marklength elems 1] > 0 &&  [hm_marklength nodes 1] > 0} {
            *detach_fromelements 1 nodes 1 0
            }
    }
}