# Transcript Processing and WER Calculation

## Description

This project provides a set of Python scripts designed to process audio transcripts and calculate the Word Error Rate (WER) for speech recognition tasks. It includes functions for aligning multiple transcripts, correcting spelling, combining the best guesses from different transcripts, and evaluating the performance of speech-to-text models against a reference transcript.

## Features

- **Transcript Alignment**: Aligns multiple transcripts from different sources.
- **Spelling Correction**: Corrects spelling errors in transcripts using the `spellchecker` library.
- **Transcript Combination**: Combines multiple transcripts into a single, more accurate version.
- **WER Calculation**: Calculates the Word Error Rate (WER) to evaluate the accuracy of the combined transcripts against a reference.

## Installation

You'll need to install some dependencies:

```bash
pip install spellchecker transformers jiwer
```

## Usage

### Aligning and Combining Transcripts

1. Place your transcript files in the specified directory structure.
2. Run the transcript processing script:

   ```python
   python transcript_processing.py
   ```

   This script will process all directories and combine transcripts into a single file named 'combined.txt'.

### Calculating WER

1. Ensure you have your reference transcripts in the specified directory.
2. Run the WER calculation script:

   ```python
   python calculate_wer.py
   ```

   This will output the average Word Error Rate for your transcripts.
