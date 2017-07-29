
;------------------------
ed_irq_editor:

	;Use all mem apart from $d000-$dfff
	sei
	lda #$35 ;MEMCONFIG_IO
	sta $01

	;Turn off all CIA driven interrupts.
	lda #$7f			;Turn off CIA-interrupts.. 
	sta $dc0d ;CIA1_ICR	;(Funky way of funxioning, those regs... This actually clears them.)
	sta $dd0d ;CIA2_ICR
	
	;NMI..
	lda #<ed_irq_nmi
	sta $fffa ;NMI_VECTORLO
	lda #>ed_irq_nmi
	sta $fffb ;NMI_VECTORHI

	rts
	

;------------------------
ed_irq_nmi:

	rti