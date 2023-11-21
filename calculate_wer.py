#!/usr/bin/env python
# coding: utf-8

# In[71]:


import os
import jiwer

def calculate_wer(reference, hypothesis):
    """
    Calculate the Word Error Rate (WER) between reference and hypothesis texts.
    """
    transformation = jiwer.Compose([
        jiwer.ToLowerCase(),
        jiwer.Strip(),
        jiwer.RemoveMultipleSpaces(),
        jiwer.RemovePunctuation(),
        jiwer.ReduceToListOfListOfWords(word_delimiter=" ")
    ])
    return jiwer.wer(reference, hypothesis, truth_transform=transformation, hypothesis_transform=transformation)

echomind_output_dir = "C:\\Users\\gdhir\\Downloads\\EchoMind-main\\EchoMind-main\\output"
timit_tests_dir = "C:\\Users\\gdhir\\Downloads\\TimitDataset\\TimitDataset\\tests"
total_wer = 0
count = 0
for root, dirs, files in os.walk(echomind_output_dir):
    if 'DR' in os.path.basename(root) and 'DR' in os.path.basename(os.path.dirname(root)):
        for file in files:
            if file == 'combined.txt':
                combined_file_path = os.path.join(root, file)
                dr_folder = os.path.basename(root)
                reference_file_path = os.path.join(timit_tests_dir, dr_folder, 'text.txt')

                if os.path.exists(combined_file_path) and os.path.exists(reference_file_path):
                    with open(combined_file_path, 'r', encoding='utf-8') as c_file, open(reference_file_path, 'r', encoding='utf-8') as r_file:
                        combined_text = c_file.read()
                        reference_text = r_file.read()

                    wer = calculate_wer(reference_text, combined_text)
                    total_wer += wer
                    count += 1
                else:
                    print(f"Missing files for directory: {dr_folder}")

if count > 0:
    average_wer = total_wer / count
    print(f"Average WER for all transcripts: {average_wer * 100:.2f}%")
else:
    print("No transcripts processed.")

