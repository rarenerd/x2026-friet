// Friet met Desire — KOALA demo: warm dragon bitmap (top) + bouncing sprite
// ornaments + a RASTER-SPLIT text bar (bottom 3 rows) running the synced
// lyric ticker. Music on V-blank, border + sprite-launch on the kick.
//
// VIC bank 1 ($4000-$7FFF) memory map:
//   $1000  SID body              $4400 cube sprites (ptrs 16..47)
//   $4C00  text screen (ptr 3)   $5000 RAM font (charbase 2)
//   $5C00  bitmap colour screen + $5FF8 sprite pointers
//   $6000  bitmap   $7F40 screen src   $8328 colour src   $8710 bg   $8720 lyrics
//
// Split: lines 51..224 = multicolor bitmap, 225..250 = hires text (rows 22-24).

.const SID_INIT = $1000
.const SID_PLAY = $1003
.var gate_prev = $90
.var beatc     = $91
.var frame_lo  = $92
.var frame_hi  = $93
.var ly_lo     = $94
.var ly_hi     = $95
.var tmp_len   = $96
.var tmp_col   = $97
.var src       = $a0      // font-copy source ptr
.var dst       = $a2      // font-copy dest ptr
.var spinbase  = $99      // cube rotation phase
.var tmpx      = $98
.var tmpy      = $9a
.var scidx     = $9b      // scene index for the song-structure escalation arc
.var colcyc    = $9c      // cube-colour rave-cycle phase (advances on every kick)
.var msbacc    = $9e      // accumulates the per-sprite X-MSB bits for $D010
.const DRIFTSTEP = 12     // precession speed (16-bit add/frame; lower = gentler)
.const NSPR  = 8        // all 8 hardware sprites = 8 flying cubes
.const CUBE_FRAMES = 32   // rotation frames in sprite_cube.bin (must be power of 2)
.const CUBE_MASK   = CUBE_FRAMES-1
.const CUBE_PTR    = 16   // first cube frame = sprite pointer 16 ($4400)
.const SPLIT = 225        // raster line: switch to text mode
.const TOPL  = 251        // raster line: switch to bitmap + run the frame

*=$0801
    .byte $0B,$08,$0A,$00,$9E
    .text "2064"
    .byte $00,$00,$00

*=$0810
entry:
    sei
    lda #0
    ldx #$0d
!zp:
    sta $02,x
    dex
    bpl !zp-
    sta gate_prev
    sta beatc
    sta frame_lo
    sta frame_hi
    sta scidx
    sta colcyc
    lda #<lyric_table
    sta ly_lo
    lda #>lyric_table
    sta ly_hi

    // ---- copy char ROM (uppercase $D000-$D7FF) -> RAM font $5000 -------
    lda $01
    pha
    lda #$33                 // char ROM visible at $D000, I/O hidden
    sta $01
    lda #<$D800              // lowercase/mixed charset (matches lyric screencodes)
    sta src
    lda #>$D800
    sta src+1
    lda #<$5000
    sta dst
    lda #>$5000
    sta dst+1
    ldx #8                   // 8 pages = 2KB
!fp:
    ldy #0
!fb:
    lda (src),y
    sta (dst),y
    iny
    bne !fb-
    inc src+1
    inc dst+1
    dex
    bne !fp-
    pla
    sta $01                  // restore I/O

    // ---- copy koala screen ($7F40)->$5C00, colour ($8328)->$D800 ------
    ldx #0
!cp:
    lda koala_screen,x
    sta $5C00,x
    lda koala_screen+$100,x
    sta $5D00,x
    lda koala_screen+$200,x
    sta $5E00,x
    lda koala_screen+$300,x
    sta $5F00,x
    lda koala_color,x
    sta $D800,x
    lda koala_color+$100,x
    sta $D900,x
    lda koala_color+$200,x
    sta $DA00,x
    lda koala_color+$300,x
    sta $DB00,x
    inx
    bne !cp-

    // sprite pointers -> $4400 (ptr 16); text screen cleared to spaces.
    // Mirror to BOTH screens' pointer slots: a sprite that dips below the
    // raster split is displayed while $D018=$34 (text screen $4C00), so its
    // pointer is fetched from $4FF8 — without the mirror it reads garbage.
    lda #16
    ldx #7
!sp:
    sta $5FF8,x                  // bitmap-screen pointers ($5C00, above split)
    sta $4FF8,x                  // text-screen pointers   ($4C00, below split)
    dex
    bpl !sp-
    lda #$20                 // clear visible text rows 22..24 to spaces
    ldx #119
!ct:
    sta $4C00+22*40,x
    lda #$01                 // WHITE text on (soon) black -> clean, not MinVWS-grey
    sta $D800+22*40,x
    lda #$20
    dex
    bpl !ct-

    // VIC bank 1
    lda $DD00
    and #$FC
    ora #$02
    sta $DD00

    // sprites: fixed X, colours, init bounce
    ldx #NSPR-1
!si:
    lda sprcol,x
    sta $D027,x
    dex
    bpl !si-
    lda #$00
    sta $D010                // orbit x stays < 256, no X-MSB needed
    sta $D01C                // hires sprites
    sta $D01B                // sprites in front
    lda #$FF
    sta $D015                // enable all 8 sprites
    lda #$00
    sta $D017                // normal size (2x stretch is reserved for the
    sta $D01D                // climax escalation)

    // bitmap colours
    lda koala_bg
    sta $D021
    lda #$00
    sta $D020

    // SID init
    lda #0
    tax
    tay
    jsr SID_INIT

    // raster IRQ
    lda #<irq_top
    sta $0314
    lda #>irq_top
    sta $0315
    lda #$7F
    sta $DC0D
    sta $DD0D
    lda $DC0D
    lda $DD0D
    lda #$01
    sta $D01A
    lda #TOPL
    sta $D012
    lda $D011
    and #$7F
    sta $D011
    cli
!fe:
    jmp !fe-

// ---- TOP IRQ (line 251): bitmap mode + run the frame ------------------
irq_top:
    lda #$FF
    sta $D019
    lda #$3B                 // bitmap mode on
    sta $D011
    lda #$18                 // multicolor on
    sta $D016
    lda #$78                 // bitmap colour screen $5C00, bitmap data $6000
    sta $D018
    lda koala_bg             // bitmap region keeps its background...
    sta $D021
    jsr SID_PLAY
    jsr fly
    jsr spin
    jsr tick_scene
    jsr lyric_tick
    // kick detect -> border cycle + sprite re-launch
    lda $D412
    and #$10
    tax
    cmp gate_prev
    stx gate_prev
    beq !nob+
    txa
    beq !nob+
    inc beatc
    lda beatc
    and #$03
    tay
    lda bordtab,y
    sta $D020
    jsr flash_cubes          // rave-pulse the 8 cube colours on the kick
!nob:
    inc frame_lo
    bne !nf+
    inc frame_hi
!nf:
    lda #SPLIT
    sta $D012
    lda #<irq_split
    sta $0314
    lda #>irq_split
    sta $0315
    jmp $EA81

// ---- SPLIT IRQ (line 225): switch to hires text for rows 22-24 --------
irq_split:
    lda #$FF
    sta $D019
    lda #$00                 // black text bg FIRST: change $D021 at the very
    sta $D021                // top of the line so the grey bitmap bg can't leak
                             // onto the right of the split scanline
    lda #$1B                 // text mode (BMM off)
    sta $D011
    lda #$08                 // hires (MCM off)
    sta $D016
    lda #$34                 // text screen $4C00, font $5000
    sta $D018
    lda #TOPL
    sta $D012
    lda #<irq_top
    sta $0314
    lda #>irq_top
    sta $0315
    jmp $EA81

// ---- fly: each sprite weaves its OWN Lissajous curve ------------------
// Per sprite: two independent phase accumulators (angx/angy) advanced by
// per-sprite speeds (dax/day). Different X:Y speed ratios -> 8 distinct
// figure-8 / pretzel / star paths instead of one shared ellipse. A slow
// common drift is added to the Y *index* (not stored) so every figure
// precesses and the whole thing never sits still. X uses the full 9-bit
// range (xlo + xhi -> $D010 MSB) so the cubes sweep the WHOLE width.
fly:
    lda driftlo              // advance the 16-bit precession accumulator
    clc
    adc #DRIFTSTEP
    sta driftlo
    lda drifthi
    adc #0
    sta drifthi              // drifthi = current precession offset (index units)
    lda #0
    sta msbacc               // build the $D010 X-MSB byte as we go
    ldx #NSPR-1
!f:
    lda axlo,x               // X phase += dxlo (16-bit, fractional speed)
    clc
    adc dxlo,x
    sta axlo,x
    lda axhi,x
    adc #0
    sta axhi,x
    tay                      // table index = integer part of the X phase
    lda xlo,y                // low 8 bits of X -> sprite X register
    sta tmpx
    lda xhi,y                // bit 8 of X: fold into the MSB byte at bit #sprite
    beq !nomsb+
    lda msbacc
    ora bittab,x
    sta msbacc
!nomsb:
    lda aylo,x               // Y phase += dylo (16-bit, fractional speed)
    clc
    adc dylo,x
    sta aylo,x
    lda ayhi,x
    adc #0
    sta ayhi,x
    clc
    adc drifthi              // + precession (index only, not stored)
    tay
    lda ytab,y
    sta tmpy
    txa
    asl
    tay                      // Y = 2*i (sprite register offset)
    lda tmpx
    sta $D000,y
    lda tmpy
    sta $D001,y
    dex
    bpl !f-
    lda msbacc
    sta $D010                // commit all 8 X-MSB bits at once
    rts
bittab: .byte 1,2,4,8,16,32,64,128

// ---- spin: cycle each sprite's pointer through the 32 cube frames -----
spin:
    lda frame_lo
    lsr
    lsr                      // advance one rotation frame every 4 ticks
    sta spinbase
    ldx #NSPR-1
!s:
    lda cube_ph,x            // each cube starts at a different rotation frame
    clc
    adc spinbase
    and #CUBE_MASK
    clc
    adc #CUBE_PTR            // cube frames = sprite pointers CUBE_PTR..+
    sta $5FF8,x              // above the split (bitmap screen $5C00)
    sta $4FF8,x              // below the split (text screen $4C00) — see init
    dex
    bpl !s-
    rts
cube_ph: .byte 0, 4, 8, 12, 16, 20, 24, 28    // 8 cubes spread across 32 frames

// ---- flash_cubes: shift the 8 sprite colours through a rave palette ---
// Called on every kick. Each cube reads cubepal[(i + colcyc) & 15], so the
// whole rack of cubes ripples through the palette in time with the beat.
flash_cubes:
    inc colcyc
    ldx #NSPR-1
!fc:
    txa
    clc
    adc colcyc
    and #$0f
    tay
    lda cubepal,y
    sta $D027,x              // sprite colour register for cube X
    dex
    bpl !fc-
    rts
// bright, saturated colours only (no $00/$06/$09/$0b — too dark on sprites)
cubepal: .byte $01,$07,$0a,$08,$0e,$03,$0d,$05,$0f,$07,$02,$0e,$0a,$04,$0d,$01

// ---- tick_scene: song-structure escalation arc ------------------------
// Keyed off the frame counter (the song is the clock). Each scene gates how
// many cubes are enabled and whether they're 2x-stretched (climax). Resyncs
// at the song-loop point so it stays aligned across loops.
tick_scene:
    lda frame_hi             // resync at the song loop (~3731 frames = $0E93)
    cmp #$0E
    bcc !chk+
    lda frame_lo
    cmp #$93
    bcc !chk+
    lda #0
    sta frame_lo
    sta frame_hi
    sta scidx
    lda #<lyric_table        // rewind the lyric ticker so it replays each loop
    sta ly_lo                // (else it stays frozen on the last line forever)
    lda #>lyric_table
    sta ly_hi
!chk:
    ldx scidx
    cpx #6
    bcs !set+                // past the last boundary
    lda frame_lo
    cmp sc_blo,x
    lda frame_hi
    sbc sc_bhi,x             // C set if frame >= boundary
    bcc !set+
    inc scidx
!set:
    ldx scidx
    lda sc_mask,x
    sta $D015                // cube count: 2 -> 4 -> 6 -> 8
    lda sc_exp,x
    sta $D017                // 2x stretch on the climax
    sta $D01D
    rts
// boundaries (frames @175bpm): 369,934,1508,2014,2563,3205
sc_blo:  .byte $71,$A6,$E4,$DE,$03,$85
sc_bhi:  .byte $01,$03,$05,$07,$0A,$0C
sc_mask: .byte $03,$0F,$3F,$FF,$FF,$FF,$FF   // 2,4,6,8,8,8,8 cubes
sc_exp:  .byte $00,$00,$00,$00,$00,$FF,$FF   // normal ... then 2x for the climax

// ---- lyric ticker: write the current line into text row 23 -----------
lyric_tick:
    ldy #0
    lda (ly_lo),y
    cmp #$FF
    bne !nx+
    iny
    lda (ly_lo),y
    cmp #$FF
    bne !nx+
    rts                      // end of table
!nx:
    ldy #0
    lda (ly_lo),y
    cmp frame_lo
    bne !no+
    iny
    lda (ly_lo),y
    cmp frame_hi
    bne !no+
    // match — read length, clear row 23, centre, copy
    iny
    lda (ly_lo),y
    sta tmp_len
    lda #$20
    ldx #39
!clr:
    sta $4C00+23*40,x
    dex
    bpl !clr-
    lda #40
    sec
    sbc tmp_len
    lsr
    sta tmp_col
    iny                      // first char
    ldx tmp_col
!cp2:
    lda (ly_lo),y
    sta $4C00+23*40,x
    iny
    inx
    dec tmp_len
    bne !cp2-
    // advance ly ptr by 3 + length
    ldy #2
    lda (ly_lo),y
    clc
    adc #3
    adc ly_lo
    sta ly_lo
    lda ly_hi
    adc #0
    sta ly_hi
!no:
    rts

bordtab:    .byte $01,$07,$0a,$0e
sprcol:     .byte $01,$07,$08,$0a,$0e,$03,$0d,$05  // 8 cube colours
// Lissajous state (RAM, mutated each frame). Phase is 8.8 fixed point per
// axis (axhi:axlo) so the per-frame step can be a fraction of one table
// entry -> smooth, slow drift. axhi/ayhi seeded spread out; the dxlo:dylo
// ratio sets the figure shape, the magnitude sets the (gentle) speed.
axlo: .byte 0,0,0,0,0,0,0,0              // X phase, fractional byte
axhi: .byte 0,32,64,96,128,160,192,224  // X phase, integer byte (= table index)
aylo: .byte 0,0,0,0,0,0,0,0
ayhi: .byte 64,96,128,160,192,224,0,32
dxlo: .byte 48,72,64,96,40,80,88,66     // X speed (/256 of an index per frame)
dylo: .byte 72,48,96,64,80,40,66,88     // Y speed (!= dxlo -> weave)
driftlo: .byte 0                          // 16-bit precession accumulator
drifthi: .byte 0
// sine position tables (KickAss computes the sines at assemble time).
// X spans 22..322 (full screen width incl. the 9th bit); split into low byte
// + bit-8 table. Y spans 48..224 (top of the picture to the raster split).
.function sx(a) { .return round(172 + 150*sin(toRadians(a*360/256))) }
xlo:  .fill 256, mod(sx(i),256)
xhi:  .fill 256, floor(sx(i)/256)
ytab: .fill 256, round(136 + 88*sin(toRadians(i*360/256)))

*=$4400
spr_data:
    .import binary "sprite_cube.bin"     // 32 rotation frames of a 3D cube (ptr 16..47)

*=$1000
sid_body:
    .import binary "sid_body.bin"

*=$6000
koala_bitmap:
    .import binary "koala_bitmap.bin"
*=$7F40
koala_screen:
    .import binary "koala_screen.bin"
*=$8328
koala_color:
    .import binary "koala_color.bin"
*=$8710
koala_bg:
    .import binary "koala_bg.bin"

*=$8720
lyric_table:
    .import binary "lyric_table.bin"
    .byte $FF,$FF,$00
