;EDITOR MAINLOOP

ed_mainloop:
	
	;Poll for "new frame event"
ed_waitnewframe: 
ed_waitnewframe_count = *+1
	lda #0
	bmi ed_waitnewframe
	dec ed_waitnewframe_count ;Mark frame as handled


	inc $d020

	jmp ed_mainloop