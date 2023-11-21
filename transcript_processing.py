#!/usr/bin/env python
# coding: utf-8

# In[70]:


import os
from collections import Counter
from difflib import SequenceMatcher
from spellchecker import SpellChecker
from transformers import pipeline

def align_transcripts(transcripts):
    base_transcript = transcripts[0]
    aligned_transcripts = [base_transcript.split()]
    for transcript in transcripts[1:]:
        match = SequenceMatcher(None, base_transcript, transcript)
        aligned_transcript = []
        for opcode in match.get_opcodes():
            if opcode[0] == 'equal':
                aligned_transcript.extend(transcript[opcode[3]:opcode[4]].split())
            elif opcode[0] == 'replace' or opcode[0] == 'insert':
                aligned_transcript.extend(['<blank>'] * (opcode[2] - opcode[1]))
        aligned_transcripts.append(aligned_transcript)
    return aligned_transcripts

def spell_correct_transcript(transcript):
    spell = SpellChecker()
    corrected_words = []
    for word in transcript.split():
        corrected_word = spell.correction(word)
        if corrected_word:
            corrected_words.append(corrected_word)
        else:
            corrected_words.append(word)
    return ' '.join(corrected_words)

def vote_on_words(aligned_transcripts):
    final_transcript = []
    for word_tuple in zip(*aligned_transcripts):
        word_counts = Counter(word_tuple)
        if word_counts.most_common(1)[0][0] != '<blank>':
            final_transcript.append(word_counts.most_common(1)[0][0])
        else:
            final_transcript.append(word_counts.most_common(2)[1][0])
    return ' '.join(final_transcript)

def combine_transcripts(transcripts):
    aligned_transcripts = align_transcripts(transcripts)
    combined_transcript = vote_on_words(aligned_transcripts)
    combined_transcript = combined_transcript.replace('<blank> ', '')
    spell_corrected_transcript = spell_correct_transcript(combined_transcript)
    return spell_corrected_transcript

def read_transcript(file_path):
    with open(file_path, 'r') as file:
        return file.read()

root_dir = "C:\\Users\\gdhir\\Downloads\\EchoMind-main\\EchoMind-main\\output"

for root, dirs, files in os.walk(root_dir):
    if 'DR' in root:  
        print(f"Processing directory: {root}")
        for sub_dir in dirs:
            if sub_dir.startswith('DR'):
                transcripts = []
                transcript_files = ['Wav2vec_transcipt.txt', 'vosk_transcipt.txt', 'Whisper_transcipt.txt']
                for t_file in transcript_files:
                    file_path = os.path.join(root, sub_dir, t_file)
                    if os.path.exists(file_path):
                        transcripts.append(read_transcript(file_path))
                    else:
                        print(f"Missing transcript file: {file_path}")

                if len(transcripts) == 3:  
                    combined_transcript = combine_transcripts(transcripts)
                    combined_file_path = os.path.join(root, sub_dir, 'combined.txt')
                    with open(combined_file_path, 'w', encoding='utf-8') as file:
                        file.write(combined_transcript)
                    print(f"Combined transcript written to {combined_file_path}")
                else:
                    print(f"Skipping directory {sub_dir} due to missing transcripts")

print("Transcripts combined successfully.")

