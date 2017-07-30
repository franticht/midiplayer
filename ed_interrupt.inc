
;------------------------
ed_interrupt_editor:

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

	;IRQ
	lda #<ed_irq_irq
	sta $fffe ;IRQ_VECTORLO
	lda #>ed_irq_irq
	sta $ffff ;IRQ_VECTORHI

	;CIA2 - NMI - Timer A = Driving the player.
	lda ed_timerval
	sta $dd04 ;Timer A Low-Byte  (RS232)CIA2_TA_LO
	lda ed_timerval+1
	sta $dd05 ;CIA2_TA_HI

	jsr ed_waitvbl
	lda #20
-	cmp $d012
	bne -

	lda #$11	;FORCE_LOAD | TIMER_START
	sta $dd0e	;CIA2_CRA
	lda #$81									;Set Interrupt for CIA2_TA.. Driving the player.
	sta $dd0d	;CIA2_ICR						;Interrupt control register

	;Set up raster interrupt
	lda #$01
	sta $d01a
	lda $d011
	and #$7f	;Turn off hibit in $d011
;	ora #$80	;Make sure it's on..
	sta $d011	;Make sure hibit of $d012 is off..
;	lda # ;ED_RASTER_IRQ_LINE
	lda #$20
	sta $d012

	;Go interrupts
	asl $d019   ;Ack any Previous Raster IRQ (clear IRQ flags)
	bit $dc0d   ;Ack any Previous CIA 1 IRQ (clear IRQ flags)
	bit $dd0d   ;Ack any Previous CIA 2 NMI (clear NMI flags)
	cli         ;Renable IRQ's

	;Init $dd00 (make sure there is no CLK/DATA bits on per default)
	;This is called both in editor init and when exiting disk menu
	;Due to the AR bug, this code doesn't really have much effect, but
	;I guess it is cleaner to have it here too anyway.
	lda #%11000111 ;=199, Vic bank 0 and CLK/DATA OFF (yes, not on..)
	sta $dd00

	rts
	

;------------------------------------------------
; NMI INTERRUPT CODE

ed_irq_nmi:
	sta ed_irq_nmi_savea
	stx ed_irq_nmi_savex
	sty ed_irq_nmi_savey				

ed_irq_nmi_savea = *+1
	lda #0
ed_irq_nmi_savex = *+1
	ldx #0
ed_irq_nmi_savey = *+1
	ldy #0

	;Ack Timer NMI
	bit $dd0d

	rti
	

;------------------------------------------------
; IRQ INTERRUPT CODE

ed_irq_irq:
;	sta ed_irq_irq_savea
;	stx ed_irq_irq_savex
;	sty ed_irq_irq_savey				

	;Increase newframe counter
	inc ed_waitnewframe_count
	
;ed_irq_irq_savea = *+1
;	lda #0
;ed_irq_irq_savex = *+1
;	ldx #0
;ed_irq_irq_savey = *+1
;	ldy #0

	;Ack Raster IRQ (clear irq flags)
	asl $d019
	
	rti