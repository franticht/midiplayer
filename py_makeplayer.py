#!/opt/local/bin/python

from random import randint

#Configuration settings
NUMRANDFILES = 8
PL_NUMCHANNELS = 6
PL_NUMSIDCHANNELS = 6   #3 for mono sid, 6 for stereo sid, or 9 for tripple sid...
PL_NUMSONGPOSITIONS = 256
PL_ZPSTART = 2



#Variable init
zpcounter = PL_ZPSTART
pf = ""
df = ""

#Generate data file
df += """\
; droneMON PLAYER DATA

		; align code to page border for speed increase
		!align 255, 0

pl_seqptrs_lo:
"""
for i in range(PL_NUMSONGPOSITIONS):
    df += "	   !byte <pl_seq_"+'{:02X}'.format(i)+"\n"
df += "\n"
df += "pl_seqptrs_hi:\n"
for i in range(PL_NUMSONGPOSITIONS):
    df += "	   !byte >pl_seq_"+'{:02X}'.format(i)+"\n"
df += "\n"
for i in range(PL_NUMCHANNELS):
    df += "pl_chn"+str(i).zfill(2)+"_seqlist:\n"
    df += "		!fill PL_NUMSONGPOSITIONS, 0\n"
    # df += "        !for i, PL_NUMSONGPOSITIONS {!byte i-1}\n"
df += "\n"
for i in range(PL_NUMSONGPOSITIONS):
    df += "pl_seq_"+'{:02X}'.format(i)+":\n"
    df += "		rts\n"
df += "\n"




#Generate code file
pf += """\
; droneMON PLAYER CODE

; This file is autogenerated by py_makeplayer.py and deleted when issuing a make clean,
; so please don't mess with it directly. Make changes in the python script instead.

;Design choice: No sidbuffer (parameters make variation possible instead)

;============================
;Config constants

PL_NUMCHANNELS = """+str(PL_NUMCHANNELS)+"""
PL_NUMSIDCHANNELS = """+str(PL_NUMSIDCHANNELS)+"""
PL_NUMSONGPOSITIONS = """+str(PL_NUMSONGPOSITIONS)+"""
PL_ZP_SONGPOS = $"""+'{:02X}'.format(zpcounter)+"\n"
zpcounter += 1
pf += "PL_ZP_TICKCOUNTER = $"+'{:02X}'.format(zpcounter)+"\n"
zpcounter += 1
pf += "\n"

nbytes = 2
pf += ";Sequence pointers\n"
for i in range(PL_NUMCHANNELS):
    pf += "PL_ZP_CHN"+str(i).zfill(2)+" = $"+'{:02X}'.format(zpcounter)+"\t;"+str(nbytes)+" bytes\n"
    zpcounter += nbytes
pf += "\n"

nbytes = 1
pf += ";Song position counters (separate for each channel)\n"
for i in range(PL_NUMCHANNELS):
    pf += "PL_ZP_CHN"+str(i).zfill(2)+"_SONGPOS = $"+'{:02X}'.format(zpcounter)+"\t;"+str(nbytes)+" bytes\n"
    zpcounter += nbytes
pf += "\n"

nbytes = 1
pf += ";Internal sequence position counters (separate for each channel)\n"
for i in range(PL_NUMCHANNELS):
    pf += "PL_ZP_CHN"+str(i).zfill(2)+"_SEQPOS = $"+'{:02X}'.format(zpcounter)+"\t;"+str(nbytes)+" bytes\n"
    zpcounter += nbytes
pf += "\n"

nbytes = 1
pf += ";Delay counters (steps, not ticks, between each note)\n"
for i in range(PL_NUMCHANNELS):
    pf += "PL_ZP_CHN"+str(i).zfill(2)+"_DELAY = $"+'{:02X}'.format(zpcounter)+"\t;"+str(nbytes)+" bytes\n"
    zpcounter += nbytes
pf += "\n"

#Sanity checking
if zpcounter > 255:
    quit("ERROR:\tZeropage data overflow in the py_makeplayer.py script!")


pf += """\
;============================
pl_main:

    ;SKICKA MIDI-KLOCKA


    ;---------------------------
    ; Sequence parsing

		;--------------------
		;Här ska det vara nån tick/step/groove-nånting-kod.
		;Mnja.. Det ska vara shufflespeed mha timerinterruptsen istället.
		;Both MIDI and DIN Sync clocks are sent at a rate of 24 ppqn (pulses per quarter note).
		;a Roland compatible device playing sixteenth notes would have to advance to
		;the next note every time it receives 6 pulses.

		;First check for sequence break (which is when tickcounter = 0)
		dec PL_ZP_TICKCOUNTER\t;Ranges from 00-c0
		beq +
		jmp .noseqbreak
+

			;Time to fetch new sequence pointers

"""
for i in range(PL_NUMCHANNELS):
    pf += "			;Fetch pointer for chn"+str(i).zfill(2)+"\n"
    pf += "			ldy PL_ZP_CHN"+str(i).zfill(2)+"_SONGPOS\t;Allow separate song positions for each channel (like ableton live mode).\n"
    pf += "			lax pl_chn"+str(i).zfill(2)+"_seqlist,y\n"
    pf += "			lda pl_seqptrs_lo,x\n"
    pf += "			sta PL_ZP_CHN"+str(i).zfill(2)+"\n"
    pf += "			lda pl_seqptrs_hi,x\n"
    pf += "			sta PL_ZP_CHN"+str(i).zfill(2)+"+1\n"
    pf += "			inc PL_ZP_CHN"+str(i).zfill(2)+"_SONGPOS\t;Bump\n"
    pf += "\n"
pf += """\
			;Clear seqbreakflag
			lda #$c0\t;There are ALWAYS 6*32 ticks/clocks in each sequence = compatible with SYNC24/MIDI SYNC
			sta PL_ZP_TICKCOUNTER

.noseqbreak:
;---

"""
# Actual sequence parsing
pf += """\
		;Decide what to do on different player ticks (0 = seqparse, 3 = pretrig, 1,2,4,5 = do nothing)
        ldx PL_ZP_TICKCOUNTER
		lda pl_tickaction,x
		beq .tick00\t;00 in the table means tick00 (seqparse)
		bpl .tick03\t;01 in the table means tick03 (pretrig)
		jmp .doneseqparse\t;ff means there is no sequence parsing to do

"""

#Sequence format
#
# Sequence break is handled by setting the PL_ZP_TICKCOUNTER variable directly from a sound chunk
#
#CTRL:
# b7 - NT   (implies one byte 00-7f = set note only, 80-ff set note+TRIG)
# b6 - S1   (implies one byte of sound chunk pointer. If that is in range 80-ff that implies one more byte of PARAMETER)
# b5 - S2   (implies one byte of sound chunk pointer. If that is in range 80-ff that implies one more byte of PARAMETER)
# b4-b0     (...corresponds to a 5bit number of pattern steps until the next one. Max = 32 = one whole sequence)
#
# NT  S1 P  S2
# C-4 4F -- --

# Om det är 3 ticks kvar till nästa så gör man en lookahead.
# (MEN MÅSTE DET ALLTID VARA JUST 3 TICKS? JA KANSKE? FÖR ENKELHETENS SKULL?)
# Använd note range $80+ för att indikera "TRIG" av något.
# Om man alltså hittar TRIG när man gör en lookahead så ska man kolla vidare om:
#   1. Sätts ett nytt instrument i ST1 PÅ DENNA RAD?
#   2. Om ja: Läs från pretrigtabell (ett värde för varje instrument) och JSR'a DIREKT DIT.
#   2. Om nej: Kolla om nuvarande defaultinstrument har PRETRIG

# Om det är 0 ticks var så:
# ...kollar man om ett nytt instrument sätts i ST1

pf += """\
        ;Pretrig (at tick03)
.tick03:
		;--------------------

"""
for i in range(PL_NUMCHANNELS):
    pf += "        ;Pre-parse channel """+'{:02X}'.format(i)+"\n"


pf += """
		jmp .doneseqparse

        ;Seqparse (at tick00)
.tick00:

"""
for i in range(PL_NUMCHANNELS):
    # pf += "xyz\n"
    pf += """\
		;--------------------
        ;Parse channel """+'{:02X}'.format(i)+"""
        dec PL_ZP_CHN"""+str(i).zfill(2)+"""_DELAY
        bpl +
            ldy PL_ZP_CHN"""+str(i).zfill(2)+"""_SEQPOS
            lda (PL_ZP_CHN"""+str(i).zfill(2)+"""),y	;Read control byte
+
        ;OBS: Det måste finnas något sätt att skippa steps i traxxet
        
        \n"""
pf += """\
.doneseqparse:
.noseqparse:

		rts
		;---


;============================
pl_init:
        ;Ensure that the first step is executed at once 
		lda #1
		sta PL_ZP_TICKCOUNTER
        
        ;Set a bunch of things to zero
        ldx #PL_NUMCHANNELS
-       sta PL_ZP_CHN00_DELAY,x
        dex
        bpl -
        rts
		;---


;============================
pl_tickaction = *-1\t;Make table 1-indexed rather than 0-indexed
"""
for i in range(32):
    pf += "		!byte $00\t;$"+'{:02X}'.format(i*6+1)+": Tick 00\n"
    pf += "		!byte $ff\t;$"+'{:02X}'.format(i*6+2)+": Tick 01\n"
    pf += "		!byte $ff\t;$"+'{:02X}'.format(i*6+3)+": Tick 02\n"
    pf += "		!byte $01\t;$"+'{:02X}'.format(i*6+4)+": Tick 03\n"
    pf += "		!byte $ff\t;$"+'{:02X}'.format(i*6+5)+": Tick 04\n"
    pf += "		!byte $ff\t;$"+'{:02X}'.format(i*6+6)+": Tick 05\n"
pf += "		;---\n"
pf += "\n"




text_file = open("pl_main.a", "w")
text_file.write(pf)
text_file.close()

text_file = open("pl_data.a", "w")
text_file.write(df)
text_file.close()

#Finally, generate some files with random bytes, for watermarking purposes
# for i in range(NUMRANDFILES):
#     rndfile = ""
#     for j in range(randint(1,5)):
#         rndfile += "     !byte $"+'{:02X}'.format(randint(0,255))+"\n"
#     text_file = open("ed_rndfile"+str(i+1)+".a", "w")
#     text_file.write(rndfile)
#     text_file.close()
    

