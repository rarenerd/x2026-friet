// Friet met Desire — KOALA demo: warm dragon bitmap (top) + bouncing sprite
// ornaments + a RASTER-SPLIT text bar (bottom 3 rows) running the synced
// lyric ticker. Music on V-blank, border + sprite-launch on the kick.
//
// VIC bank 1 ($4000-$7FFF) memory map:
//   $1000  SID body          $4400 sprite shape (ptr 16)
//   $4800  text screen (ptr 2)   $5000 RAM font (charbase 2)
//   $5C00  bitmap screen (koala colours) + $5FF8 sprite pointers
//   $6000  bitmap   $7F40 screen src   $8328 colour src   $8710 bg
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
.const NSPR  = 6
.const CUBE_FRAMES = 32   // rotation frames in sprite_cube.bin (power of 2; 32 later)
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
    lda koala_screen_b,x          // interlace frame B -> $5800
    sta $5800,x
    lda koala_screen_b+$100,x
    sta $5900,x
    lda koala_screen_b+$200,x
    sta $5A00,x
    lda koala_screen_b+$300,x
    sta $5B00,x
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

    // sprite pointers -> $4400 (ptr 16); text screen cleared to spaces
    lda #16
    ldx #7
!sp:
    sta $5FF8,x                  // sprite pointers for screen A ($5C00)
    sta $5BF8,x                  // ... and for interlace screen B ($5800)
    dex
    bpl !sp-
    lda #$20                 // clear visible text rows 22..24 to spaces
    ldx #119
!ct:
    sta $4C00+22*40,x
    lda #$07                 // yellow text colour for those rows
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
    lda #$3F
    sta $D015
    sta $D017                // double height (epic, imposing cubes)
    sta $D01D                // double width

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
    lda frame_lo             // 50Hz interlace: flip screen A/B each frame
    lsr
    lda #$78                 // even -> screen $5C00 (frame A)
    bcc !ia+
    lda #$68                 // odd  -> screen $5800 (frame B), bitmap $6000
!ia:
    sta $D018
    jsr SID_PLAY
    jsr fly
    jsr spin
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

// ---- fly: each sprite orbits an ellipse (sine paths) ------------------
fly:
    ldy #NSPR-1
!f:
    lda frame_lo
    clc
    adc phtab,y              // per-sprite orbit phase
    tax                      // X = angle index 0..255
    lda xtab,x
    sta tmpx
    lda ytab,x
    sta tmpy
    tya
    asl
    tax                      // X = 2*i (sprite register offset)
    lda tmpx
    sta $D000,x
    lda tmpy
    sta $D001,x
    dey
    bpl !f-
    rts

// ---- spin: cycle each sprite's pointer through the 8 cube frames ------
spin:
    lda frame_lo
    lsr
    lsr                      // advance one rotation frame every 4 ticks
    sta spinbase
    ldx #NSPR-1
!s:
    txa
    clc
    adc spinbase             // stagger phase per sprite
    and #CUBE_MASK
    clc
    adc #CUBE_PTR            // cube frames = sprite pointers CUBE_PTR..+
    sta $5FF8,x              // frame-A pointers
    sta $5BF8,x              // frame-B pointers
    dex
    bpl !s-
    rts

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
sprcol:     .byte $01,$07,$08,$0a,$0e,$03      // white,yellow,orange,lred,lblue,cyan
phtab:      .byte 0, 43, 86, 128, 171, 214     // orbit phase per sprite
// elliptical orbit position tables (KickAss computes the sines at assemble time)
xtab: .fill 256, round(140 + 112*sin(toRadians((i+64)*360/256)))
ytab: .fill 256, round(104 + 80*sin(toRadians(i*360/256)))

*=$4400
spr_data:
    .import binary "sprite_cube.bin"     // 8 rotation frames of a 3D cube (ptr 16..23)

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

*=$8C00
koala_screen_b:
    .import binary "koala_screen_b.bin"
