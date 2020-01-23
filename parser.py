import pandas as pd
import spacy
from os import listdir, path
from lxml import etree

def extract_data(nlp, xml_file):
  headers = ['language', 'score', 'head']
  data = {}
  root = etree.parse(xml_file).getroot()
  errors = []
  total = 0
  correctionless = 0
  for header in headers:
    for h in root.iter(header):
      if h.text:
        data[header] = h.text
      if header == 'head' and h.attrib['sortkey']:
        data[header] = h.attrib['sortkey']
  answers = ['answer1', 'answer2']
  for answer in answers:
    for a in root.iter(answer):
      e, t, c = extract_errors(nlp, a)
      errors += e
      total += t
      correctionless += c
  return data, errors, total, correctionless

def replace_non_alphanumeric(text):
  characters = ['-', '\"', ',', '(', ')', ':', ';', '!', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', '/', '#', '£', '%', '$', '*', '+', '&', '|', '.', '=']
  for c in characters:
    text = text.replace(c, '')
  return text

def extract_errors(nlp, answer):
  headers = ['exam_score']
  errors_sentences = []
  exam_score = None
  total_number_of_errors = 0
  number_of_correctionless_errors = 0
  for header in headers:
    for h in answer.iter(header):
      exam_score = h.text
  for p in answer.iter('p'):
    if p.find('NS') != None:
        sentence_element = p
        nodes = sentence_element.xpath('child::node()')
        errors = list(sentence_element.iter('NS'))
        num_errors = len(errors)
        total_number_of_errors += num_errors
        count = 0
        while num_errors > 0:
          correct_sentence = ''
          line = ''
          num_errors -= 1
          error_position = None
          error_length = None
          error_type = None
          error_of_interest = False
          for node in nodes:
            if type(node) == etree._Element and len(list(node)) != 0:  # if the node is an error node (<NS></NS>) and it contains incorrect and corrected tags
              if node == errors[num_errors]: # if it is the error at the position examined
                error_type = node.attrib['type']
                error_of_interest = True
                error_position = len(nlp(" ".join(line.split()))) # recording error position
              else:
                error_of_interest = False
              for child in list(node): # loop through wrong and corrected utterances
                if child.tag == 'c' and child.text:
                  correct_sentence += replace_non_alphanumeric(child.text)
                  if not error_type:
                    line += replace_non_alphanumeric(child.text)
                elif child.tag == 'i' and child.text and error_type and error_of_interest:
                  line += replace_non_alphanumeric(child.text)
                  error_length = len(child.text.split())
            elif type(node) == etree._Element and len(list(node)) == 0 and node.text:
              text = replace_non_alphanumeric(node.text)
              line += text
              correct_sentence += text
              count += 1
            elif type(node) != etree._Element: # if the node only contains unicode text
              text = replace_non_alphanumeric(node)
              line += text
              correct_sentence += text
          if error_type and 'P' not in error_type and error_position is not None and error_length is not None: # filtering punctuation and nested errors
            line = " ".join(line.split())
            correct_sentence = " ".join(correct_sentence.split())
            error_bigram, e_bi_dep = get_pos_ngram(nlp, line, error_position, 2, error_type)
            correct_bigram, c_bi_dep  = get_pos_ngram(nlp, correct_sentence, error_position, 2)
            error_trigram, e_tri_dep = get_pos_ngram(nlp, line, error_position, 3, error_type)
            correct_trigram, c_tri_dep = get_pos_ngram(nlp, correct_sentence, error_position, 3)
            error_pos, e_dep = get_pos_ngram(nlp, line, error_position, 1, error_type)
            correct_pos, c_dep = get_pos_ngram(nlp, correct_sentence, error_position, 1)
            error_pos_2, e_dep_2 = get_pos_ngram(nlp, line, error_position + 1, 1)
            correct_pos_2, c_dep_2 = get_pos_ngram(nlp, correct_sentence, error_position + 1, 1)
            error_pos_3, e_dep_3 = get_pos_ngram(nlp, line, error_position + 2, 1)
            correct_pos_3, c_dep_3 = get_pos_ngram(nlp, correct_sentence, error_position + 2, 1)
            first_first_pos, first_second_pos, first_third_pos, \
              second_first_pos, second_second_pos, second_third_pos, \
                third_first_pos, third_second_pos, third_third_pos = compare_tags(error_pos, error_pos_2, error_pos_3,
                                                                                  correct_pos, correct_pos_2, correct_pos_3)
            first_first_dep, first_second_dep, first_third_dep, \
              second_first_dep, second_second_dep, second_third_dep, \
                third_first_dep, third_second_dep, third_third_dep = compare_tags(e_dep, e_dep_2, e_dep_3,
                                                                                  c_dep, c_dep_2, c_dep_3)
            errors_sentences.append({'line': line, 'correct_sentence': correct_sentence, 'exam_score': exam_score,
              'error_type': error_type, 'error_position': error_position,
              'error_trigram': error_trigram, 'correct_trigram': correct_trigram,
              'error_bigram': error_bigram, 'correct_bigram': correct_bigram,
              'error_pos': error_pos, 'correct_pos': correct_pos,
              'error_pos_2': error_pos_2, 'correct_pos_2': correct_pos_2,
              'error_pos_3': error_pos_3, 'correct_pos_3': correct_pos_3,
              'e_tri_dep': e_tri_dep, 'c_tri_dep': c_tri_dep,
              'e_bi_dep': e_bi_dep, 'c_bi_dep': c_bi_dep,
              'e_dep': e_dep, 'c_dep': c_dep,
              'e_dep_2': e_dep_2, 'c_dep_2': c_dep_2,
              'e_dep_3': e_dep_3, 'c_dep_3': c_dep_3,
              'first_first_pos': first_first_pos, 'first_second_pos': first_second_pos, 'first_third_pos': first_third_pos,
              'second_first_pos': second_first_pos, 'second_second_pos': second_second_pos, 'second_third_pos': second_third_pos,
              'third_first_pos': third_first_pos, 'third_second_pos': third_second_pos, 'third_third_pos': third_third_pos,
              'first_first_dep': first_first_dep, 'first_second_dep': first_second_dep, 'first_third_dep': first_third_dep,
              'second_first_dep': second_first_dep, 'second_second_dep': second_second_dep, 'second_third_dep': second_third_dep,
              'third_first_dep': third_first_dep, 'third_second_dep': third_second_dep, 'third_third_dep': third_third_dep,
              'error_length': error_length})
        number_of_correctionless_errors += count/len(errors)
  return errors_sentences, total_number_of_errors, number_of_correctionless_errors

def tag_sentence(nlp, sentence):
  if sentence.isupper():
    sentence = sentence.lower()
  tags = []
  deps = []
  for sent in nlp.pipe([sentence], disable=["ner", "textcat"]):
    for token in sent:
      if token.tag_ != '_SP':
        tags.append(token.tag_)
        deps.append(token.dep_)
  return tags, deps

def get_pos_ngram(nlp, sentence, index, n, error_type=None):
  tags, deps = tag_sentence(nlp, sentence)
  pos_tags = ''
  dep_tags = ''
  if error_type and ('M' in error_type or 'AS' in error_type): # adding a blank tag for 'missing' error types
    n -= 1
    pos_tags = '_ '
    dep_tags = '_ '
  tags.extend(['*'] * (n + 2))
  deps.extend(['*'] * (n + 2))
  for i in range(index, index + n):
    pos_tags += tags[i] + " "
    dep_tags += deps[i] + " "
  return pos_tags, dep_tags

def compare_tags(first_incorrect, second_incorrect, third_incorrect,
                  first_correct, second_correct, third_correct):
  return first_incorrect == first_correct, first_incorrect == second_correct, first_incorrect == third_correct,\
          second_incorrect == first_correct, second_incorrect == second_correct, second_incorrect == third_correct,\
          third_incorrect == first_correct, third_incorrect == second_correct, third_incorrect == third_correct

def main():
  nlp = spacy.load('en_core_web_lg')
  structure = {'head': [], 'language': [], 'score': [], 'exam_score': [], 'line': [], 'error_position': [], 'error_type': [],
    'correct_sentence': [], 'error_trigram': [], 'correct_trigram': [], 'error_bigram': [], 'correct_bigram': [], 'error_pos': [], 'correct_pos': [],
    'correct_pos_2': [], 'error_pos_2': [], 'correct_pos_3': [], 'error_pos_3': [], 'error_length': [],  'e_tri_dep': [], 'c_tri_dep': [],
    'e_bi_dep': [], 'c_bi_dep': [], 'e_dep': [], 'c_dep': [], 'e_dep_2': [], 'c_dep_2': [], 'e_dep_3': [], 'c_dep_3': [],
    'first_first_pos': [], 'first_second_pos': [], 'first_third_pos': [],
    'second_first_pos': [], 'second_second_pos': [], 'second_third_pos': [],
    'third_first_pos': [], 'third_second_pos': [], 'third_third_pos': [],
    'first_first_dep': [], 'first_second_dep': [], 'first_third_dep': [],
    'second_first_dep': [], 'second_second_dep': [], 'second_third_dep': [],
    'third_first_dep': [], 'third_second_dep': [], 'third_third_dep': []}
  languages = {}
  dataset = './fce-released-dataset/dataset/'
  directories = listdir(dataset)
  t = 0
  c = 0
  for directory in directories:
    if path.isdir(dataset + directory):
      files = listdir(dataset + directory)
      for file in files:
        data, errors, total, correctionless = extract_data(nlp, dataset + directory + '/' + file)
        t += total
        c += correctionless
        if data['language'] not in languages.keys():
          languages[data['language']] = 1
        else:
          languages[data['language']] += 1
        for error in errors:
          structure['head'].append(data['head'])
          structure['language'].append(data['language'])
          structure['score'].append(data['score'])
          structure['exam_score'].append(error['exam_score'])
          structure['line'].append(error['line'])
          structure['correct_sentence'].append(error['correct_sentence'])
          structure['error_type'].append(error['error_type'])
          structure['error_position'].append(error['error_position'])
          structure['error_trigram'].append(error['error_trigram'])
          structure['correct_trigram'].append(error['correct_trigram'])
          structure['error_bigram'].append(error['error_bigram'])
          structure['correct_bigram'].append(error['correct_bigram'])
          structure['error_pos'].append(error['error_pos'])
          structure['correct_pos'].append(error['correct_pos'])
          structure['error_pos_2'].append(error['error_pos_2'])
          structure['correct_pos_2'].append(error['correct_pos_2'])
          structure['error_pos_3'].append(error['error_pos_3'])
          structure['correct_pos_3'].append(error['correct_pos_3'])
          structure['e_tri_dep'].append(error['e_tri_dep'])
          structure['c_tri_dep'].append(error['c_tri_dep'])
          structure['e_bi_dep'].append(error['e_bi_dep'])
          structure['c_bi_dep'].append(error['c_bi_dep'])
          structure['e_dep'].append(error['e_dep'])
          structure['c_dep'].append(error['c_dep'])
          structure['e_dep_2'].append(error['e_dep_2'])
          structure['c_dep_2'].append(error['c_dep_2'])
          structure['e_dep_3'].append(error['e_dep_3'])
          structure['c_dep_3'].append(error['c_dep_3'])
          

          structure['first_first_pos'].append(error['first_first_pos'])
          structure['first_second_pos'].append(error['first_second_pos'])
          structure['first_third_pos'].append(error['first_third_pos'])
          structure['second_first_pos'].append(error['second_first_pos'])
          structure['second_second_pos'].append(error['second_second_pos'])
          structure['second_third_pos'].append(error['second_third_pos'])
          structure['third_first_pos'].append(error['third_first_pos'])
          structure['third_second_pos'].append(error['third_second_pos'])
          structure['third_third_pos'].append(error['third_third_pos'])
          structure['first_first_dep'].append(error['first_first_dep'])

          structure['first_second_dep'].append(error['first_second_dep'])
          structure['first_third_dep'].append(error['first_third_dep'])
          structure['second_first_dep'].append(error['second_first_dep'])
          structure['second_second_dep'].append(error['second_second_dep'])
          structure['second_third_dep'].append(error['second_third_dep'])
          structure['third_first_dep'].append(error['third_first_dep'])
          structure['third_second_dep'].append(error['third_second_dep'])
          structure['third_third_dep'].append(error['third_third_dep'])

          structure['error_length'].append(error['error_length'])
  df = pd.DataFrame(data=structure)
  df.to_csv(r'./dataframe.csv')
  print(languages, t, c)

def test():
  nlp = spacy.load('en_core_web_lg')
  test1 = '/Users/leticiawanderley/Documents/CMPUT 664/project/fce-released-dataset/dataset/0100_2000_12/doc209.xml'
  test = './fce-released-dataset/dataset/0100_2000_6/doc730.xml'
  #test = './fce-released-dataset/dataset/0102_2000_6/doc2402.xml'
  data, errors, total, correctionless = extract_data(nlp, test1)
  print(total, correctionless)
  for e in errors:
    if e['error_type'] == 'ID':
      print(e)

if __name__ == "__main__":
  main()
  #test()