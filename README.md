# MathyChords

A generative chord-voicing engine for guitar that expands small input note clusters into colourful, playable chord shapes using interval analysis, harmonic templates, and tuning-aware fingering algorithms.

## Overview

MathyChords transforms partial chord fragments of two to four notes into full voicings by:

- analysing the interval relationships between input notes
- decomposing those intervals into contiguous step sequences
- matching the results against a library of harmonic templates
- Comparing the intervals of templates against the cartesian products of the steps in the input
- selecting a potential template candidate
- creating a new theoretical chord by inserting complementary notes around the input
- checking whether a playable fingering within the selected tuning and fret-span constraints can be constructed
- filtering unsuitable results
- displaying all possible fingerings for the chord given the tuning set by the user

The goal is not traditional chord identification. MathyChords is designed for creative expansion and exploration, producing modern, open, and harmonically rich voicings suited to styles such as math rock, post-rock, and contemporary jazz.

## Current Features

- Interval-relationship analysis and contiguous interval decomposition
- Harmonic-template matching and candidate selection
- Consonance filtering
- Configurable guitar tunings
- Adjustable fret-span fingering constraints
- Tuning-aware fingering generation
- Graphical interface using PySide6
- Optional audio playback using FluidSynth
- Automated tests for the core generation logic

- ## Future Features
- Expand the template library
- continue to refine fingering construction algorithm
- replacing Fluidsynth with an original, light-weight audio handling engine

## Technology

- Python
- PySide6
- FluidSynth
- File-based harmonic-template and interval data

## Status

MathyChords is a functional prototype still under development. 


