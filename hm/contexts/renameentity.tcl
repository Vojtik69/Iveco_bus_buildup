########################################################################################
# This is a tcl script that interfaces w/ HM.                                          #
# This will allow the user to prefix several selected entities
########################################################################################

itcl::class ::demo::RenameEntityCtx {
    inherit ::hm::context::HMScriptableBase
    constructor {args} {}

    public method proceed {args};
	
    protected method OnSelectionChange {args};
}

itcl::body ::demo::RenameEntityCtx::constructor {args} {
    ctx SetOption entityprefix "rev1_"
    eval itk_initialize $args;
}

itcl::body ::demo::RenameEntityCtx::proceed {args} {
    set prefix [ctx GetOption entityprefix]
    set entityType [ctx::selection get compSelector -type]
    set count [ctx::selection count compSelector]
	ctx StartRecordHistory "Renamed $count entities"
    foreach id [ctx::selection ids compSelector] {
        set oldName [hm_getvalue $entityType id=$id dataname=name]
        set newName ${prefix}$oldName
        *setvalue $entityType id=$id name=$newName
    }
	ctx EndRecordHistory "Renamed $count entities"
	ctx::selection clear compSelector
}

itcl::body ::demo::RenameEntityCtx::OnSelectionChange {args} {
    if {[dict getifexists {*}$args count]} {
         ctx::ui set prefix_md_label -label "Prefix"
         ctx::ui post prefix_md;
    } else {
         ctx::ui unpost prefix_md;
    }
}

ctx::manager register hm RenameEntityCtx "::demo::RenameEntityCtx"
