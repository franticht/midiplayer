;GENERIC ROUTINES



;--------------------------------------------
;Clear screen

ed_clearscreen:
	
	;Clear CHAR RAM
	jsr ed_clearscreenram_default
	
	;Clear COLOR RAM
	jmp ed_clearcolorram_default	;JMP-quit

;	rts

;--------------------------------------------
;Clear Screen RAM

ed_clearscreenram_default:
	lda #$20
ed_clearscreenram:
	ldx #250
-	sta $0400+000-1,x
	sta $0400+250-1,x
	sta $0400+500-1,x
	sta $0400+750-1,x
	dex
	bne -
	rts

;--------------------------------------------
;Clear Color RAM

ed_clearcolorram_default:
	lda #0
ed_clearcolorram:
	ldx #250
-	sta $d800+000-1,x
	sta $d800+250-1,x
	sta $d800+500-1,x
	sta $d800+750-1,x
	dex
	bne -
	rts


;--------------------------------------------
;Wait for line 0

ed_waitvbl:
-	bit $d011
	bmi -
-	bit $d011
	bpl -

	rts