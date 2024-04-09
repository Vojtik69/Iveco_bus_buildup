########################################################################################
# This is a tcl script that interfaces w/ HM.                                          #
########################################################################################

itcl::class ::demo::Coord3toCoord1Ctx {
    inherit ::hm::context::HMScriptableBase
    constructor {args} {}

    public method proceed {args};
    public method ok {args};
}

itcl::body ::demo::Coord3toCoord1Ctx::proceed {args} {
    set cord3r_list [::CustomerName::GetAllCord3]
    ::CustomerName::CycleSystems $cord3r_list
    #Messaging
    if { [llength $cord3r_list] != 0 } {
        tk_messageBox -parent . -type ok -title "What happened?" \
        -message "$cord3r_list: converted to CORD1R"
    } else {
        tk_messageBox -parent . -type ok -title "What happened?" \
        -message "There are no CORD3R systems in this model"
    }
	
	ctx::selection clear "SystemSel"
}

itcl::body ::demo::Coord3toCoord1Ctx::ok {args} {
    ctx::manager exit
}

namespace eval CustomerName {} {

#Get the systems and find the CORD3R systems.
proc ::CustomerName::GetAllCord3 {} {
    #*createmarkpanel systems 1 "Select Systems"
    set cord3_sys []
#    set all_systems [hm_getmark systems 1]
    set all_systems [ctx::selection ids SystemSel]
    
    #If the system is a CORD3R, mark it.
    foreach s $all_systems {
        if { [hm_getvalue systems id=$s dataname=definitioncode] == 1 } {
            lappend cord3_sys $s
        }
    }
    return $cord3_sys
#    *clearmarkall 1
}

#Cycle through the CORD3R systems and grab the Gs and ref/disp nodes.
proc ::CustomerName::CycleSystems {cord3_list} {
    if { [llength $cord3_list] == 0 } {
        return 0
    }
    foreach c $cord3_list {
        #Get G1, G2 and G3 for the CORD3R
        set c3_g1 [hm_getvalue systems id=$c dataname=originnodeid]
        set c3_g2 [hm_getvalue systems id=$c dataname=axisnodeid]
        set c3_g3 [hm_getvalue systems id=$c dataname=planenodeid]
        
        #If there's assignment, assign the old nodes to the new system
        set new_sys [::CustomerName::CreateNew $c3_g1 $c3_g2 $c]
        *createmark nodes 1 "equal to value" inputsystemid $c
        set ref_nodes [hm_getmark nodes 1]
        if { [llength $ref_nodes] != 0 } {
            ::CustomerName::AssignRef $ref_nodes $new_sys
        }
        *createmark nodes 2 "equal to value" outputsystemid $c
        set disp_nodes [hm_getmark nodes 2]
        if { [llength $disp_nodes] != 0 } {
            ::CustomerName::AssignDisp $disp_nodes $new_sys
        }
        #Any element MCIDs?
        hm_getcrossreferencedentities systs $c 4 1 0 0 -byid
        set mcid_elems [hm_getmark elems 1]
        *clearmarkall 1
        if { [llength $mcid_elems] != 0 } {
            ::CustomerName::AssignMCID $mcid_elems $new_sys
        }
        #Delete the old system
        hm_createmark systems 1 $c
        *deletemark systems 1
        #Renumber to old IDs
        hm_createmark systems 1 $new_sys
        *renumbersolverid systems 1 $c 1 0 0 0 0 0
    }
	*clearmarkall 1
	*clearmarkall 2
}
#Create a new CORD1R given two nodes of a CORD3R
proc ::CustomerName::CreateNew {g1 g2 c} {
    *createmark nodes 1 $g1
    *duplicatemark nodes 1 
    set new_g2 [hm_getmark nodes 1]
    *createvector 1 0 0 1 
    *translatemarkwithsystem nodes 1 1 1 $c $g1 
    *systemcreate3nodes 0 $g1 "z-axis" $new_g2 "xz-plane" $g2
    *clearmarkall 1
    return [hm_latestentityid systems]
}
#If there are ref nodes, this will be called and the nodes from the CORD3R will be assigned to the CORD1R
proc ::CustomerName::AssignRef {ref c} {
    hm_createmark nodes 1 $ref
    *systemsetreference nodes 1 $c
	*clearmarkall 1
}
#Same for disp.
proc ::CustomerName::AssignDisp {disp c} {
    hm_createmark nodes 1 $disp
    *systemsetanalysis nodes 1 $c
	*clearmarkall 1
}
#Assign MCID
proc ::CustomerName::AssignMCID {elems c} {
    foreach el $elems {
        *attributeupdateentity elements $el 3045 1 2 0 systems $c
    }
}
}
#::CustomerName::Main

ctx::manager register hm Coord3toCoord1Ctx "::demo::Coord3toCoord1Ctx"

