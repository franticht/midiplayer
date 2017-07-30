;INITIALIZE EDITOR

ed_init:

	;Turn interrupts off and select normal ROM banking
	sei
	lda #$37
	sta $01
	
	;Clear screen
	lda #0
	sta $d020
	sta $d021
	jsr ed_clearscreen
	
	;Initialize player
	lda #0
	jsr pl_init
	
	;Initialize interrupts
	jsr ed_interrupt_editor

	rts