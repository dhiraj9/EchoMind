import os
import csv
import shutil
import pyfiglet
import json
import wave
import moviepy
import pydub
import math
import sys
import vosk
import librosa
import soundfile as sf
import whisper_timestamped as whisper
from pydub import AudioSegment
from termcolor import colored
from allosaurus.app import read_recognizer
from vosk import Model, KaldiRecognizer, SetLogLevel
import subprocess as s
import string
from collections import Counter
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
import torch

# Controls some of the optional print statements
verbose = False
if "--verbose" in sys.argv:
    verbose = True

# Model chosen for Allosoarus -- see github page for more options
modelA_path = "uni2005"
# Model for Volk - see downloads page for more options
modelV_path = r"C:\Users\gdhir\Downloads\vosk-model-en-us-0.22-lgraph\vosk-model-en-us-0.22-lgraph"
# Model chose for whisper
modelW = whisper.load_model("medium")
# Load the pre-trained Wav2Vec 2.0 tokenizer (processor) and model
processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

if not os.path.exists(modelV_path):
    print(colored("Error - vosk model not found. Make sure model is downloaded and correct path is given to it", "red"))
    sys.exit(1)

if (verbose == False):
    SetLogLevel(-1)
else:
    SetLogLevel(0)

try:
    print("Loading model")
    modelV = Model(modelV_path)
    print("model loaded")

except:
    print(colored("Error: Could not instatiate Vosk model", 'red'))
    sys.exit(1)

try:
    modelA = read_recognizer(modelA_path)
except:
    print(colored("Error: Could not load Allosoarus model. Make sure you downloaded model before running this script.",
                  'red'))
    sys.exit(1)

# Recusively looks for all files in a given directory, and returns a list with a file path to them
def getFilesInFolder(k):
    ret = []
    for filename in os.listdir(k):
        if filename.startswith('DR'):
            f = os.path.join(k, filename)
            # checking if it is a file
            if os.path.isfile(f):
                ret += [f]
            else:
                ret += getFilesInFolder(f)
    return ret


# Slips wave files into smalle segments (15 secs atm)
class SplitWavAudioMubin():
    def __init__(self, folder, filename):
        self.folder = folder
        self.filename = filename
        self.filepath = folder + filename
        self.filepaths = []

        self.audio = AudioSegment.from_wav(self.filepath)

    def get_duration(self):
        return self.audio.duration_seconds

    def single_split(self, from_min, from_sec, to_min, to_sec, split_filename):
        t1 = (from_min * 60 + from_sec) * 1000
        t2 = (to_min * 60 + to_sec) * 1000
        split_audio = self.audio[t1:t2]
        split_audio.export(self.folder + split_filename, format="wav")
        self.filepaths.append(str(self.folder + split_filename))
        if (verbose):
            print("Audio seg split: " + self.folder + split_filename)

    def multiple_split(self, min_per_split, sec_per_split):
        total_mins = math.ceil(self.get_duration() / 60)
        last_sec = math.ceil(self.get_duration() % 60)
        for i in range(0, total_mins, min_per_split):
            if (i < (total_mins - 1)):
                for j in range(0, 60, sec_per_split):
                    split_fn = str(i) + ":" + str(j) + '_' + self.filename
                    self.single_split(i, j, i, j + sec_per_split, split_fn)
            else:
                for j in range(0, last_sec, sec_per_split):
                    split_fn = str(i) + ":" + str(j) + '_' + self.filename
                    self.single_split(i, j, i, j + sec_per_split, split_fn)

        if (verbose):
            if i == total_mins - min_per_split:
                print('All splited successfully :')
                for x in self.filepaths:
                    print(x)
                print("_" * 100)


# print start up message
print("=" * 46)
f = pyfiglet.Figlet(font="standard")
print(colored(f.renderText(" EchoMind"), 'cyan'))
print("UB Speech to text and phonemes project".center(46))
print("=" * 46)
dir_path = os.path.dirname(os.path.realpath(__file__))

# Get a list of files paths to all audio files inside InputAudioData
try:
    input = getFilesInFolder(dir_path+'\InputAudioData')
except:
    print("No audio Files found")
    input = []

# Create empty directorys for output data
if os.path.exists(dir_path + '/output'):
    shutil.rmtree(dir_path + '/output')
os.makedirs(dir_path + '/output')

# Loop through all audio files and process them acoordingly
for audio in input:
    file_name = os.path.basename(audio)
    file = os.path.splitext(file_name)
    file_location = audio.removeprefix(dir_path + '/InputAudioData')
    file_type = file[1]
    wavFile = dir_path + '/' + "output" + '/' + file[0] + "/" + file[0] + ".wav"
    os.makedirs(dir_path + '/' + "output" + '/' + file[0])
    f = open(dir_path + '/' + "output" + '/' + file[0] + "/filedata.txt", "a")
    csvGen = open(dir_path + '/' + "output" + '/' + file[0] + "/genData.csv", "a")
    csvWriter = csv.writer(csvGen)
    f.write("The file came from: " + file_location)

    # convert the file to a .wav if needed, and then copy the .wav to be part of the output
    if (file_type == ".wav"):
        if (verbose): print("Native Wave File:" + dir_path + '/' + "output" + '/' + file[0] + "/" + file_name)
        ob = sf.SoundFile(audio)
        if (format(ob.subtype) != "PCM_16"):
            data, samplerate = sf.read(audio)
            reduced_noise = nr.reduce_noise(y=data, sr=samplerate)
            normalized_data = librosa.util.normalize(reduced_noise)
            sf.write(dir_path + '/' + "output" + '/' + file[0] + "/" + file_name, normalized_data, samplerate, subtype='PCM_16')
        else:
            shutil.copyfile(audio, dir_path + '/' + "output" + '/' + file[0] + "/" + file_name)

    elif (file_type == ".mp3"):
        if (verbose): print("Converting Mp3 File:" + dir_path + '/' + "output" + '/' + file[0] + "/" + file_name)
        sound = pydub.AudioSegment.from_mp3(audio)
        sound.set_channels(1)
        sound = sound.set_frame_rate(16000)
        sound = sound.set_channels(1)
        sound.export(wavFile, format="wav")
    elif (file_type == ".mp4"):
        # may need to fix conversion - not sure if 16 bit wav or not
        if (verbose): print("Converting Mp4 File:" + dir_path + '/' + "output" + '/' + file[0] + "/" + file_name)
        video = moviepy.editor.VideoFileClip(audio, verbose=verbose, )
        # Extract the Audio
        audio = video.audio
        # Export the Audio
        if (verbose):
            audio.write_audiofile(wavFile)
        else:
            audio.write_audiofile(wavFile, logger=None)
    elif (file_type == '.flac'):
        data, samplerate = sf.read(audio)
        sf.write(wavFile, data, samplerate, subtype='PCM_16')

    conversion = AudioSegment.from_file(file=wavFile, format="wav")
    n_channels = conversion.channels
    if (n_channels > 1):
        try:
            sound = AudioSegment.from_wav(wavFile)
            sound = sound.set_channels(1)
            sound.export(wavFile, format="wav")
        except:
            print(colored("Error - trouble converting number of audio channels in file " + wavFile, "red"))
            sys.exit(1)

    with wave.open(wavFile) as input:
        # Read basic informaiton from the wavefile
        f.write("\n" + "_" * 15)
        f.write("\nNumber of channels  - " + str(n_channels))
        sample_width = input.getsampwidth()
        f.write("\nSample Width - " + str(sample_width))
        sample_freq = input.getframerate()
        f.write("\nFrame rate  - " + str(sample_freq))
        n_samples = input.getnframes()
        f.write("\nNumber of Frames  - " + str(n_samples))
        t_audio = round(n_samples / sample_freq, 3)
        f.write("\nlenght of Audio sample - " + str(t_audio))
        f.write("\nCompression type  - " + str(input.getcompname()) + " --- Orignal file type: " + file_type)

    # Break audio into 15 sec chuncks
    folder = dir_path + '\\' + "output" + '\\' + file[0] + "\\"
    file = file[0] + ".wav"
    split_wav = SplitWavAudioMubin(folder, file)
    split_wav.multiple_split(min_per_split=1, sec_per_split=15)

    split_files = split_wav.filepaths

    # for every audio segment do the following
    for seg in split_files:

        # file where data relating to audio seg should be stored
        subfile = seg[:-4]

        # audio file currently being processed
        audioSeg = os.path.join(subfile, os.path.basename(seg))
        transciption = []

        # file management
        subfile = subfile.replace('0:0_', '')
        os.makedirs(subfile)
        audioSeg = audioSeg.replace('0:0_', '')
        shutil.move(seg, audioSeg)

        # Whisper AI - get text data

        result_timestamped = modelW.transcribe(audioSeg, word_timestamps=True, language="en")

        with open(subfile + "/Whisper_transcipt.txt", "w") as text_file:
            text_file.write(result_timestamped["text"])
            transciption.append(result_timestamped["text"])

        with open(subfile + "/whisper_timestamped.txt", "w") as text_file:
            json_object = json.dumps(result_timestamped, indent=4)
            text_file.write(json_object)

        # Vosk
        wf = wave.open(audioSeg, "rb")
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
            print("Audio file must be WAV format mono PCM.")
            sys.exit(1)
        rec = KaldiRecognizer(modelV, wf.getframerate())
        rec.SetWords(True)
        rec.SetPartialWords(True)
        res = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res.append(json.loads(rec.Result()))

            else:
                rec.PartialResult()

        res.append(json.loads(rec.FinalResult()))

        with open(subfile + "/vosk_transcipt.txt", "w") as text_file:
            text_file.write(" ")
        with open(subfile + "/vosk_timestamped.txt", "w") as text_file:
            text_file.write(" ")
        with open(subfile + "/vosk_transcipt.txt", "a+") as text_file:
            temp = ""
            for result in res:
                text_file.write(result["text"] + "\n")
                temp += (result["text"] + " ")
            transciption.append(temp)
        with open(subfile + "/vosk_timestamped.txt", "a+") as text_file:
            for result in res:
                try:
                    for line in result['result']:
                        text_file.write(str(line) + "\n")
                except:
                    text_file.write("silence")

        # Wav2vec
        speech, sample_rate = soundfile.read(audioSeg)
        if sample_rate != 16000:
            raise ValueError("The wav2vec 2.0 model expects 16kHz audio. Please resample the audio.")
        input_values = processor(speech, return_tensors="pt", sampling_rate=sample_rate).input_values
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)
        text = transcription[0]
        with open(subfile + "/Wav2vec_transcipt.txt", "w") as text_file:
            transciption.append(text)
            text_file.write(text)

