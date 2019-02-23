#-*- coding:utf-8 -*-
import re
import argparse
import hashlib
from google.cloud import texttospeech

def md5sum_str(text):
    hash = hashlib.md5()
    hash.update(text)
    return hash.hexdigest()

def isEnglish(argText) :
    english_check = re.compile(r'[a-zA-Z0-9$@$!%*?&#^-_. +]+')
    if english_check.match(argText) :
        return True
    else :
        return False

def getLangCode(argText) :
    if isEnglish(argText) :
        return 'en-US'

    return 'ko-KR'

def getSpeechName(langCode, gender) :
    if gender == "FEMALE" :
        if langCode == 'en-US' :
            return 'en-US-Wavenet-F' # or E?
        else:
            return 'ko-KR-Wavenet-A'
    else :
        if langCode == 'en-US' :
            return 'en-US-Wavenet-B'
        return 'ko-KR-Wavenet-C'

def getSSmlVoiceGender(gender) :
    if gender == "FEMALE" :
        return texttospeech.enums.SsmlVoiceGender.FEMALE
    elif gender == "MALE" :
        return texttospeech.enums.SsmlVoiceGender.MALE

    return texttospeech.enums.SsmlVoiceGender.NEUTRAL

def convertSpeech(argText, gender, output = None):
    # [START tts_quickstart]
    """Synthesizes speech from the input string of text or ssml.
    Note: ssml must be well-formed according to:
        https://www.w3.org/TR/speech-synthesis/
    """
    # Detect Text Language Code
    langCode = getLangCode(argText)

    # Set output file name
    if output is None :
        output = md5sum_str(argText.encode('utf-8')+gender.encode('utf-8'))[:12]+".mp3"

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Set the text input to be synthesized
    synthesis_input = texttospeech.types.SynthesisInput(text=argText)

    # Build the voice request, select the language code ("en-US") and the ssml
    # voice gender ("neutral")
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=langCode,
        name=getSpeechName(langCode, gender),
        ssml_gender=getSSmlVoiceGender(gender))

    # Select the type of audio file you want returned
    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    # Perform the text-to-speech request on the text input with the selected
    # voice parameters and audio file type
    response = client.synthesize_speech(synthesis_input, voice, audio_config)

    # The response's audio_content is binary.
    with open(output, 'wb') as out:
        # Write the response to the output file.
        out.write(response.audio_content)
        print('Audio content written to file "{0}"'.format(output))
    # [END tts_quickstart]

def parseArguments() :
    parser = argparse.ArgumentParser(description='This program converts text to mp3 voice files.')
    parser.add_argument('-text', type=str, help='text string to speech')
    parser.add_argument('-output', type=str, help='output mp3 filename')
    parser.add_argument('-gender', type=str.upper, help='text string to speech gender', choices=['FEMALE', 'MALE', 'NEUTRAL'], default='FEMALE')
    parser.add_argument('-file', type=str, help='file contents to speech')
    args = parser.parse_args()

    if args.text is None and args.file is None :
        parser.print_help()

    return args.text, args.file, args.gender, args.output

if __name__ == '__main__':
    text, filepath, gender, output = parseArguments()
    if text is not None :
        convertSpeech(text, gender, output)
    elif filepath is not None :
        pass
