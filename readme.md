# MathyChords

A generative chord-voicing engine for guitar that expands small input note clusters into colourful, playable chord shapes using interval analysis, harmonic templates, and tuning-aware fingering algorithms.

## Demo
https://github.com/user-attachments/assets/865882e0-6751-4a62-a7c8-5881a93b0aee


## Overview

MathyChords transforms partial chord fragments of two to four notes into full voicings by:

* analysing the interval relationships between input notes
* decomposing those intervals into contiguous step sequences
* matching the results against a library of harmonic templates
* comparing the intervals of templates against the Cartesian products of the steps in the input
* selecting a potential template candidate
* creating a new theoretical chord by inserting complementary notes around the input
* checking whether a playable fingering within the selected tuning and fret-span constraints can be constructed
* filtering unsuitable results
* displaying all possible fingerings for the chord given the tuning set by the user

The goal is not traditional chord identification. MathyChords is designed for creative expansion and exploration, producing modern, open, and harmonically rich voicings suited to styles such as math rock, post-rock, and contemporary jazz.

## Current Features

* Interval-relationship analysis and contiguous interval decomposition
* Harmonic-template matching and candidate selection
* Consonance filtering
* Configurable guitar tunings
* Adjustable fret-span fingering constraints
* Tuning-aware fingering generation
* Graphical interface using PySide6
* Audio playback using FluidSynth


## Requirements

### Python Dependencies

* Python 3
* PySide6 6.11.1
* pyFluidSynth 1.4.0

Python dependencies can be installed using:

`pip install -r requirements.txt`

### Audio Dependencies

MathyChords currently requires FluidSynth and the Arachno SoundFont for audio playback.

* [FluidSynth](https://www.fluidsynth.org/download/) - download the appropriate FluidSynth binaries for your system.
* [Arachno SoundFont (SF2)](https://www.arachnosoft.com/main/download.php?id=soundfont-sf2) - download the SF2 version of the Arachno SoundFont.

For the current Windows implementation, place the FluidSynth binaries in:

`fluidsynth-bin/`

Place the downloaded Arachno SoundFont at:

`data/arachno.sf2`

These third-party audio files are not included in this repository and must be downloaded separately.

## Technology

* Python
* PySide6
* FluidSynth / pyFluidSynth
* File-based harmonic-template and interval data

## Future Features

* Expand the harmonic-template library
* Continue refining the fingering-construction algorithm
* Replace FluidSynth with an original lightweight audio-handling engine

## Status

MathyChords is a functional prototype currently under development.
