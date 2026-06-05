// Friet met Desire — KOALA demo player WITH BOUNCING SPRITE ORNAMENTS.
// Full-screen multicolor-bitmap picture + the SID + 6 hardware sprites that
// bounce (gravity + floor restitution) and get re-launched UP on every kick.
// Border colour also cycles on the kick.
//
// Memory: $0801 stub, $0810 player, $1000 SID, $4800 sprite shape,
//         $5C00 screen matrix (runtime copy), $5FF8 sprite pointers,
//         $6000 koala bitmap, $7F40 screen src, $8328 colour src, $8710 bg.
// VIC bank 1 ($4000-$7FFF).

.const SID_INIT = $1000
.const SID_PLAY = $1003
.var gate_prev = $90
.var beatc     = $91
.const NSPR  = 6
.const FLOOR = 214          // sprite Y where it bounces
.const GRAV  = 1

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

    // copy koala screen ($7F40)->$5C00 and colour ($8328)->$D800 (1024 b)
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

    // sprite pointers (AFTER the copy, which touched $5FF8): all -> $4800
    lda #32
    ldx #7
!sp:
    sta $5FF8,x
    dex
    bpl !sp-

    // VIC bank 1, multicolor bitmap
    lda $DD00
    and #$FC
    ora #$02
    sta $DD00
    lda #$78
    sta $D018
    lda #$3B
    sta $D011
    lda #$18
    sta $D016
    lda koala_bg
    sta $D021
    lda #$00
    sta $D020

    // sprites: fixed X, colours, enable, init bounce state
    ldx #NSPR-1
!si:
    lda spr_xlo,x
    txa
    asl
    tay
    lda spr_xlo,x
    sta $D000,y          // X low for sprite x  ($D000 + 2*x)
    lda spr_y0,x
    sta spr_y,x
    lda spr_vy0,x
    sta spr_vy,x
    lda sprcol,x
    sta $D027,x          // sprite colour
    dex
    bpl !si-
    lda #$30             // X MSB for sprites 4 & 5 (x=256,300)
    sta $D010
    lda #$00
    sta $D01C            // hires sprites
    sta $D01B            // sprites in front of the bitmap
    lda #$3F             // enable sprites 0..5
    sta $D015

    // SID init
    lda #0
    tax
    tay
    jsr SID_INIT

    // hook IRQ
    lda #<irq
    sta $0314
    lda #>irq
    sta $0315
    lda #$7F
    sta $DC0D
    sta $DD0D
    lda $DC0D
    lda $DD0D
    lda #$01
    sta $D01A
    lda #250
    sta $D012
    lda $D011
    and #$7F
    sta $D011
    cli
!fe:
    jmp !fe-

irq:
    lda #$FF
    sta $D019
    jsr SID_PLAY
    jsr bounce
    // kick detect (V3 triangle bit rising edge) -> border cycle + re-launch
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
    ldx #NSPR-1          // re-launch every sprite UP on the kick
!kl:
    lda spr_launch,x
    sta spr_vy,x
    dex
    bpl !kl-
!nob:
    jmp $EA81

// ---- bounce: gravity + floor, write Y registers -----------------------
bounce:
    ldx #NSPR-1
!b:
    lda spr_vy,x
    clc
    adc #GRAV
    sta spr_vy,x
    clc
    lda spr_y,x
    adc spr_vy,x         // signed add (vy is two's-complement)
    sta spr_y,x
    cmp #FLOOR
    bcc !nf+
    lda #FLOOR
    sta spr_y,x
    lda spr_bounce,x     // restitution velocity (negative)
    sta spr_vy,x
    lda #FLOOR
    sta spr_y,x
!nf:
    txa
    asl
    tay
    lda spr_y,x
    sta $D001,y          // sprite x's Y register ($D001 + 2*x)
    dex
    bpl !b-
    rts

bordtab:    .byte $01,$07,$0a,$0e
spr_xlo:    .byte 30, 64, 98, 222, 0, 44       // X low (spr4,5 use MSB)
sprcol:     .byte $01,$07,$08,$0a,$07,$08      // white,yellow,orange,lred,yellow,orange (warm)
spr_y0:     .byte 80, 120, 170, 90, 140, 200
spr_vy0:    .byte $f8,$f6,$f9,$f7,$f5,$fa
spr_bounce: .byte $f9,$f8,$f7,$f9,$f8,$f7      // -7..-9 restitution
spr_launch: .byte $f4,$f3,$f5,$f4,$f3,$f5      // -11,-13,-11.. kick pop
spr_y:      .byte 0,0,0,0,0,0
spr_vy:     .byte 0,0,0,0,0,0

// ---- sprite shape -----------------------------------------------------
*=$4800
spr_data:
    .import binary "sprite_orn.bin"

// ---- SID body ---------------------------------------------------------
*=$1000
sid_body:
    .import binary "sid_body.bin"

// ---- Koala image ------------------------------------------------------
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
