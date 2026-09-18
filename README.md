# MathyChords

A generative chord-voicing engine for guitar that expands small input note clusters into colourful, playable chord shapes using interval analysis, harmonic templates, and tuning-aware fingering algorithms.

## Overview

MathyChords transforms partial chord fragments of two to four notes into full voicings by:

- analysing the interval relationships between input notes
- decomposing those intervals into contiguous step sequences
- matching the results against a library of harmonic templates
- filtering unsuitable or overly dissonant results
- selecting an appropriate template candidate
- constructing a playable fingering within the selected tuning and fret-span constraints

The goal is not traditional chord identification. MathyChords is designed for creative expansion and exploration, producing modern, open, and harmonically rich voicings suited to styles such as math rock, post-rock, and contemporary jazz.

## Current Features

- Interval-relationship analysis and contiguous interval decomposition
- Harmonic-template matching and candidate selection
- Consonance filtering
- Configurable guitar tunings
- Adjustable fret-span fingering constraints
- Tuning-aware fingering generation
- Graphical chord input using PySide6
- Optional audio playback using FluidSynth
- Automated tests for the core generation logic

## Technology

- Python
- PySide6
- FluidSynth
- File-based harmonic-template and interval data

## Status

MathyChords is a functional prototype under active development. The core chord-generation pipeline and graphical interface are working, while the selection and fingering algorithms continue to be refined.


