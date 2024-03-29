#!/usr/bin/python3

# Copyright (c) 2024
# clay@thoughtrights.com
# Thoughtrights

import os
import sys
from pathlib import Path
from os.path import exists
from openai import OpenAI
from pydub import AudioSegment
import re
import random

random.seed()

client = OpenAI(api_key=os.environ.get("OPENAI_DUNGEONEER_API_KEY"))
fullAudioFile = AudioSegment.silent(duration=0)

fillerWordsShort = ["uh", "um", "so"]
fillerWordsLong = ["uh", "um", "so", "well", "er", "hmm", "like", "okay"] # FUTURE IMPROVEMENT

allowedVoices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
allowedModels = ["tts-1", "tts-1-hd"]
minSpeed = 0.25 # 1/4 speed - will have varying distortion b/c it's done in post
maxSpeed = 4    # 4x speed - will have varying distortion b/c it's done in post
minDelay = 0    # no delay at chapter switch
maxDelay = 3600 # sixty minutes max delay
minFiller= 0    # never *add* filler words
maxFiller= 1    # always *add* a filler word in a sentence break

defaultSettings = {
    "CHAPTER": "default",
    "DELAY": 1.5,  
    "SPEED": 1.0,
    "VOICE": "alloy",
    "FILLER": 0,
    "MODEL": "tts-1"
}



document = '''
### CHAPTER intro, SPEED 1.0, VOICE onyx

Good evening everyone. ... Tonight we have a special guest who will be
reading an epic poem in Tolkien's Elvish language, Quenya.

Please welcome our spoken word performer, FABLE.


### CHAPTER reader intro, SPEED 1.0, VOICE fable, DELAY 2.5, FILLER 0.2

Hello and good evening. My stage name is FABLE.

Tonight that is very appropriate.

The poem I will read for you tonight is entitled "The Unlikely
Hero". It is similar in form as all those novels following the style
outlined by Joseph Campbell in his book, "The Hero with a Thousand
Faces".

As indicated ... it is written in Quenya. This is only one of
J.R.R. Tolkien's many invented languages. Quenya itself is only one of
his two well-constructed fantasy ELVISH languages. His other Elvish
language is called "Sindarin".

Tonight ... I will be reading "The Unlikely Hero" - written by a
fictional Elf author - in a fictional Elvish language.

I apologize in advance for it being dense, but I hope you can
appreciate its tone and flow. Afterward I will recite the same poem in
the King's English. 

Please sit back and enjoy its rhythm as I twist my tongue in knots.

Thank you.


### CHAPTER quenya poem, DELAY 3.2, SPEED 1.0, VOICE fable, FILLER 0.0

"I ÚMIELYA HERU: ELENIË I EÄRENDIL"

Mélië ar sírë lómë,
I úmielya heru,
Ná care alwë,
Ar ná culumë anta.

Táreo coa,
Ná corma firya,
I carië tirya,
Ar i lambë úrë.

Ná i oromardi,
Ná i núrë cendë,
Ná i firyal,
Ar ná i herur.

Á anta maruvan,
I úmielya heru,
Táreo coa,
Ar i vinya lúmë.

Aldaron antanë,
Nér care atan,
Nárë firë hilya,
Ná vandë tuluva.

Tulë sí manë,
I úmielya heru,
Táreo coa,
Ar síla vëa.

I quendi tuluva,
Míra úcarë atan,
Ná vandë tuluva,
Ar ná pilinë heru.

Nárë valdë hilya,
I úmielya heru,
Táreo coa,
Ar síla undómë.

Meldo vardë atan,
Ar menelvar tulya,
Nárë tirë carë,
Ar sí manë cala.

Nai melmë síra,
I úmielya heru,
Táreo coa,
Ar síla vinya.

Elenië i Eärendil,
Ná care alwë,
Ar ná culumë anta,
Nárë tirë carë.

Eärendil ambar,
I úmielya heru,
Táreo coa,
Ar síla vinya.

Aldaron antanë,
Nér care atan,
Nárë firë hilya,
Ná vandë tuluva.

Elenië i Eärendil,
I úmielya heru,
Táreo coa,
Ar síla undómë.

Nárë valdë hilya,
I úmielya heru,
Táreo coa,
Ar síla undómë.

Nai melmë síra,
I úmielya heru,
Táreo coa,
Ar síla vinya.

Elenië i Eärendil,
I úmielya heru,
Táreo coa,
Ar síla vinya.


### CHAPTER translation, DELAY 3.2, SPEED 1.0, VOICE fable, FILLER 0.03

And now the English translation ...

"THE UNLIKELY HERO: ELENIË OF EÄRENDIL"

In the twilight of evening,
The unlikely hero,
He does not seek glory,
And he does not crave fame.

He walks alone,
Without a shining sword,
The heart of a wanderer,
And the soul of a dreamer.

He is not of noble birth,
Nor of royal blood,
Nor of heroic lineage,
And nor of great strength.

But in his heart burns,
The unlikely hero,
He walks alone,
And the wind whispers his name.

The trees sing,
Men heed his call,
The fire of his spirit,
Does not fade away.

Under starlit sky,
The unlikely hero,
He walks alone,
And the world awakens.

The elves listen,
To the words of men,
They heed his call,
And do not forget the hero.

The fire of his spirit,
The unlikely hero,
He walks alone,
And the world is changed.

The heavens bow to him,
And the stars shine bright,
The fire still burns,
And under this sky he stands.

For his love is true,
The unlikely hero,
He walks alone,
And the world rejoices.

Elenië of Eärendil,
He does not seek glory,
And he does not crave fame,
Yet the world remembers.

Eärendil's star,
The unlikely hero,
He walks alone,
And the world rejoices.

The trees sing,
Men heed his call,
The fire of his spirit,
Does not fade away.

Elenië of Eärendil,
The unlikely hero,
He walks alone,
And the world is changed.

The fire of his spirit,
The unlikely hero,
He walks alone,
And the world is changed.

For his love is true,
The unlikely hero,
He walks alone,
And the world rejoices.

Elenië of Eärendil,
The unlikely hero,
He walks alone,
And the world rejoices.



### CHAPTER close, DELAY 2.8, SPEED 1.0, VOICE fable

Thank you for your time tonight.

### CHAPTER close-2, SPEED 1.0, VOICE onyx

Alright. As always, THANK YOU FABLE.
'''

def verboseOutput (msg):
    print(msg) # add in logging system and log levels?
    sys.stdout.flush()

def errorOutput (msg):
    print(msg) # add in logging system and log levels?
    sys.stdout.flush()

    
def createSegment (client, settings=defaultSettings, dialog=''):

    tempAudioFile = "tmp_chapter.mp3"

    verboseOutput(f"Working on chapter \"{settings['CHAPTER']}\".")
    verboseOutput(f"Adding {settings['DELAY']} seconds of silence.")
    audioSegment = AudioSegment.silent(duration= (settings['DELAY'] * 1000)) # DELAY is in secs. duration takes msecs

    verboseOutput(f"Requesting audio file from OpenAI for dialog.")
    response = client.audio.speech.create(
        model = settings['MODEL'],
        voice = settings['VOICE'],
        speed = settings['SPEED'],
        input = dialog
    )

    with open(tempAudioFile, "wb") as f:
        f.write(response.content) 

    # If we want to support RIGHT and LEFT stereo weights. We'd do the
    # mixing right here.
    
    audioSegment += AudioSegment.from_file(tempAudioFile)
    os.remove(tempAudioFile)
    verboseOutput(f"Finished chapter \"{settings['CHAPTER']}\".")
    return (audioSegment)





currentSettings = defaultSettings
currentText = ''
alreadyInChapter = False

# For FILLER word opportunities
prevLineEndedWithComma = None
prevLineEndedWithPeriod = None
prevLineEndedWithEllipses = None

for line in document.splitlines():

    if line.startswith('### CHAPTER'):
        if alreadyInChapter:
            # make the previous chapter
            fullAudioFile += createSegment(client, currentSettings, currentText)

            # flush the old settings before loading new ones
            currentSettings = defaultSettings
            currentText = ''

        alreadyInChapter = True

        # SIMPLE PARSER FOR THE CHAPTER-DIRECTIVE
        for directive in line.split(','):
            # minor cleaning allowances
            directive = re.sub('^\s*', '', directive)
            directive = re.sub('\s*$', '', directive)
            directive = re.sub('"', '', directive)
            
            # Python 3.10 and above could do a "match" style case statement, but let's not assume that.
            # There's probably a ARGV approach I could use, but I like the markup style I already picked.
            if directive.startswith('### CHAPTER'):
                chapterName = ''
                chapterName = re.sub('^\s*', '', directive[11:])
                currentSettings['CHAPTER'] = chapterName
            elif directive.startswith('DELAY'):
                chapterDelay = float(re.search(r"\s([0-9\.]+)$", directive).group(1))
                if (chapterDelay >= minDelay and chapterDelay <= maxDelay):
                    currentSettings['DELAY'] = chapterDelay
                else:
                    errorOutput(f"error: Bad delay value, {chapterDelay}.") 
            elif directive.startswith('SPEED'):
                chapterSpeed = float(re.search(r"\s([0-9\.]+)$", directive).group(1))
                if (chapterSpeed >= minSpeed and chapterSpeed <= maxSpeed):
                    currentSettings['SPEED'] = chapterSpeed
                else:
                    errorOutput(f"error: Bad speed value, {chapterSpeed}.") 
            elif directive.startswith('VOICE'):
                chapterVoice = re.search(r"VOICE\s+([a-z]+)$", directive).group(1)
                if (chapterVoice in allowedVoices):
                    currentSettings['VOICE'] = chapterVoice
                else:
                    errorOutput(f"error: Unknown voice, {chapterVoice}.") 
            elif directive.startswith('FILLER'):
                chapterFiller = float(re.search(r"\s([0-9\.]+)$", directive).group(1))
                if (chapterFiller >= minFiller and chapterFiller <= maxFiller):
                    currentSettings['FILLER'] = chapterFiller
                else:
                    errorOutput(f"error: Bad filler value, {chapterFiller}")
            elif directive.startswith('MODEL'):
                chapterModel = re.search(r"MODEL\s+([a-zA-Z\-]+)$", directive).group(1)
                if (chapterModel in allowedModels):
                    currentSettings['MODEL'] = chapterModel
                else:
                    errorOutput(f"error: Unknown model, {chapterModel}.") 
            else:
                errorOutput(f"error: Unknown directive, {directive}.") 
                
                    
    else: #not a new chapter
        
        # Filler words active in this chapter and not a blank line
        if ((currentSettings['FILLER'] > 0) and (re.search(r"\w+", line))):
            # The previous line should be evaluated as a filler opportunity
            if (random.random() <= currentSettings['FILLER']):
                if (prevLineEndedWithEllipses):
                    line = random.choice(fillerWordsShort) + "... " + line
                elif (prevLineEndedWithPeriod or prevLineEndedWithComma):
                    line = random.choice(fillerWordsShort) + " " + line

            # Each ellipse is an opportunity (and double-dips if it's on the end of a sentence)
            lineParse = line
            line = ''
            while (re.search("\.\.\.", lineParse)):
                # found an oppty. 
                if (random.random() <= currentSettings['FILLER']):
                    # add filler
                    x = (re.search("\.\.\.", lineParse))
                    line += lineParse[0:(x.end())] + random.choice(fillerWordsShort) + "..."
                    lineParse = lineParse[(x.end()):]
                else:
                    # don't add filler
                    x = (re.search("\.\.\.", lineParse))
                    line += lineParse[0:(x.end())] 
                    lineParse = lineParse[(x.end()):]
            line += lineParse

            # Each period followed by a space and capital is a filler opportunity
            lineParse = line
            line = ''
            while (re.search("\.\s[A-Z]", lineParse)):
                # found an oppty. 
                if (random.random() <= currentSettings['FILLER']):
                    # add filler
                    x = (re.search("\.\s[A-Z]", lineParse))
                    line += lineParse[0:(x.end() - 1)] + random.choice(fillerWordsShort) + " "
                    lineParse = lineParse[(x.end() - 1):]
                else:
                    # don't add filler
                    x = (re.search("\.\s[A-Z]", lineParse))
                    line += lineParse[0:(x.end() - 1)] 
                    lineParse = lineParse[(x.end() - 1):]
            line += lineParse
            
        
        # If these are true, they may be used in the next line.
        prevLineEndedWithComma = re.search(r"\,\s*$", line)
        prevLineEndedWithPeriod = re.search(r"\.\s*$", line)
        prevLineEndedWithEllipses = re.search(r"\.\.\.\s*$", line)
        # preserve blanks, etc.
        currentText += ("\n" + line)

# After all lines are procesed, process the final chapter and extend it a smidge
currentText += "\n\n...\n"
fullAudioFile += createSegment(client, currentSettings, currentText)


fullAudioFile.export("spoken-word-output.mp3", format="mp3")

