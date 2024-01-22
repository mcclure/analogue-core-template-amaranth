#
# user core constraints
#
# put your clock groups in here as well as any net assignments
#

set_clock_groups -asynchronous \
 -group { bridge_spiclk } \
 -group { clk_74a } \
 -group { clk_74b } #\
# -group { ic|mp1|mf_pllbase_inst|altera_pll_i|general[0].gpll~PLL_OUTPUT_COUNTER|divclk } \
# -group { ic|mp1|mf_pllbase_inst|altera_pll_i|general[1].gpll~PLL_OUTPUT_COUNTER|divclk } \
# -group { ic|mp1|mf_pllbase_inst|altera_pll_i|general[2].gpll~PLL_OUTPUT_COUNTER|divclk } \
# -group { ic|mp1|mf_pllbase_inst|altera_pll_i|general[3].gpll~PLL_OUTPUT_COUNTER|divclk } 

#proc debug_andi_col2list { col } {
#   set list ""
#   foreach_in_collection c $col { lappend list [get_object_name $c] }
#   return $list
#}
#set debugAndi1 [open "debug_andi_1.txt" "w"]
#puts $debugAndi1 "TEST1234"
#puts $debugAndi1 [debug_andi_col2list [get_ports clk_74a]]
#close $debugAndi1

#create_generated_clock -divide_by 48 -duty_cycle 50 -master_clock [get_clocks clk_74a] -source core_top:ic|amaranth_core:ac|amaranth_core.video_clk_div:video_clk_div|clk_reg[0] -phase 0 -name vid_0
#create_generated_clock -divide_by 48 -duty_cycle 50 -master_clock [get_clocks clk_74a] -source core_top:ic|amaranth_core:ac|amaranth_core.video_clk_div:video_clk_div|clk_reg[15] -phase 90 -name vid_90
