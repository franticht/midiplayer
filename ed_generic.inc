;GENERIC ROUTINES



;--------------------------------------------
;Clear screen

ed_clearscreen:
	ldx #0
	
	;Clear CHAR RAM
	lda #$20
-	sta $0400+40*0,x
	sta $0400+40*6,x
	sta $0400+40*12,x
	sta $0400+40*18,x
	dex
	bne -
	
	;Clear COLOR RAM
	lda #5
-	sta $d800+40*0,x
	sta $d800+40*6,x
	sta $d800+40*12,x
	sta $d800+40*18,x
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