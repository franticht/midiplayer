;INITIALIZE EDITOR

ed_init:

	;Turn interrupts off and select normal ROM banking
	sei
	lda #$37
	sta $01

	;Initialize player
	lda #0
	jsr pl_init

	rts