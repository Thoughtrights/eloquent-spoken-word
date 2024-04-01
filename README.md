# eloquent-spoken-word


## Purpose & Background

I don't love the sound of my own voice. I have been using OpenAI's
APIs. Nested in there was Whisper and its [Neural] TTS endpoint. I
thought it was neat.

OpenAI's text to speech has good voices. However I found myself going
through some contortions to get the result I wanted. These were the
problems I decided to solve for:

* IMHO the pacing is fast. There is no reliable way to introduce
  pauses or breaks. Ellipses, punctuation, and line breaks can have a
  useful effect. Sometimes. "[Pause]" can sometimes work. There needed
  to be a way to let the listener catch their breath because the TTS
  speaker was never going to take a break.

* The token limits which limit how much can be thrown at the model at
  one time can get in the way pretty easily. So you will need to chunk
  your requests.

* For most any speech, there is a need for pacing changes; Portions of a
  read document or message should be faster and portions should be slower.

* Changing speakers - sometimes in the same paragraph - is very
  useful. Certainly within a dialog.

* I found myself adding occassional "filler words" like "uh" to
  enforce and accentuate the pauses. Then I realized it's just more
  natual to have filler words in different portions of a document for
  its pacing and feel. Then I realized it's terrible to litter the
  document with filler words when it really is based on someone
  reading the document and it should not be in the doc itself.

I created a Simple OpenAI TTS Markup Language to address the above
points. The BNF for it is in `simple-openai-tts-markup-language.bnf`.


## Directive Use

Have a standard text document. Add in additional lines on their own at
each beginning of a chapter or change in speech, or break in speech. The format is generally:

`### CHAPTER optional text string here, SPEED 1.0, VOICE fable, DELAY 2.5, FILLER 0.2, MODEL tts-1`

Where:

`SPEED` is slow to fast and between 0.25 and 4.0. The default and
recommended value is 1.0 because other levels can introduce some
distortion.

`VOICE` is "alloy", "echo", "fable", "onyx", "nova", or "shimmer"

`MODEL` is "tts-1", "tts-1-hd". The default is "tts-1" and cheap. You
also don't want to flip between the two.

`DELAY` is the number of seconds to pause before starting this new
segment. It can be from 0 to 3600.

`FILLER` is the percentile chance 0 to 1 where 0.2 is a 20% chance to
add a filler word at a sentence break or ellipse.

All of the segments are optional however if one is not specified then
the default value will be used. For this reason you should always
supply a VOICE.

Or for a gross amount of detail you can read https://github.com/Thoughtrights/eloquent-spoken-word/blob/main/simple-openai-tts-markup-language.bnf


## Future Work

### Other TTS Systems

I did try some other deterministic TTSs out there. Some have been out
there for 40 years. Most just have some base augmentation. I have used
MacOS's `say` in scripts for a long while. It's great for what it is.

I do mean to try AWS's Amazon Polly.


### Use a Logging System

I have various print statements grouped. I might want to change these
to logging and log levels. Maybe.


### Negative Values for the DELAY directive.

It would be cool to support NEGATIVE values for DELAY that instead of
adding a silent segment, it would overlay the new segment on the end
(minus offset) of the main segment. But for now we have a guarantee
the DELAY is present and is greater or equal to 0. It is truly silent
so we do not expect audio "pops" from concatenation.


### OpenAI's MP3 Header && Do It All In Memory

OpenAI gives us a full mp3. We need to strip that. I'm using and
abusing pydub AudioSegment. I really should look into doing it all in
memory instead of these messy disk I/O iterations.

OpenAI also allows for a `response_format=pcm` which returns "similar
to WAV but containing the raw samples in 24kHz (16-bit signed,
low-endian), without the header."

`ffmpeg`, the super comprehensive and amazing system that also happens
to support AudioSegment does support "PCM signed 16-bit little-endian"
among thousands of formats. It is not clear what if any identifer
describes that PCM format.
https://www.ffmpeg.org/general.html#File-Formats


### Speaking of Memory

I imagine there could be a need to concatenate in files because the
audio may become too large for RAM. This isn't the case in my examples
but I do wonder about it. And it makes me wonder if I would instead go
slightly the other way regarding "do it all in memory".
 

### Stereo Audio with Weighted Segments

Audio is in stereo. But it's basically mono. It would be cool to
support LEFT and RIGHT stereo weights for speakers instead of just
mono. The directive would be something like LEFT and then a positive
or negative value. Or RIGHT with a value.

Note: It would get awkwardly complex to mix (without
pre-pre-processing) to support a negative value for DELAY *and*
LEFT/RIGHT direction.


### Command Line

Add command line options. Support file input and file output
names. Support STDIN && STDOUT. Support default overrides for all the
options. Support changes to the filler word list.


### Filler Words

I have a `fillerWordsShort` and `fillerWordsLong` but I'm not using
`fillerWordsLong` anywhere. I haven't even tried them. When I put them
in, I was thinking that they would be useful in larger fills. I do
need to try them out and either cut them entirely or see where I can
use them.


## Caveats

* I did consider leveraging subtitling and captioning formats. But
  they were a bigger project than I was looking for. And they're more
  about where to shove text instead what to do with it. That said,
  they could be an interesting data source and have applicability for
  Accessibility.

* OpenAI's TTS and model is tailored to English.

* I need to tweak my filler-word fill logic to skip some fill opportunities.

* I also did consider the Speech Synthesis Markup Language (SSML), but
  that is way more heavyweight than I was looking for. And honestly,
  XML is not where I want to be. There are plenty of neat things in
  there (like BREAK, PROSODY, and EMPHASIS). It might be worth going
  back and implementing some of them.
  https://www.w3.org/TR/speech-synthesis11/




