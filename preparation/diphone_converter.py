"""
diphone converter
=================
Module allows user to convert text in czech to set of diphones.
Uses information stored in file convert_data.json.

functions:
    * to_supported - Changes text to contain only supported characters.
    * graphems_to_phonems - Creates phonetic transcription of text.
    * phonems_to_diphones - Creates sequence of diphones from phonetic
      transcription.
    * convert_to_diphones - Makes sequence of diphones from text.
"""
import json
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
convert_data_path = os.path.join(package_directory, "convert_data.json")
with open(convert_data_path, "r", encoding="utf8") as json_data_file:
    data = json.loads(json_data_file.read())
    ALL_SUPPORTED = data["all_supported"]
    CONSONANTS = data["consonants"]
    VOICED_TO_VOICELESS = data["voiced_to_voiceless"]
    VOICELESS_TO_VOICED = data["voiceless_to_voiced"]
    REPLACING_SINGLE_CHAR = data["single_char_replacing"]
    REPLACING_TWO_CHAR = data["two_chars_replacing"]
    NUM_CONVERT_DICT = data["number_dict"]


def to_supported(text):
    """
    changes text to contain only supported characters

    :param str text: Text to be changed to supported characters
    :return: text containing only supported characters
    :rtype: str
    """
    text = text.lower()
    new_text = ""
    for char in text:
        if char in ALL_SUPPORTED:
            new_text += char
        elif char in NUM_CONVERT_DICT:
            new_text += NUM_CONVERT_DICT[char]
        elif char in [",", ".", "!", "?"]:
            new_text += "_"
    return new_text


def apply_special_rules(text):
    """
    applies on text special rules from convert_data.json

    :param str text: text to apply rules on
    :return: text with applied rules
    :rtype: str
    """
    idx = 0
    new_text = ""
    while idx < len(text):
        if text[idx:idx + 2] in REPLACING_TWO_CHAR:
            new_text += REPLACING_TWO_CHAR[text[idx:idx + 2]]
            idx += 2
        elif text[idx] in REPLACING_SINGLE_CHAR:
            new_text += REPLACING_SINGLE_CHAR[text[idx]]
            idx += 1
        else:
            new_text += text[idx]
            idx += 1
    return new_text


def apply_assimilation(text):
    """
    applies regressive assimilation on text. (spodoba znělosti)

    :param str text: text to apply assimilation on
    :return: text with applied assimilation
    :rtype: str
    """
    new_text = ""
    consonant_group = ""
    for char in text:
        if char in CONSONANTS:
            consonant_group += char
        elif char in ("_", " ", "X") and len(consonant_group) > 0:
            new_text += to_voiceless(consonant_group)
            consonant_group = ""
        elif len(consonant_group) > 0:
            if consonant_group[-1] in VOICED_TO_VOICELESS:
                new_text += to_voiced(consonant_group)
            elif consonant_group[-1] in VOICELESS_TO_VOICED:
                new_text += to_voiceless(consonant_group)
            consonant_group = ""
        if char not in CONSONANTS + [" "]:
            new_text += char

    if len(consonant_group) > 0:
        new_text += to_voiceless(consonant_group)

    return new_text


def to_voiced(consonant_group):
    """
    changes all voiceless consonants with voiced pair to voiced

    :param str consonant_group: group of consonants
    :return: group of voiced consonants
    :rtype: str
    """
    new_group = ""
    for consonant in consonant_group:
        if consonant in VOICELESS_TO_VOICED:
            new_group += VOICELESS_TO_VOICED[consonant]
        else:
            new_group += consonant
    return new_group


def to_voiceless(consonant_group):
    """
    changes all voiced consonants with voiceless pair to voiceless

    :param str consonant_group: group of consonants
    :return: group of voiceless consonants
    :rtype: str
    """
    new_group = ""
    for consonant in consonant_group:
        if consonant in VOICED_TO_VOICELESS:
            new_group += VOICED_TO_VOICELESS[consonant]
        else:
            new_group += consonant
    return new_group


def graphems_to_phonems(text):
    """
    creates phonetic transcription of text

    :param str text: text to be phonetically transcribed
    :return: phonetic transcription of text
    :rtype: str
    """
    text = to_supported(text)
    text = apply_special_rules(text)
    text = apply_assimilation(text)

    return text


def phonems_to_diphones(text):
    """
    creates sequence of diphones from phonetic transcription

    :param str text: phonetical transcription of text
    :return: sequence of diphones, list of 2 characters long strings
    :rtype: list[str]
    """
    text = "_" + text + "_"
    diphones = []
    for idx in range(len(text) - 1):
        diphones.append(text[idx:idx + 2])
    return diphones


def convert_to_diphones(text):
    """
    makes sequence of diphones from text

    :param str text: text to be converted to diphones
    :return: sequence of diphones, list of 2 characters long strings
    :rtype: list[str]
    """
    return phonems_to_diphones(graphems_to_phonems(text))
