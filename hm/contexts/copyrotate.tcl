########################################################################################
# This is a tcl script that interfaces w/ HM.                                          #
# This will allow the user to duplicate and rotate a set of elements multiple times.#
########################################################################################

itcl::class ::demo::CopyRotateCtx {
    inherit ::hm::context::HMScriptableBase
    constructor {args} {}

    #GUI methods
    public method proceed {args}
    public method ok {args}
    public method cancel {args}

    #setters
    public method setcoordoption {args}
    public method setrotdir {args}
    public method setelemdup {args}
    public method setrotmag {args}
    public method setnumrot {args}
    
    #internal methods
    private method coordsystem {args}
    private method rotdir {args}
    private method updateattributes {args}
    private method performrotation {rotation_dir coord_sys element_dup rot_mag num_rot}

    #variables
    private variable Priv;
}

itcl::body ::demo::CopyRotateCtx::constructor {args} {
    array set Priv {rotation_dir "X-axis" coord_sys "Global" num_rot "5" element_dup "Original" rot_mag "50"};
	eval itk_initialize $args
}

itcl::body ::demo::CopyRotateCtx::setcoordoption {args} {
    set Priv(coord_sys) $args
    coordsystem
}
itcl::body ::demo::CopyRotateCtx::setrotdir {args} {
	set Priv(rotation_dir) $args
    rotdir
}
itcl::body ::demo::CopyRotateCtx::setelemdup {args} {
    set Priv(element_dup) $args
}
itcl::body ::demo::CopyRotateCtx::setrotmag {args} {
    set Priv(rot_mag) $args
}
itcl::body ::demo::CopyRotateCtx::setnumrot {args} {
    set Priv(num_rot) $args
}

itcl::body ::demo::CopyRotateCtx::proceed {args} {
#Main Procedure
   global elems1
   
   #--------------------------------#
   # Get the element list to rotate #
   #--------------------------------#
   set elems1 [ctx::selection ids ElemSel]
   if { ! [ Null elems1 ] } {
	  ctx StartRecordHistory "Rotate Elements"
      performrotation $Priv(rotation_dir) $Priv(coord_sys) $Priv(element_dup) $Priv(rot_mag) $Priv(num_rot)
	  ctx EndRecordHistory "Rotate Elements"
   }
}

itcl::body ::demo::CopyRotateCtx::ok {args} {
    proceed
    ctx::manager exit
}

itcl::body ::demo::CopyRotateCtx::cancel {args} {
    ctx::manager exit
}

itcl::body ::demo::CopyRotateCtx::coordsystem {args} {
    if {$Priv(coord_sys) eq "Local" && $Priv(rotation_dir) != "Vector" && $Priv(rotation_dir) != "N1,N2,N3"} {
        updateattributes {syssel 1 vecsel 0 n1 0 n2 0 n3 0} 
        return
    }
    rotdir
}

itcl::body ::demo::CopyRotateCtx::updateattributes {args} {
    foreach {option value} {*}$args {
        ctx::ui set $option -visible $value
    }
}

itcl::body ::demo::CopyRotateCtx::rotdir {args} {
    if {$Priv(rotation_dir) eq "Vector"} {
        updateattributes {syssel 0 vecsel 1 n1 0 n2 0 n3 0} 
        return
    }
    if {$Priv(rotation_dir) eq "N1,N2,N3"} {
        updateattributes {syssel 0 vecsel 0 n1 1 n2 1 n3 1}
        return
    }
    if {$Priv(coord_sys) eq "Local"} {
        updateattributes {syssel 1 vecsel 0 n1 0 n2 0 n3 0}
        return
    }
    if {$Priv(coord_sys) eq "Global"} {
        updateattributes {syssel 0 vecsel 0 n1 0 n2 0 n3 0}
    }
}


itcl::body ::demo::CopyRotateCtx::performrotation {rotation_dir coord_sys element_dup rot_mag num_rot} {
   global elems1;
   
   #----------------------------------#
   #  Define the Rotation direction   #
   #----------------------------------#
   if {  [ Null Priv(num_rot) ] } {
      Message "Number of rotations not specified!"
      return;
   } elseif { [ Null Priv(rot_mag) ] } {
      Message "Rotation magnitude not specified!"
      return;
   }
   
   if { $Priv(coord_sys) == "Local" && $Priv(rotation_dir) != "Vector" && $Priv(rotation_dir) != "N1,N2,N3"} {
      set sys_id [ctx::selection ids SystemSel]
   }

   #----------------------#
   # Base Node Definition #
   #----------------------#
    set base [ctx::selection ids BaseNode]
   if { [ Null base ] } {
      set base_id 0;
   } else {
      set base_id $base;
   }
   set base_x [ hm_getvalue nodes id=$base_id dataname=globalx ];
   set base_y [ hm_getvalue nodes id=$base_id dataname=globaly ];
   set base_z [ hm_getvalue nodes id=$base_id dataname=globalz ];

   #---------------------------#
   # Create Rotation Planes... #
   #---------------------------#
   
   if {$Priv(rotation_dir) == "X-axis" && $Priv(coord_sys) == "Global"} {
   
    *createplane 1 1.0 0.0 0.0 $base_x $base_y $base_z
      
   } elseif {$Priv(rotation_dir) == "X-axis" && $Priv(coord_sys) == "Local"} {
   
    set new_xyz [ hm_xformvectoratpointtoglobal 1.0 0.0 0.0 $sys_id $base_id ];
    set new_x [ lindex $new_xyz 0 ];
    set new_y [ lindex $new_xyz 1 ];
    set new_z [ lindex $new_xyz 2 ];
	puts "*createplane 1 $new_x $new_y $new_z $base_x $base_y $base_z"
    *createplane 1 $new_x $new_y $new_z $base_x $base_y $base_z
   } elseif {$Priv(rotation_dir) == "Y-axis" && $Priv(coord_sys) == "Global"} {

    *createplane 1 0.0 1.0 0.0 $base_x $base_y $base_z

   } elseif {$Priv(rotation_dir) == "Y-axis" && $Priv(coord_sys) == "Local"} {

    set new_xyz [ hm_xformvectoratpointtoglobal 0.0 1.0 0.0 $sys_id $base_id ];
    set new_x [ lindex $new_xyz 0 ];
    set new_y [ lindex $new_xyz 1 ];
    set new_z [ lindex $new_xyz 2 ];
    *createplane 1 $new_x $new_y $new_z $base_x $base_y $base_z

   } elseif {$Priv(rotation_dir) == "Z-axis" && $Priv(coord_sys) == "Global"} {

    *createplane 1 0.0 0.0 1.0 $base_x $base_y $base_z

   } elseif {$Priv(rotation_dir) == "Z-axis" && $Priv(coord_sys) == "Local"} {

    set new_xyz [ hm_xformvectoratpointtoglobal 0.0 0.0 1.0 $sys_id $base_id ];
    set new_x [ lindex $new_xyz 0 ];
    set new_y [ lindex $new_xyz 1 ];
    set new_z [ lindex $new_xyz 2 ];
    puts "*createplane 1 $new_x $new_y $new_z $base_x $base_y $base_z"
    *createplane 1 $new_x $new_y $new_z $base_x $base_y $base_z


   } elseif {$Priv(rotation_dir) == "Vector"} {
      set v1 [ctx::selection ids VecSel]

      set vecx [ hm_getvalue vectors id=$v1 dataname=xcomp ]
      set vecy [ hm_getvalue vectors id=$v1 dataname=ycomp ]
      set vecz [ hm_getvalue vectors id=$v1 dataname=zcomp ]
      *createplane 1 $vecx $vecy $vecz $base_x $base_y $base_z

   } elseif {$Priv(rotation_dir) == "N1,N2,N3"} {
   
      set go "No";
      while {$go == "No"} {
         set n1 [ctx::selection ids N1]
         if {  [ Null n1 ] } {
            Message "N1 not selected."
         } else {
            set n1x [ hm_getvalue nodes id=$n1 dataname=globalx ]
            set n1y [ hm_getvalue nodes id=$n1 dataname=globaly ]
            set n1z [ hm_getvalue nodes id=$n1 dataname=globalz ]
            set go "Yes";
         }
      }
      
      set go "No";
      while {$go == "No"} {      
         set n2 [ctx::selection ids N2]
      
         if {  [ Null n2 ] } {
            Message "N2 not selected."
         } else {        
            set n2x [ hm_getvalue nodes id=$n2 dataname=globalx ]
            set n2y [ hm_getvalue nodes id=$n2 dataname=globaly ]
            set n2z [ hm_getvalue nodes id=$n2 dataname=globalz ]
            
            set go "Yes";
         }
      }
      
      set n3 [ctx::selection ids N3]
      set vec1x [expr $n2x - $n1x]
      set vec1y [expr $n2y - $n1y]
      set vec1z [expr $n2z - $n1z]
      
      if {  [ Null n3 ] } {
        *createplane 1 $vec1x $vec1y $vec1z $base_x $base_y $base_z
      } else {
         set n3x [ hm_getvalue nodes id=$n3 dataname=globalx ]
         set n3y [ hm_getvalue nodes id=$n3 dataname=globaly ]
         set n3z [ hm_getvalue nodes id=$n3 dataname=globalz ]

         set vec2x [expr $n3x - $n2x]
         set vec2y [expr $n3y - $n2y]
         set vec2z [expr $n3z - $n2z]
      
         set vecx [expr $vec1y*$vec2z - $vec1z*$vec2y]
         set vecy [expr $vec1z*$vec2x - $vec1x*$vec2z]
         set vecz [expr $vec1x*$vec2y - $vec1y*$vec2x]
      
       *createplane 1 $vecx $vecy $vecz $base_x $base_y $base_z
      }
   }
         
   for {set i 1} {$i <= $Priv(num_rot)} {incr i 1} {
      eval *createmark elems 1 $elems1
      if { $Priv(element_dup) == "Original"} {
         *duplicatemark elems 1 0
      } else {
         *duplicatemark elems 1 1
      }
      *createmarklast elems 1
	  *rotatemark elems 1 1 [expr $i*$Priv(rot_mag)];

      *clearmark elems 1
      set elems2 "";
   }
   
   *window 0 0 0 0 0;
   *plot;
}

ctx::manager register hm CopyRotateCtx "::demo::CopyRotateCtx"
