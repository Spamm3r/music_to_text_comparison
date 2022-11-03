import speech_recognition as sr
import os
import math
import jiwer
from pydub import AudioSegment
from pydub.silence import split_on_silence
import azure.cognitiveservices.speech as speechsdk


class Utilities:
    def __init__(self):
        # self.wit_key = '6DXD7C2F3PH2ELYPNUDS73NLLJQK4SUD'
        self.wit_key = '6TRRUSXN7HAHU2Q5BLC6B33L7GWCYQ3D'
        # 1 self.client_id = 'MvFliQofevWN9IiQz4kmtA=='
        self.client_id = 'WUR8hl8ENATJUIe9VaSkPg=='
        # 1 self.client_key = 'ckmfy9EXz54mXbP_gPrazJT0b3gZtbCN4-x5CbB2QUABJR1QtlMQKgDADbflTkbac5FqaNjCM5ADFIRlM4_LKg=='
        self.client_key = 'dj2WMYnxu_tQi5f7ll-e8yYKJW7p2UkQhUM-GGDO2INbvaRxmDX4fIzWhXhkre1tfuzJ8DlTwLj-y6McwUi9TA=='
        self.music_path_dict = ['blue_sky',
                                'gangsta_',
                                'last_cell',
                                'never_gonna_give_you_up',
                                'over_the_rainbow']
        self.transformation = jiwer.Compose([
            jiwer.ToLowerCase(),
            jiwer.RemoveWhiteSpace(replace_by_space=True),
            jiwer.RemoveMultipleSpaces(),
            jiwer.ReduceToListOfListOfWords(word_delimiter=" ")
        ])

    def experiment_one_chunks(self):
        music_path_dict = ['experiment_one/mus_vocals/blue_sky_vocals.wav',
                           'experiment_one/mus_vocals/gangsta_vocals.wav',
                           'experiment_one/mus_vocals/last_cell_vocals.wav',
                           'experiment_one/mus_vocals/never_gonna_give_you_up_vocals.wav',
                           'experiment_one/mus_vocals/over_the_rainbow_vocals.wav']

        gt_path_dict = ['experiment_one/lyr/blue_sky.txt',
                        'experiment_one/lyr/gangsta.txt',
                        'experiment_one/lyr/last_cell.txt',
                        'experiment_one/lyr/never_gonna_give_you_up.txt',
                        'experiment_one/lyr/over_the_rainbow.txt']

        libs = ['sphinx',
                'bing',
                'wit.ai',
                'houndify']

        for i in range(5):
            print(self.music_path_dict[i])
            for j in range(4):
                print(libs[j])
                self.silence_based_conversion(music_path_dict[i], gt_path_dict[i], self.transformation, j, False)

    def silence_based_conversion(self, path, gt_path, transformation, library_number, additional_logging) -> None:
        song = AudioSegment.from_wav(path)

        with open(gt_path, 'r', encoding="utf8") as hyp:
            ground_truth = hyp.read()
        ground_truth = ground_truth.replace("\n", " ")
        result = ""
        algorithm = ""
        if additional_logging:
            print("Splitting into chunks...")
        chunks = split_on_silence(song, silence_thresh=math.floor(song.dBFS - 5), min_silence_len=1200)

        try:
            os.mkdir('trash/audio_chunks')
        except FileExistsError:
            if additional_logging:
                print("Cleaning dir...")
            for root, dirs, files in os.walk('trash/audio_chunks'):
                for file in files:
                    os.remove(os.path.join(root, file))

        if additional_logging:
            print("Creating chunks...")
        i = 0
        for chunk in chunks:
            chunk_silent = AudioSegment.silent(duration=10)
            audio_chunk = chunk_silent + chunk + chunk_silent
            if additional_logging:
                print("saving chunk{0}.wav".format(i))
            audio_chunk.export("./trash/audio_chunks/chunk{0}.wav".format(i), bitrate='192k', format="wav")
            filename = 'trash/audio_chunks/chunk' + str(i) + '.wav'
            if additional_logging:
                print("Processing chunk " + str(i))
            file = filename
            r = sr.Recognizer()
            with sr.AudioFile(file) as source:
                audio_listened = r.listen(source)
                try:
                    if library_number == 0:
                        result += r.recognize_sphinx(audio_listened)

                    if library_number == 1:
                        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                                               region=os.environ.get('SPEECH_REGION'))
                        speech_config.speech_recognition_language = "en-US"
                        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=False, filename=file)
                        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                                       audio_config=audio_config)
                        result += str(speech_recognizer.recognize_once())

                    if library_number == 2:
                        result += r.recognize_wit(audio_listened, key=self.wit_key)

                    if library_number == 3:
                        result += r.recognize_houndify(audio_listened, client_id=self.client_id,
                                                       client_key=self.client_key)
                except sr.UnknownValueError:
                    if additional_logging:
                        print("Could not understand audio" + filename)

                except sr.RequestError as e:
                    print("Could not request results. check your internet connection")
            i += 1
        wer = jiwer.wer(ground_truth, result, truth_transform=transformation, hypothesis_transform=transformation)
        print(algorithm + str(round(wer, 3) * 100) + "%" + " ### " + str(wer))

    def experiment_one_full(self):
        music_path_dict = ['experiment_one/mus/blue_sky.wav',
                           'experiment_one/mus/gangsta.wav',
                           'experiment_one/mus/last_cell.wav',
                           'experiment_one/mus/never_gonna_give_you_up.wav',
                           'experiment_one/mus/over_the_rainbow.wav']

        gt_path_dict = ['experiment_one/lyr/blue_sky.txt',
                        'experiment_one/lyr/gangsta.txt',
                        'experiment_one/lyr/last_cell.txt',
                        'experiment_one/lyr/never_gonna_give_you_up.txt',
                        'experiment_one/lyr/over_the_rainbow.txt']

        for i in range(5):
            print(self.music_path_dict[i])
            self.full_conversion(music_path_dict[i], gt_path_dict[i], self.transformation, False)

    def experiment_one_vocals(self):
        music_path_dict = ['experiment_one/mus_vocals/blue_sky_vocals.wav',
                           'experiment_one/mus_vocals/gangsta_vocals.wav',
                           'experiment_one/mus_vocals/last_cell_vocals.wav',
                           'experiment_one/mus_vocals/never_gonna_give_you_up_vocals.wav',
                           'experiment_one/mus_vocals/over_the_rainbow_vocals.wav']

        gt_path_dict = ['experiment_one/lyr/blue_sky.txt',
                        'experiment_one/lyr/gangsta.txt',
                        'experiment_one/lyr/last_cell.txt',
                        'experiment_one/lyr/never_gonna_give_you_up.txt',
                        'experiment_one/lyr/over_the_rainbow.txt']

        for i in range(5):
            print(self.music_path_dict[i])
            self.full_conversion(music_path_dict[i], gt_path_dict[i], self.transformation, False)

    def full_conversion(self, path, gt_path, transformation, additional_logging) -> None:
        r = sr.Recognizer()
        algorithm = ""
        with open(gt_path, 'r', encoding="utf8") as hyp:
            ground_truth = hyp.read()
        ground_truth = ground_truth.replace("\n", " ")
        with sr.AudioFile(path) as source:
            audio_listened = r.record(source)
            for i in range(4):
                result = ""
                wer_value = 0
                try:
                    if i == 0:
                        algorithm = "Sphinx: "
                        result += r.recognize_sphinx(audio_listened)

                    if i == 1:
                        algorithm = "Bing: "
                        speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'),
                                                               region=os.environ.get('SPEECH_REGION'))
                        speech_config.speech_recognition_language = "en-US"
                        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=False, filename=path)
                        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config,
                                                                       audio_config=audio_config)
                        result += str(speech_recognizer.recognize_once())

                    if i == 2:
                        algorithm = "Wit: "
                        result += r.recognize_wit(audio_listened, key=self.wit_key)

                    if i == 3:
                        algorithm = "Houndify: "
                        result += r.recognize_houndify(audio_listened, client_id=self.client_id,
                                                       client_key=self.client_key)

                except sr.UnknownValueError:
                    if additional_logging:
                        print("Could not understand audio")

                except sr.RequestError as e:
                    print("Could not request results. check your internet connection")

                if additional_logging:
                    print(result)
                wer_value = jiwer.wer(ground_truth, result, truth_transform=transformation,
                                      hypothesis_transform=transformation)
                print(algorithm + str(wer_value * 100) + "%" + " ### " + str(wer_value))

    def experiment_two_full(self):
        music_path_dict = ['experiment_two/mus/blue_sky.wav',
                           'experiment_two/mus/gangsta.wav',
                           'experiment_two/mus/last_cell.wav',
                           'experiment_two/mus/never_gonna_give_you_up.wav',
                           'experiment_two/mus/over_the_rainbow.wav']

        gt_path_dict = ['experiment_two/lyr/blue_sky.txt',
                        'experiment_two/lyr/gangsta.txt',
                        'experiment_two/lyr/last_cell.txt',
                        'experiment_two/lyr/never_gonna_give_you_up.txt',
                        'experiment_two/lyr/over_the_rainbow.txt']

        for i in range(5):
            print(self.music_path_dict[i])
            self.full_conversion(music_path_dict[i], gt_path_dict[i], self.transformation, True)

    def experiment_two_vocals(self):
        music_path_dict = ['experiment_two/mus_vocals/blue_sky_vocals.wav',
                           'experiment_two/mus_vocals/gangsta_vocals.wav',
                           'experiment_two/mus_vocals/last_cell_vocals.wav',
                           'experiment_two/mus_vocals/never_gonna_give_you_up_vocals.wav',
                           'experiment_two/mus_vocals/over_the_rainbow_vocals.wav']

        gt_path_dict = ['experiment_two/lyr/blue_sky.txt',
                        'experiment_two/lyr/gangsta.txt',
                        'experiment_two/lyr/last_cell.txt',
                        'experiment_two/lyr/never_gonna_give_you_up.txt',
                        'experiment_two/lyr/over_the_rainbow.txt']

        for i in range(5):
            print(self.music_path_dict[i])
            self.full_conversion(music_path_dict[i], gt_path_dict[i], self.transformation, True)

