# Mathy-Chords
A generative chord-voicing engine for guitar that expands small input note clusters into colourful chord shapes using contiguous interval decomposition, template referencing, and tuning-aware fingering algorithms.

## Overview
Mathy Chords aims to transform partial chord fragments (2–4 notes) into full voicings by:

- analysing the interval relationships in the input
- matching them to a library of harmonic templates
- selecting a suitable template candidate
- constructing a physically playable fingering based on the selected tuning and fret span limits.

The goal is not traditional chord identification, but 'creative expansion and exploration'; producing modern, open, and harmonically rich voicings suitable for styles like math rock, post-rock, and contemporary jazz.

## Current Components
The following modules are planned or partially implemented:

- Interval decomposition engine: breaks input intervals into contiguous step sequences.
- Template engine: matches decompositions against a library of harmonic templates.
- Selection system: chooses a viable template candidate.
- Tuning and note utilities: core functions for pitch-class math and tuning awareness.



## Future Components
My current plans include:

- updating the selection system to fallback to select a new candidate when a rare unmappable shape is generated.
- Implement final v1 fingering generator prototype: maps template steps onto real guitar strings within playability constraints.
- add note doubling where appropriate (open-sounding shapes, drone notes, etc.) 
- Provide both a CLI prototype and a later GUI/app interface.

## Status
Development is still at the prototype stage with work on the selection algorithm currently underway.

