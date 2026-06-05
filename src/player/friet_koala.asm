// Friet met Desire — KOALA demo player.
// Full-screen multicolor-bitmap KoalaPainter image + the SID, with a
// beat-reactive colour cycle (border + background step on every kick).
//
// Memory: $0801 BASIC stub, $0810 player, $1000 SID body (~$43C5),
//         $5C00 screen matrix (filled at runtime), $6000 koala bitmap,
//         $7F40 koala screen src, $8328 koala colour src, $8710 bg.
// VIC bank 1 ($4000-$7FFF): bitmap $6000 (offset $2000), screen $5C00.

.const SID_INIT = $1000
.const SID_PLAY = $1003
.var gate_prev = $90      // previous V3 triangle bit (kick edge-detect)
.var beatc     = $91      // kicks counted -> colour-cycle index

*=$0801
    .byte $0B, $08, $0A, $00, $9E
    .text "2064"
    .byte $00, $00, $00

*=$0810
entry:
    sei
    lda #0
    ldx #$0d
!zpclr:
    sta $02,x
    dex
    bpl !zpclr-
    sta gate_prev
    sta beatc

    // Copy koala screen-RAM ($7F40) -> VIC screen matrix $5C00, and
    // koala colour-RAM ($8328) -> colour RAM $D800 (1024 bytes each).
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

    // VIC bank 1 ($4000-$7FFF)
    lda $DD00
    and #$FC
    ora #$02
    sta $DD00
    lda #$78            // screen matrix $5C00 (hi nibble 7), bitmap $6000 (bit3)
    sta $D018
    lda #$3B            // bitmap mode (BMM), display enabled
    sta $D011
    lda #$18            // multicolor on
    sta $D016
    lda koala_bg
    sta $D021
    lda #$00
    sta $D020

    // SID init (subtune 0)
    lda #0
    tax
    tay
    jsr SID_INIT

    // Hook IRQ (raster)
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
!forever:
    jmp !forever-

irq:
    lda #$FF
    sta $D019
    jsr SID_PLAY
    // --- kick detect (V3 triangle waveform bit) rising edge -> cycle ---
    lda $D412
    and #$10
    tax
    cmp gate_prev
    stx gate_prev
    beq !nobeat+
    txa
    beq !nobeat+        // triangle cleared (kick ended) -> ignore
    inc beatc
    lda beatc
    and #$03
    tay
    lda bordtab,y
    sta $D020            // border pulses on the kick; the painted picture
                         // ($D021 background) is left intact
!nobeat:
    jmp $EA81

bordtab: .byte $01, $07, $0a, $0e    // white, yellow, light red, light blue

// ---- SID body ---------------------------------------------------------
*=$1000
sid_body:
    .import binary "sid_body.bin"

// ---- Koala image (KoalaPainter memory layout) -------------------------
*=$6000
koala_bitmap:
    .import binary "koala_bitmap.bin"    // 8000  $6000-$7F3F
*=$7F40
koala_screen:
    .import binary "koala_screen.bin"    // 1000  $7F40-$8327
*=$8328
koala_color:
    .import binary "koala_color.bin"     // 1000  $8328-$870F
*=$8710
koala_bg:
    .import binary "koala_bg.bin"        // 1     $8710
