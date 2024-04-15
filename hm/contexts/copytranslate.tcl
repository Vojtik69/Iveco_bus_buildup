########################################################################################
# This is a tcl script that interfaces w/ HM.                                          #
# This will allow the user to duplicate and translate a set of elements multiple times.#
########################################################################################
itcl::class ::demo::CopyTranslateCtx {
    inherit ::hm::context::HMScriptableBase
    constructor {args} {}
	
    public method proceed {args}
    public method ok {}
    public method cancel {}
	
    public method onpost {args}
    public method settrans {type}
    public method updateguidebar {}
    public method updateselectors {active args}
    public method performtranslation { translation_dir coord_sys element_dup trans num_trans }

    protected method OnSelectionChange {args}
}

#======================================================================================================================
itcl::body ::demo::CopyTranslateCtx::constructor {args} {
    #set five options to default values to be used later
    array set options {coordsys Global transdir X-axis transmag 10 transnum 5 elemdup Original}
    foreach {option value} [array get options] { ctx SetOption $option $value }
	eval itk_initialize $args
}

#======================================================================================================================
itcl::body ::demo::CopyTranslateCtx::onpost {args} {
    #methods in the base class: HMScriptableBase
    ShowNamedCursor cursorElements
    ctx WorkflowHelp "Source"
}

#======================================================================================================================
itcl::body ::demo::CopyTranslateCtx::OnSelectionChange {args} {
    ctx SetOption "coordsys" Global
    #post micro-dialog when elements have been selected.
    if {[ctx::selection count ElemSel]} {
        ctx::ui post trans_options_microd
        ctx WorkflowHelp "Target"
    } else { 
        ctx::ui unpost trans_options_microd
        ctx WorkflowHelp "Source"
    }
    #if nodes and system has been selected, set the coordinate system to Local
    if {[ctx::selection count SystemSel] && [ctx::selection count BaseNode]} {
        ctx SetOption "coordsys" Local
    }
}

ctx::manager register hm CopyTranslateCtx "::demo::CopyTranslateCtx"
#======================================================================================================================
itcl::body ::demo::CopyTranslateCtx::settrans {type} {
    ctx SetOption "transdir" $type
    #update the chooser in the GUI to the selected-type
    ctx::ui set trans_dir_chooser -label $type
    updateguidebar
}

itcl::body ::demo::CopyTranslateCtx::updateguidebar {} {
    switch [ctx GetOption transdir] {
        "Vector" { updateselectors "VecSel" {
            syssel 0 nodesel 0 vecsel 1 dirsel 0 }
            ctx ShowNamedCursor cursorVectors
        }
        "Direction" {
            updateselectors "Direction" {syssel 0 nodesel 0 vecsel 0 dirsel 1} 
        }
        "X-axis" -
        "Y-axis" -
        "Z-axis" {
            updateselectors "" {syssel 1 nodesel 1 vecsel 0 dirsel 0 }
            ctx ShowNamedCursor cursorSelect
        }
    }
}

itcl::body ::demo::CopyTranslateCtx::updateselectors {active args} {
    foreach {option value} {*}$args { 
        ctx::ui set $option -visible $value
    }
    if {$active ne ""} {
        [ctx GetNamedHMSelection "$active"] SetActive true
    }
}

itcl::body ::demo::CopyTranslateCtx::performtranslation { translation_dir coord_sys element_dup trans num_trans } {
   global elems1;
   
   #----------------------------------#
   # Define the Translation direction #
   #----------------------------------#
   if {  [ Null num_trans ] } {
      Message "Number of translations not specified!"
      return;
   } elseif { [ Null trans ] } {
      Message "Translation magnitude not specified!"
      return;
   }
   
   if { $coord_sys == "Local" && $translation_dir != "Vector" && $translation_dir != "Direction"} {
      set sys_id [ctx::selection ids SystemSel]
      set base [ctx::selection ids BaseNode]
      if {  [ Null base ] } {
         set base_id 0;
      } else {
         set base_id $base;
      }
   }

   if {$translation_dir == "X-axis"} {
      *createvector 1 1.0 0.0 0.0
   } elseif {$translation_dir == "Y-axis"} {
      *createvector 1 0.0 1.0 0.0
   } elseif {$translation_dir == "Z-axis"} {
      *createvector 1 0.0 0.0 1.0
   } elseif {$translation_dir == "Vector"} {
      set v1 [ctx::selection ids VecSel]
      set vecx [ hm_getvalue vectors id=$v1 dataname=xcomp ]
      set vecy [ hm_getvalue vectors id=$v1 dataname=ycomp ]
      set vecz [ hm_getvalue vectors id=$v1 dataname=zcomp ]
      *createvector 1 $vecx $vecy $vecz
   } elseif {$translation_dir == "Direction"} {
         set dir [[ctx GetNamedHMSelection "Direction"] GetPlaneBaseandAxis]
         *createvector 1 [lindex $dir 3] [lindex $dir 4] [lindex $dir 5]
   }

   for {set i 1} {$i <= $num_trans} {incr i 1} {
      eval *createmark elems 1 $elems1

      if { $element_dup == "Original" } {
         *duplicatemark elems 1 0
      } else {
         *duplicatemark elems 1 1
      }

      *createmarklast elems 1
      if { $coord_sys == "Global" || $translation_dir == "Vector" || $translation_dir == "Direction"} {
         *translatemark elems 1 1 [expr $i*$trans];
      } else {
         *translatemarkwithsystem elems 1 1 [expr $i*$trans] $sys_id $base_id;
      }
      *clearmark elems 1
      set elems2 "";
   }
   
   *window 0 0 0 0 0;
   *plot;
}

itcl::body ::demo::CopyTranslateCtx::cancel {} {
    ctx::manager exit
}

itcl::body ::demo::CopyTranslateCtx::proceed {args} {
   #Main Procedure
   global elems1;
   
   #-----------------------------------#
   # Get the element list to translate #
   #-----------------------------------#
   
   set elems1 [ctx::selection ids ElemSel]
   
   if { ! [ Null elems1 ] } {
        ctx StartRecordHistory "Translate Elements"
        performtranslation [ctx GetOption transdir] [ctx GetOption coordsys] [ctx GetOption elemdup] [ctx GetOption transmag] [ctx GetOption transnum]
        ctx EndRecordHistory "Translate Elements"
		ctx WorkflowHelp "Source"
   }
   ctx::selection clear "VecSel"
   ctx::selection clear "Direction"
   ctx::selection clear "ElemSel"
   ctx::selection clear "BaseNode"
   ctx::selection clear "SystemSel"
}

itcl::body ::demo::CopyTranslateCtx::ok {} {
    proceed
    ctx::manager exit
}
