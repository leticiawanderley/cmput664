import pandas as pd
import re
import spacy

from os import listdir, path

FULL_MATCH = 0
ERROR_TYPE = 1
INCORRECT = 3
INNER_ERROR_TYPE = 5
INNER_INCORRECT = 7
INNER_CORRECT = 9
INNER_INCORRECT_SUFFIX = 10
CORRECT = 12

PIPE = '|'
SPACED_PIPE = ' | '
PIPE_AT_POS_0 = '| '
EMPTY = ''
SPACE = ' '

exam_score_re = r'(?<=<exam_score>)(.*?)(?=<\/exam_score>)'
sentence_re = r'(?<=<p>)(.*?)(?=<\/p>)'  # retrieves sentence between <p></p>
full_inner_error_re = r"(<NS type=\"([A-Z]+)\">(<i>([\w\s\'\,\.\:\;\-\"\?\!\(\)\=\_\%\£\$\\&\/]*)(<NS type=\"([A-Z]+)\">(<i>(.*?)<\/i>)*(<c>(.*?)<\/c>)*<\/NS>([\w\s\'\,\.\:\;\-\"\?\!\(\)\=\_\%\£\$\\&\/]*))*<\/i>)*(<c>(.*?)<\/c>)*<\/NS>)"
error_type_re = r'(<NS type=\"([A-Z]+)\">)'
wrong_error_coding_re = r'(<NS type=\"[A-Z]+\">|<\/NS>|<\/*[a-z]+>)'


def combine_filename(dataset, directory, file):
    return dataset + directory + '/' + file


def clean_extra_whitespaces(sentence):
    words = sentence.split()
    new_sentence = EMPTY
    for w in words:
        new_sentence += w.strip() + SPACE
    return new_sentence


def replace_with_correction(sentence):
    errors_match = re.findall(full_inner_error_re, sentence, re.MULTILINE)
    for e in errors_match:
        sentence = sentence.replace(e[FULL_MATCH], e[CORRECT] if e[CORRECT]
                                    else EMPTY)
    sentence = re.sub(wrong_error_coding_re, SPACE, sentence)
    return clean_extra_whitespaces(sentence)


def mark_utterance(string):
    return "%s%s" % (PIPE, string)


def string_or_empty(string):
    return string if string and not string.isspace() else SPACE


def check_format(sentence):
    return '</i>' in sentence or '</c>' in sentence


def build_string(first, second, third):
    return (string_or_empty(first) + mark_utterance(string_or_empty(second)) +
            string_or_empty(third))


def tag_sentence(nlp, sentence):
    if sentence.isupper():
        sentence = sentence.lower()
    tokens = []
    tags = []
    deps = []
    poss = []
    index = 0
    for sent in nlp.pipe([sentence], disable=["ner", "textcat"]):
        for i, token in enumerate(sent):
            if token.text == PIPE:
                index = i
                break
    if index == 0:
        sentence = sentence.replace(PIPE_AT_POS_0, EMPTY)
    else:
        sentence = sentence.replace(SPACED_PIPE, SPACE)
    for sent in nlp.pipe([sentence], disable=["ner", "textcat"]):
        for i, token in enumerate(sent):
            tokens.append(token.text)
            tags.append(token.tag_)
            deps.append(token.dep_)
            poss.append(token.pos_)
    return tags, deps, poss, tokens, index


def fill_array(array, length):
    if len(array) < length:
        array = array + ['_'] * (length - len(array))
    return array


def set_tags_and_deps(nlp, sentence, data_dict, affix, length):
    tags, deps, poss, tokens, error_index = tag_sentence(nlp, sentence)
    data_dict[affix + '_error_index'].append(error_index)
    trigram = fill_array(tokens[error_index: error_index + length], length)
    trigram_tags = fill_array(tags[error_index: error_index + length], length)
    trigram_deps = fill_array(deps[error_index: error_index + length], length)
    trigram_poss = fill_array(poss[error_index: error_index + length], length)
    data_dict[affix + '_trigram'].append(trigram)
    data_dict[affix + '_trigram_tags'].append(" ".join(trigram_tags))
    data_dict[affix + '_trigram_deps'].append(" ".join(trigram_deps))
    data_dict[affix + '_trigram_poss'].append(" ".join(trigram_poss))
    for i in range(length):
        data_dict[affix + '_trigram_tag_' + str(i)].append(trigram_tags[i])
        data_dict[affix + '_trigram_dep_' + str(i)].append(trigram_deps[i])


def compare_utterances(data_dict, length):
    for type in ['tag', 'dep']:
        for i in range(length):
            for j in range(length):
                correct_value = 'correct_trigram_' + type + '_' + str(i)
                incorrect_value = 'incorrect_trigram_' + type + '_' + str(j)
                is_the_same = data_dict[correct_value][-1] == \
                    data_dict[incorrect_value][-1]
                data_dict[str(i) + '_' + str(j) + '_' + type]\
                    .append(is_the_same)


def sentence_formatting(sentence, full_match, replacement):
    sentence = replace_with_correction(
                  sentence.replace(full_match, replacement))\
                      .replace(PIPE, SPACED_PIPE)
    return clean_extra_whitespaces(sentence)


def add_common_data(data_dict, common_data, sentence, exam_score):
    data_dict['student_id'].append(common_data['student_id'])
    data_dict['language'].append(common_data['language'])
    data_dict['overall_score'].append(common_data['overall_score'])
    data_dict['exam_score'].append(exam_score)
    data_dict['raw_sentence'].append(sentence)


def add_sentences(data_dict, sentence, error, error_type_index,
                  full_match_index, incorrect, correct, nlp):
    if check_format(correct) or check_format(incorrect):
        return False
    length = 3
    correct_sentence = sentence_formatting(sentence, error[full_match_index],
                                           correct)
    incorrect_sentence = sentence_formatting(sentence, error[full_match_index],
                                             incorrect)
    set_tags_and_deps(nlp, correct_sentence, data_dict, 'correct', length)
    set_tags_and_deps(nlp, incorrect_sentence, data_dict, 'incorrect', length)
    compare_utterances(data_dict, length)
    data_dict['error_type'].append(error[error_type_index])
    data_dict['correct_sentence'].append(correct_sentence)
    data_dict['incorrect_sentence'].append(incorrect_sentence)
    data_dict['error_length'].append(len(incorrect.split()))
    data_dict['correction_length'].append(len(correct.split()))
    return True


def get_errors(filename, data_dict, nlp):
    regex_dict = {
        'student_id': r'(?<=sortkey=\")(.*?)(?=\">)',
        'language': r'(?<=<language>)(.*?)(?=<\/language>)',
        'overall_score': r'(?<=<score>)(.*?)(?=<\/score>)'
    }
    lines = open(filename, 'r').readlines()
    data_count = 0
    current_exam_score = 0
    common_data = {}
    number_of_errors = 0
    number_of_wrong = 0
    number_of_inner = 0
    for line in lines:
        if data_count < len(regex_dict):
            for data in regex_dict.keys():
                match = re.search(regex_dict[data], line, re.MULTILINE)
                if match:
                    common_data[data] = match.groups()[FULL_MATCH]
                    data_count += 1
        exam_score_match = re.search(exam_score_re, line, re.MULTILINE)
        if exam_score_match:
            current_exam_score = exam_score_match.groups()[FULL_MATCH]
        sentence_match = re.search(sentence_re, line, re.MULTILINE)
        if sentence_match:
            sentence = sentence_match.groups()[FULL_MATCH].replace('  ', SPACE)
            errors_match = re.findall(full_inner_error_re, sentence,
                                      re.MULTILINE)
            number_of_errors += len(errors_match)
            for e in errors_match:
                if e[INNER_ERROR_TYPE]:
                    number_of_inner += 1
                    incorrect = build_string(e[INCORRECT], e[INNER_INCORRECT],
                                             e[INNER_INCORRECT_SUFFIX])
                    correct = build_string(e[INCORRECT], e[INNER_CORRECT],
                                           e[INNER_INCORRECT_SUFFIX])
                    is_correct_format = add_sentences(data_dict, sentence, e,
                                                      INNER_ERROR_TYPE,
                                                      FULL_MATCH,
                                                      incorrect, correct, nlp)
                    if is_correct_format:
                        add_common_data(data_dict, common_data, sentence,
                                        current_exam_score)
                    else:
                        number_of_wrong += 1
                    incorrect = mark_utterance(correct.replace(PIPE, EMPTY))
                else:
                    incorrect = mark_utterance(string_or_empty(e[INCORRECT]))
                correct = mark_utterance(string_or_empty(e[CORRECT]))
                is_correct_format = add_sentences(data_dict, sentence, e,
                                                  ERROR_TYPE, FULL_MATCH,
                                                  incorrect, correct, nlp)
                if is_correct_format:
                    add_common_data(data_dict, common_data, sentence,
                                    current_exam_score)
                else:
                    number_of_wrong += 1
    return number_of_errors, number_of_wrong, number_of_inner


def main(test=False):
    total_errors = 0
    wrong = 0
    number_of_inner = 0
    nlp = spacy.load('en_core_web_lg')
    data_dict = {'student_id': [], 'language': [], 'overall_score': [],
                 'exam_score': [], 'raw_sentence': [], 'error_type': [],
                 'error_length': [], 'correction_length': [],
                 'correct_error_index': [], 'correct_sentence': [],
                 'correct_trigram': [], 'correct_trigram_tags': [],
                 'correct_trigram_deps': [], 'correct_trigram_poss': [],
                 'correct_trigram_tag_0': [], 'correct_trigram_tag_1': [],
                 'correct_trigram_tag_2': [], 'correct_trigram_dep_0': [],
                 'correct_trigram_dep_1': [], 'correct_trigram_dep_2': [],
                 'incorrect_error_index': [], 'incorrect_sentence': [],
                 'incorrect_trigram': [], 'incorrect_trigram_tags': [],
                 'incorrect_trigram_deps': [], 'incorrect_trigram_poss': [],
                 'incorrect_trigram_tag_0': [], 'incorrect_trigram_tag_1': [],
                 'incorrect_trigram_tag_2': [], 'incorrect_trigram_dep_0': [],
                 'incorrect_trigram_dep_1': [], 'incorrect_trigram_dep_2': [],
                 '0_0_tag': [], '0_1_tag': [], '0_2_tag': [],
                 '1_0_tag': [], '1_1_tag': [], '1_2_tag': [],
                 '2_0_tag': [], '2_1_tag': [], '2_2_tag': [],
                 '0_0_dep': [], '0_1_dep': [], '0_2_dep': [],
                 '1_0_dep': [], '1_1_dep': [], '1_2_dep': [],
                 '2_0_dep': [], '2_1_dep': [], '2_2_dep': []}

    if test:
        test = './fce-released-dataset/dataset/0102_2000_12/doc605.xml'
        a, b, c = get_errors(test, data_dict, nlp)
        total_errors += a
        wrong += b
        number_of_inner += c
        df = pd.DataFrame.from_dict(data_dict)
        df.to_csv('test_parser2.csv')
    else:
        dataset = './fce-released-dataset/dataset/'
        directories = listdir(dataset)
        for directory in directories:
            if path.isdir(dataset + directory):
                files = listdir(dataset + directory)
                for file in files:
                    filename = combine_filename(dataset, directory, file)
                    a, b, c = get_errors(filename, data_dict, nlp)
                    total_errors += a
                    wrong += b
                    number_of_inner += c
    df = pd.DataFrame.from_dict(data_dict)
    print('TOTAL ERRORS', total_errors)
    print('WRONG FORMAT', wrong)
    print('TOTAL INNER', number_of_inner)
    df.to_csv('main_parser2.csv')


main(test=True)
