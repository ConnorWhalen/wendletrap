# wendletrap
A script that creates stepmania and clone hero files from midi data.

There are editors out there that make charting easier than editing midi, but none of them run on MacOS : (. Wendletrap lets you create charts in your daw or piano roll tool of choice. It requires purpose-built midi data and won't work with actual midi tracks from songs.

I recommend using a visualizer like [Chart Hero](https://nb48.github.io/chart-hero/) or Stepmania's built-in preview for reviewing your work, since it's hard not to make mistakes working this way.

## Setup
This script was developed using python 3.9.1.

Its dependencies are [click](https://click.palletsprojects.com/en/8.0.x/quickstart/) and [pyyaml](https://pyyaml.org/).

## How to use
Run
```
python wendletrap.py --filename file.wendle --filetype t
```
with `file.wendle` replaced with your .wendle file and "t" replaced with either "sm" or "chart" for the output file type.

.wendle is a text file format made up for this script. Check `template.wendle` to see the exact format. It lists most of the properties and metadata that go into stepfiles verbatim (check out the [stepfile format](https://github.com/stepmania/stepmania/wiki/sm) to see the full list). It has some additional fields needed for chart files which i've noted in the template (I haven't found documentation on the clone hero file format yet :( ).

I strongly recommend creating a songs folder and within that folder creating a folder for each song. Each song folder will contain a wendle file, one of more midi files, an audio file, and some image files.

### MIDI Format

A wendletrap-designed MIDI file will not be especially musical.

Tempo and Time Signature changes will be pulled from the MIDI file.

#### Stepmania (sm) Files

wendletrap maps specific MIDI pitches to different stepmania notes. The mapping is:

Note Type | <- | v | ^ | ->
--------- | -- | - | - | --
Normal | 36 (C1) | 39 (D#1) | 42 (F#1) | 45 (A1)
Hold | 37 (C#1) | 40 (E1) | 43 (G1) | 46 (A#1)
Roll | 38 (D1) | 41 (F1) | 44 (G#1) | 47 (B1)

The length of the midi note will be used to set the length of hold and roll notes.

#### Clone Hero (chart) Files

The mapping for clone hero is:

Note Type | Purple | Green | Red | Yellow | Blue | Orange | HOPO | Tap | Star Power
--------- | ------ | ----- | --- | ------ | ---- | ------ | ---- | --- | ----------
Normal | 36 (C1) | 38 (D1) | 40 (E1) | 42 (F#1) | 44 (G#1) | 46 (A#1) | 48 (C2) | 49 (C#2) | x
Hold | 37 (C#1) | 39 (D#1) | 41 (F1) | 43 (G1) | 45 (A1) | 47 (B1) | x | x | 50 (D2)

The length of the midi note will be used to set the length of hold notes and the star power region.

HOPOs and taps are done by pairing a normal/hold note with the HOPO/tap note.

