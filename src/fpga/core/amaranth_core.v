/* Generated by Amaranth Yosys 0.25 (PyPI ver 0.25.0.0.post77, git sha1 e02b7f64b) */

module amaranth_core(audio_dac, audio_lrck, audio_mclk, clk, cont1_joy, cont1_key, cont1_trig, cont2_joy, cont2_key, cont2_trig, cont3_joy, cont3_key, cont3_trig, cont4_joy, cont4_key, cont4_trig, dbg_rx, dbg_tx, init_done, rst, user1
, user2, video_de, video_hs, video_rgb, video_rgb_clk, video_rgb_clk90, video_skip, video_vs, audio_adc);
  reg \$auto$verilog_backend.cc:2083:dump_module$1  = 0;
  wire \$101 ;
  wire \$103 ;
  wire \$105 ;
  wire \$107 ;
  wire [2:0] \$109 ;
  wire \$11 ;
  wire [2:0] \$110 ;
  wire \$112 ;
  wire \$114 ;
  wire [8:0] \$116 ;
  wire [8:0] \$117 ;
  wire \$119 ;
  wire \$13 ;
  wire \$15 ;
  wire \$17 ;
  wire \$19 ;
  wire \$21 ;
  wire \$23 ;
  wire \$25 ;
  wire \$27 ;
  wire \$29 ;
  wire \$3 ;
  wire [10:0] \$31 ;
  wire [10:0] \$33 ;
  wire \$35 ;
  wire \$37 ;
  wire \$39 ;
  wire [7:0] \$41 ;
  wire [7:0] \$43 ;
  wire [7:0] \$45 ;
  wire [7:0] \$47 ;
  wire [7:0] \$49 ;
  wire \$5 ;
  wire [7:0] \$51 ;
  wire [7:0] \$53 ;
  wire [7:0] \$55 ;
  wire [7:0] \$57 ;
  wire [7:0] \$59 ;
  wire [7:0] \$61 ;
  wire [7:0] \$63 ;
  wire \$65 ;
  wire \$67 ;
  wire \$69 ;
  wire \$7 ;
  wire \$71 ;
  wire [10:0] \$73 ;
  wire [10:0] \$74 ;
  wire \$76 ;
  wire \$78 ;
  wire [10:0] \$80 ;
  wire [10:0] \$81 ;
  wire \$83 ;
  wire [22:0] \$85 ;
  wire [22:0] \$86 ;
  wire [23:0] \$88 ;
  wire [22:0] \$89 ;
  wire \$9 ;
  wire [23:0] \$91 ;
  wire \$93 ;
  wire \$95 ;
  wire \$97 ;
  wire \$99 ;
  reg [21:0] audgen_accum = 22'h0b5464;
  reg [21:0] \audgen_accum$next ;
  reg audgen_bit_update_stb;
  wire [3:0] audgen_channel_internal;
  wire audgen_channel_select;
  wire audgen_dac;
  wire audgen_lrck;
  reg [7:0] audgen_lrck_count = 8'h00;
  reg [7:0] \audgen_lrck_count$next ;
  wire [4:0] audgen_lrck_internal;
  reg audgen_mclk = 1'h0;
  reg \audgen_mclk$next ;
  wire audgen_mclk_stb;
  wire audgen_silenced;
  wire audgen_slck;
  reg [1:0] audgen_slck_count = 2'h3;
  reg [1:0] \audgen_slck_count$next ;
  reg audgen_slck_update = 1'h1;
  reg \audgen_slck_update$next ;
  reg audgen_word_update_stb;
  input audio_adc;
  wire audio_adc;
  output audio_dac;
  wire audio_dac;
  output audio_lrck;
  wire audio_lrck;
  output audio_mclk;
  wire audio_mclk;
  reg [1:0] blue_region = 2'h0;
  reg [1:0] \blue_region$next ;
  wire boot_clk;
  wire bottom_left_diag;
  input clk;
  wire clk;
  wire \clk$1 ;
  input [31:0] cont1_joy;
  wire [31:0] cont1_joy;
  input [31:0] cont1_key;
  wire [31:0] cont1_key;
  reg [31:0] cont1_key_latch = 32'd0;
  reg [31:0] \cont1_key_latch$next ;
  input [15:0] cont1_trig;
  wire [15:0] cont1_trig;
  input [31:0] cont2_joy;
  wire [31:0] cont2_joy;
  input [31:0] cont2_key;
  wire [31:0] cont2_key;
  input [15:0] cont2_trig;
  wire [15:0] cont2_trig;
  input [31:0] cont3_joy;
  wire [31:0] cont3_joy;
  input [31:0] cont3_key;
  wire [31:0] cont3_key;
  input [15:0] cont3_trig;
  wire [15:0] cont3_trig;
  input [31:0] cont4_joy;
  wire [31:0] cont4_joy;
  input [31:0] cont4_key;
  wire [31:0] cont4_key;
  input [15:0] cont4_trig;
  wire [15:0] cont4_trig;
  input dbg_rx;
  wire dbg_rx;
  input dbg_tx;
  wire dbg_tx;
  wire [1:0] green_region;
  output init_done;
  reg init_done = 1'h0;
  wire \init_done$next ;
  wire left_half;
  reg [1:0] red_region = 2'h0;
  reg [1:0] \red_region$next ;
  input rst;
  wire rst;
  wire \rst$2 ;
  wire top_half;
  wire top_left_diag;
  input user1;
  wire user1;
  input user2;
  wire user2;
  wire video_active;
  wire video_clk_div_clk;
  wire video_clk_div_clk90;
  wire video_clk_div_stb;
  output video_de;
  reg video_de = 1'h0;
  reg \video_de$next ;
  output video_hs;
  reg video_hs = 1'h0;
  reg \video_hs$next ;
  wire video_hsync_stb;
  output [23:0] video_rgb;
  reg [23:0] video_rgb = 24'h000000;
  reg [23:0] \video_rgb$next ;
  output video_rgb_clk;
  wire video_rgb_clk;
  output video_rgb_clk90;
  wire video_rgb_clk90;
  input video_skip;
  wire video_skip;
  output video_vs;
  reg video_vs = 1'h0;
  reg \video_vs$next ;
  wire video_vsync_stb;
  reg [9:0] video_x_count = 10'h000;
  reg [9:0] \video_x_count$next ;
  reg [9:0] video_y_count = 10'h000;
  reg [9:0] \video_y_count$next ;
  assign \$9  = video_clk_div_stb & \$7 ;
  assign \$99  = ~ audgen_mclk;
  assign \$101  = audgen_mclk_stb & \$99 ;
  assign \$103  = audgen_slck_count == 2'h2;
  assign \$105  = ~ audgen_mclk;
  assign \$107  = audgen_mclk_stb & \$105 ;
  assign \$110  = audgen_slck_count + 1'h1;
  assign \$112  = ~ audgen_mclk;
  assign \$114  = audgen_mclk_stb & \$112 ;
  assign \$117  = audgen_lrck_count + 1'h1;
  assign \$11  = video_y_count == 9'h15c;
  assign \$119  = audgen_lrck_internal == 5'h17;
  always @(posedge boot_clk)
    init_done <= 1'h1;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) red_region <= 2'h0;
    else red_region <= \red_region$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) blue_region <= 2'h0;
    else blue_region <= \blue_region$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) cont1_key_latch <= 32'd0;
    else cont1_key_latch <= \cont1_key_latch$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_rgb <= 24'h000000;
    else video_rgb <= \video_rgb$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_vs <= 1'h0;
    else video_vs <= \video_vs$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_hs <= 1'h0;
    else video_hs <= \video_hs$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_x_count <= 10'h000;
    else video_x_count <= \video_x_count$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_y_count <= 10'h000;
    else video_y_count <= \video_y_count$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) video_de <= 1'h0;
    else video_de <= \video_de$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) audgen_accum <= 22'h0b5464;
    else audgen_accum <= \audgen_accum$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) audgen_mclk <= 1'h0;
    else audgen_mclk <= \audgen_mclk$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) audgen_slck_update <= 1'h1;
    else audgen_slck_update <= \audgen_slck_update$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) audgen_slck_count <= 2'h3;
    else audgen_slck_count <= \audgen_slck_count$next ;
  always @(posedge \clk$1 , posedge \rst$2 )
    if (\rst$2 ) audgen_lrck_count <= 8'h00;
    else audgen_lrck_count <= \audgen_lrck_count$next ;
  assign \$13  = \$9  & \$11 ;
  assign \$15  = video_x_count >= 3'h4;
  assign \$17  = video_x_count < 9'h194;
  assign \$19  = \$15  & \$17 ;
  assign \$21  = video_y_count >= 5'h1d;
  assign \$23  = \$19  & \$21 ;
  assign \$25  = video_y_count < 9'h15d;
  assign \$27  = \$23  & \$25 ;
  assign \$29  = video_x_count < video_y_count;
  assign \$31  = + video_x_count;
  assign \$33  = 9'h13f - video_y_count;
  assign \$35  = $signed(\$31 ) < $signed(\$33 );
  assign \$37  = video_x_count < 8'hc8;
  assign \$3  = video_x_count == 9'h194;
  assign \$39  = video_y_count < 8'ha0;
  assign \$41  = + cont1_key_latch[0];
  assign \$43  = + cont1_key_latch[1];
  assign \$45  = + cont1_key_latch[2];
  assign \$47  = + cont1_key_latch[3];
  assign \$49  = + cont1_key_latch[4];
  assign \$51  = + cont1_key_latch[5];
  assign \$53  = + cont1_key_latch[6];
  assign \$55  = + cont1_key_latch[7];
  assign \$57  = + cont1_key_latch[8];
  assign \$5  = video_clk_div_stb & \$3 ;
  assign \$59  = + cont1_key_latch[9];
  assign \$61  = + cont1_key_latch[14];
  assign \$63  = + cont1_key_latch[15];
  assign \$65  = ! video_x_count;
  assign \$67  = ! video_y_count;
  assign \$69  = \$65  & \$67 ;
  assign \$71  = video_x_count == 2'h3;
  assign \$74  = video_x_count + 1'h1;
  assign \$76  = video_x_count == 9'h197;
  assign \$78  = video_x_count == 9'h197;
  assign \$7  = video_x_count == 9'h195;
  assign \$81  = video_y_count + 1'h1;
  assign \$83  = video_y_count == 9'h17a;
  assign \$86  = audgen_accum + 22'h03c000;
  assign \$89  = audgen_accum - 22'h0b5464;
  assign \$91  = $signed(\$89 ) + $signed(23'h03c000);
  assign \$93  = audgen_accum >= 22'h0b5464;
  assign \$95  = ~ audgen_mclk;
  assign \$97  = ~ audgen_slck_count[1];
  \amaranth_core.video_clk_div  video_clk_div (
    .clk(\clk$1 ),
    .\clk$1 (video_clk_div_clk),
    .clk90(video_clk_div_clk90),
    .rst(\rst$2 ),
    .stb(video_clk_div_stb)
  );
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \red_region$next  = red_region;
    casez (video_clk_div_stb)
      1'h1:
        begin
          (* full_case = 32'd1 *)
          casez (bottom_left_diag)
            1'h1:
                (* full_case = 32'd1 *)
                casez (top_left_diag)
                endcase
            default:
                (* full_case = 32'd1 *)
                casez (top_left_diag)
                endcase
          endcase
          (* full_case = 32'd1 *)
          casez (left_half)
            1'h1:
                (* full_case = 32'd1 *)
                casez (top_half)
                  1'h1:
                      \red_region$next  = 2'h0;
                  default:
                      \red_region$next  = 2'h2;
                endcase
            default:
                (* full_case = 32'd1 *)
                casez (top_half)
                  1'h1:
                      \red_region$next  = 2'h1;
                  default:
                      \red_region$next  = 2'h3;
                endcase
          endcase
        end
    endcase
    casez (\rst$2 )
      1'h1:
          \red_region$next  = 2'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \blue_region$next  = blue_region;
    casez (video_clk_div_stb)
      1'h1:
          (* full_case = 32'd1 *)
          casez (bottom_left_diag)
            1'h1:
                (* full_case = 32'd1 *)
                casez (top_left_diag)
                  1'h1:
                      \blue_region$next  = 2'h1;
                  default:
                      \blue_region$next  = 2'h2;
                endcase
            default:
                (* full_case = 32'd1 *)
                casez (top_left_diag)
                  1'h1:
                      \blue_region$next  = 2'h0;
                  default:
                      \blue_region$next  = 2'h3;
                endcase
          endcase
    endcase
    casez (\rst$2 )
      1'h1:
          \blue_region$next  = 2'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \cont1_key_latch$next  = cont1_key_latch;
    casez (video_vsync_stb)
      1'h1:
          \cont1_key_latch$next  = cont1_key;
    endcase
    casez (\rst$2 )
      1'h1:
          \cont1_key_latch$next  = 32'd0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_rgb$next  = video_rgb;
    casez (video_clk_div_stb)
      1'h1:
        begin
          \video_rgb$next  = 24'h000000;
          casez (video_active)
            1'h1:
              begin
                (* full_case = 32'd1 *)
                casez (red_region)
                  2'h0:
                      \video_rgb$next [23:16] = \$41 ;
                  2'h2:
                      \video_rgb$next [23:16] = \$43 ;
                  2'h1:
                      \video_rgb$next [23:16] = \$45 ;
                  2'h3:
                      \video_rgb$next [23:16] = \$47 ;
                endcase
                (* full_case = 32'd1 *)
                casez (blue_region)
                  2'h3:
                      \video_rgb$next [7:0] = \$49 ;
                  2'h2:
                      \video_rgb$next [7:0] = \$51 ;
                  2'h0:
                      \video_rgb$next [7:0] = \$53 ;
                  2'h1:
                      \video_rgb$next [7:0] = \$55 ;
                endcase
                (* full_case = 32'd1 *)
                casez (green_region)
                  2'h0:
                      \video_rgb$next [15:8] = \$57 ;
                  2'h1:
                      \video_rgb$next [15:8] = \$59 ;
                  2'h2:
                      \video_rgb$next [15:8] = \$61 ;
                  2'h3:
                      \video_rgb$next [15:8] = \$63 ;
                endcase
              end
          endcase
        end
    endcase
    casez (\rst$2 )
      1'h1:
          \video_rgb$next  = 24'h000000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_vs$next  = video_vs;
    casez (video_clk_div_stb)
      1'h1:
          \video_vs$next  = \$69 ;
    endcase
    casez (\rst$2 )
      1'h1:
          \video_vs$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_hs$next  = video_hs;
    casez (video_clk_div_stb)
      1'h1:
          \video_hs$next  = \$71 ;
    endcase
    casez (\rst$2 )
      1'h1:
          \video_hs$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_x_count$next  = video_x_count;
    casez (video_clk_div_stb)
      1'h1:
        begin
          \video_x_count$next  = \$74 [9:0];
          casez (\$76 )
            1'h1:
                \video_x_count$next  = 10'h000;
          endcase
        end
    endcase
    casez (\rst$2 )
      1'h1:
          \video_x_count$next  = 10'h000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_y_count$next  = video_y_count;
    casez (video_clk_div_stb)
      1'h1:
          casez (\$78 )
            1'h1:
              begin
                \video_y_count$next  = \$81 [9:0];
                casez (\$83 )
                  1'h1:
                      \video_y_count$next  = 10'h000;
                endcase
              end
          endcase
    endcase
    casez (\rst$2 )
      1'h1:
          \video_y_count$next  = 10'h000;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \video_de$next  = video_de;
    casez (video_clk_div_stb)
      1'h1:
          \video_de$next  = video_active;
    endcase
    casez (\rst$2 )
      1'h1:
          \video_de$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \audgen_accum$next  = \$86 [21:0];
    casez (audgen_mclk_stb)
      1'h1:
          \audgen_accum$next  = \$91 [21:0];
    endcase
    casez (\rst$2 )
      1'h1:
          \audgen_accum$next  = 22'h0b5464;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \audgen_mclk$next  = audgen_mclk;
    casez (audgen_mclk_stb)
      1'h1:
          \audgen_mclk$next  = \$95 ;
    endcase
    casez (\rst$2 )
      1'h1:
          \audgen_mclk$next  = 1'h0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \audgen_slck_update$next  = 1'h0;
    casez (\$101 )
      1'h1:
          casez (\$103 )
            1'h1:
                \audgen_slck_update$next  = 1'h1;
          endcase
    endcase
    casez (\rst$2 )
      1'h1:
          \audgen_slck_update$next  = 1'h1;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \audgen_slck_count$next  = audgen_slck_count;
    casez (\$107 )
      1'h1:
          \audgen_slck_count$next  = \$110 [1:0];
    endcase
    casez (\rst$2 )
      1'h1:
          \audgen_slck_count$next  = 2'h3;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    \audgen_lrck_count$next  = audgen_lrck_count;
    casez (\$114 )
      1'h1:
          \audgen_lrck_count$next  = \$117 [7:0];
    endcase
    casez (\rst$2 )
      1'h1:
          \audgen_lrck_count$next  = 8'h00;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    audgen_word_update_stb = 1'h0;
    casez (audgen_slck_update)
      1'h1:
          casez (\$119 )
            1'h1:
                audgen_word_update_stb = 1'h1;
          endcase
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$1 ) begin end
    audgen_bit_update_stb = 1'h0;
    casez (audgen_slck_update)
      1'h1:
          audgen_bit_update_stb = 1'h1;
    endcase
  end
  assign \$73  = \$74 ;
  assign \$80  = \$81 ;
  assign \$85  = \$86 ;
  assign \$88  = \$91 ;
  assign \$109  = \$110 ;
  assign \$116  = \$117 ;
  assign green_region = 2'h0;
  assign audio_lrck = audgen_lrck;
  assign audio_dac = audgen_dac;
  assign audio_mclk = audgen_mclk;
  assign audgen_lrck_internal = audgen_lrck_count[6:2];
  assign audgen_silenced = audgen_lrck_count[6];
  assign audgen_channel_internal = audgen_lrck_count[5:2];
  assign audgen_channel_select = audgen_lrck;
  assign audgen_lrck = audgen_lrck_count[7];
  assign audgen_slck = \$97 ;
  assign audgen_mclk_stb = \$93 ;
  assign audgen_dac = 1'h0;
  assign top_half = \$39 ;
  assign left_half = \$37 ;
  assign top_left_diag = \$35 ;
  assign bottom_left_diag = \$29 ;
  assign video_active = \$27 ;
  assign video_vsync_stb = \$13 ;
  assign video_hsync_stb = \$5 ;
  assign video_rgb_clk90 = video_clk_div_clk90;
  assign video_rgb_clk = video_clk_div_clk;
  assign \init_done$next  = 1'h1;
  assign \rst$2  = rst;
  assign \clk$1  = clk;
  assign boot_clk = clk;
endmodule

module \amaranth_core.video_clk_div (rst, \clk$1 , clk90, stb, clk);
  reg \$auto$verilog_backend.cc:2083:dump_module$2  = 0;
  input clk;
  wire clk;
  output \clk$1 ;
  wire \clk$1 ;
  output clk90;
  wire clk90;
  reg [7:0] clk_reg = 8'hf0;
  reg [7:0] \clk_reg$next ;
  input rst;
  wire rst;
  output stb;
  wire stb;
  reg [7:0] stb_reg = 8'h01;
  reg [7:0] \stb_reg$next ;
  always @(posedge clk, posedge rst)
    if (rst) clk_reg <= 8'hf0;
    else clk_reg <= \clk_reg$next ;
  always @(posedge clk, posedge rst)
    if (rst) stb_reg <= 8'h01;
    else stb_reg <= \stb_reg$next ;
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$2 ) begin end
    \clk_reg$next  = { clk_reg[6:0], clk_reg[7] };
    casez (rst)
      1'h1:
          \clk_reg$next  = 8'hf0;
    endcase
  end
  always @* begin
    if (\$auto$verilog_backend.cc:2083:dump_module$2 ) begin end
    \stb_reg$next  = { stb_reg[6:0], stb_reg[7] };
    casez (rst)
      1'h1:
          \stb_reg$next  = 8'h01;
    endcase
  end
  assign stb = stb_reg[0];
  assign clk90 = clk_reg[2];
  assign \clk$1  = clk_reg[0];
endmodule
