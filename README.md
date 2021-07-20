# wendletrap
A script that creates stepmania files from midi data

## Setup
This script was developed using python 3.9.1.

Its only dependency is [click](https://click.palletsprojects.com/en/8.0.x/quickstart/).

## How to use
Run
```
python wendletrap.py --filename file.wendle
```
with `file.wendle` replaced with your .wendle file.

.wendle is a text file format made up for this script. Check `template.wendle` to see the exact format. It lists most of the properties and metadata that go into the stepfile verbatim (check out the [stepfile format](https://github.com/stepmania/stepmania/wiki/sm) to see the full list). Then in addition you'll need a name for the sm file being created and the names of midi files to be fed in.

I strongly recommend creating a songs folder and within that folder creating a folder for each song. Each song folder will contain a wendle file, one of more midi files, an audio file, and some image files.

### MIDI Format

wendletrap maps specific MIDI pitches to different stepmania notes. The mapping is:

Note Type | <- | v | ^ | ->
--------- | -- | - | - | --
Normal | 36 (C1) | 39 (D#1) | 42 (F#1) | 45 (A1)
Hold | 37 (C#1) | 40 (E1) | 43 (G1) | 46 (A#1)
Roll | 38 (D1) | 41 (F1) | 44 (G#1) | 47 (B1)

The length of the midi note will be used to set the length of hold and roll notes.

A wendletrap-designed MIDI file will not be especially musical.

Tempo and Time Signature changes will be pulled from the MIDI file. Time signatures must be over 4.
