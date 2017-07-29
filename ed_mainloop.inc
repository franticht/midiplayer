;EDITOR MAINLOOP

ed_mainloop:
	
	;Poll for "new frame event"
ed_waitnewframe: 
;event_newframe:
event_newframe_count = *+1
	lda #0
	bmi ed_waitnewframe

	


	inc $d020

	jmp ed_mainloop