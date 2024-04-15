########################################################################################
# This is a tcl script that interfaces w/ HM.                                          #
########################################################################################

itcl::class ::demo::SolidCentroidCtx {
    inherit ::hm::context::HMScriptableBase
    constructor {args} {}

    public method proceed {args};
    public method ok {args};
}

itcl::body ::demo::SolidCentroidCtx::proceed {args} {
	
	set solidIdList [ ctx::selection ids "SolidSel" ]

	::ExtensionDemoHM::NodeatCentroid $solidIdList
	
	ctx::selection clear "SolidSel"

}

proc ::ExtensionDemoHM::NodeatCentroid { solidIdList } {
	
	::ExtensionDemoHM::Graphics 0

	foreach solid $solidIdList {
		
		*createmark solids 1 $solid
		set centroid [ hm_getcentroid solids 1 ]
		puts $centroid
		eval *createnode $centroid 0 0 0
		*clearmark solids 1
	}
	
	::ExtensionDemoHM::Graphics 1
}

itcl::body ::demo::SolidCentroidCtx::ok {} {
    proceed
    ctx exit
}

ctx::manager register hm SolidCentroidCtx "::demo::SolidCentroidCtx"
