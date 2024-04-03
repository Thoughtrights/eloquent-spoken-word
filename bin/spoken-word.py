#!/usr/bin/python3

# Copyright (c) 2024
# clay@thoughtrights.com
# Thoughtrights

import os
import sys
import getopt
from openai import OpenAI
from pydub import AudioSegment
import re
import random

random.seed()

helpText = "\n" + sys.argv[0] + """ usage options:
\t --input=<filename> | --stdin
\t --output=<filename>
\t[--voice={alloy,echo,fable,onyx,nova,shimmer}] [--speed=<multiplier>]
\t[--model={tts-1,tts-1-hd}] [--delay=<real-seconds>] [--filler=<real-percent>]
\t[--verbose]
\t[--help]

"""

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
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

def verboseOutput (msg):
    if (verbose):
        print(msg)
    sys.stdout.flush()

def errorOutput (msg):
    print(msg)
    sys.stdout.flush()

    
def createSegment (client, settings=defaultSettings, dialog=''):

    tempAudioFile = "tmp_chapter.mp3"

    verboseOutput(f"Working on chapter \"{settings['CHAPTER']}\".")
    verboseOutput(f"Adding {settings['DELAY']} seconds of silence.")
    audioSegment = AudioSegment.silent(duration= (settings['DELAY'] * 1000)) # DELAY is secs
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



verbose = False
stdin = False
inputFile = ''
outputFile = ''
try:
    opts, args = getopt.getopt(
        sys.argv[1:],
        "iovh",
        ["input=", "output=", "verbose", "stdin", "voice=", "speed=", "model=", "delay=", "filler=", "help"]
    )
except getopt.GetoptError:
    print(help_text)
    sys.exit(2)
    
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print(helpText)
        sys.exit()
    elif opt in ("-i", "--input"):
        inputFile = arg
    elif opt in ("-o", "--output"):
        outputFile = arg
    elif opt in ("-v", "--verbose"):
        verbose = True
    elif opt in ("--stdin"):
        stdin = True
    elif opt in ("--voice"):
        if (arg in allowedVoices):
            defaultSettings['VOICE'] = arg
        else:
            errorOutput(f"Error: Unknown voice, {arg}.") 
            print(helpText)
            sys.exit
    elif opt in ("--speed"):
        if (float(arg) >= minSpeed and float(arg) <= maxSpeed):
            defaultSettings['SPEED'] = float(arg)
        else:
            errorOutput(f"Error: Bad speed value, {arg}.") 
            print(helpText)
            sys.exit
    elif opt in ("--delay"):
        if (float(arg) >= minDelay and float(arg) <= maxDelay):
            defaultSettings['DELAY'] = float(arg)
        else:
            errorOutput(f"Error: Bad delay value, {arg}.") 
            print(helpText)
            sys.exit
    elif opt in ("--filler"):
        if (float(arg) >= minFiller and float(arg) <= maxFiller):
            defaultSettings['FILLER'] = float(arg)
        else:
            errorOutput(f"Error: Bad filler value, {arg}.") 
            print(helpText)
            sys.exit
    elif opt in ("--model"):
        if (arg in allowedModels):
            defaultSettings['MODEL'] = arg
        else:
            errorOutput(f"Error: Unknown model, {arg}.") 
            print(helpText)
            sys.exit

verboseOutput('Verbosity mode on.')
if (stdin and inputFile != ''):
    errorOutput(f"Error: both a specified input file and stdin were specified.") 
    print(helpText)
    sys.exit
if (stdin is False and inputFile == ''):
    errorOutput(f"Error: no file input or stdin specified.") 
    print(helpText)
    sys.exit
if (outputFile == ''):
    errorOutput(f"Error: no specified output file.") 
    print(helpText)
    sys.exit

# GET INPUT
document = ''
if (stdin):
    for line in sys.stdin:
        document += line
else:
    fileHandle = open(inputFile, "r")
    for line in fileHandle:
        document += line


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
                verboseOutput(f"THE DIRECTIVE is {directive}.") 
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

fullAudioFile.export(outputFile, format="mp3")

