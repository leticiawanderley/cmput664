import pandas as pd
import spacy
from os import listdir, path
from lxml import etree

def extract_data(nlp, xml_file):
  headers = ['language', 'score', 'head']
  data = {}
  root = etree.parse(xml_file).getroot()
  errors = []
  for header in headers:
    for h in root.iter(header):
      if h.text:
        data[header] = h.text
      if header == 'head' and h.attrib['sortkey']:
        data[header] = h.attrib['sortkey']
  answers = ['answer1', 'answer2']
  for answer in answers:
    for a in root.iter(answer):
      errors += extract_errors(nlp, a)
  return data, errors

def replace_non_alphanumeric(text):
  characters = ['-', '\"', ',', '(', ')', ':', ';', '!', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', '/', '#', '£', '%', '$', '*', '+', '&', '|', '.', '=']
  for c in characters:
    text = text.replace(c, '')
  return text

def extract_errors(nlp, answer):
  headers = ['exam_score']
  errors_sentences = []
  exam_score = None

  for header in headers:
    for h in answer.iter(header):
      exam_score = h.text
  for p in answer.iter('p'):
    if p.find('NS') != None:
        sentence_element = p
        nodes = sentence_element.xpath('child::node()')
        errors = list(sentence_element.iter('NS'))
        num_errors = len(errors)
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
                error_position = len(tag_sentence(nlp, line)) # recording error position
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
            elif type(node) != etree._Element: # if the node only contains unicode text
              text = replace_non_alphanumeric(node)
              line += text
              correct_sentence += text
          if error_type and 'P' not in error_type and error_position is not None and error_length is not None: # filtering punctuation and nested errors
            error_bigram = get_pos_ngram(nlp, line, error_position, 2, error_type)
            correct_bigram = get_pos_ngram(nlp, correct_sentence, error_position, 2)
            error_trigram = get_pos_ngram(nlp, line, error_position, 3, error_type)
            correct_trigram = get_pos_ngram(nlp, correct_sentence, error_position, 3)
            error_pos = get_pos_ngram(nlp, line, error_position, 1, error_type)
            correct_pos = get_pos_ngram(nlp, correct_sentence, error_position, 1)
            error_pos_2 = get_pos_ngram(nlp, line, error_position + 1, 1)
            correct_pos_2 = get_pos_ngram(nlp, correct_sentence, error_position + 1, 1)
            error_pos_3 = get_pos_ngram(nlp, line, error_position + 2, 1)
            correct_pos_3 = get_pos_ngram(nlp, correct_sentence, error_position + 2, 1)
            errors_sentences.append({'line': line, 'correct_sentence': correct_sentence, 'exam_score': exam_score,
              'error_type': error_type, 'error_position': error_position,
              'error_trigram': error_trigram, 'correct_trigram': correct_trigram,
              'error_bigram': error_bigram, 'correct_bigram': correct_bigram,
              'error_pos': error_pos, 'correct_pos': correct_pos,
              'error_pos_2': error_pos_2, 'correct_pos_2': correct_pos_2,
              'error_pos_3': error_pos_3, 'correct_pos_3': correct_pos_3,
              'error_length': error_length})
  return errors_sentences

def tag_sentence(nlp, sentence):
  if sentence.isupper():
    sentence = sentence.lower()
  doc = nlp(sentence)
  tags = []
  for token in doc:
    if token.tag_ != '_SP':
      tags.append(token.tag_)
  return tags

def get_pos_ngram(nlp, sentence, index, n, error_type=None):
  tags = tag_sentence(nlp, sentence)
  pos_tags = ''
  if error_type and 'M' in error_type: # adding a blank tag for 'missing' error types
    n -= 1
    pos_tags = '_ '
  tags.extend(['*'] * (n + 2))
  for i in range(index, index + n):
    pos_tags += tags[i] + " "
  return pos_tags

def main():
  nlp = spacy.load('en_core_web_lg')
  structure = {'head': [], 'language': [], 'score': [], 'exam_score': [], 'line': [], 'error_position': [], 'error_type': [],
    'correct_sentence': [], 'error_trigram': [], 'correct_trigram': [], 'error_bigram': [], 'correct_bigram': [], 'error_pos': [], 'correct_pos': [],
    'correct_pos_2': [], 'error_pos_2': [], 'correct_pos_3': [], 'error_pos_3': [], 'error_length': []}
  languages = {}
  dataset = './fce-released-dataset/dataset/'
  directories = listdir(dataset)
  for directory in directories:
    if path.isdir(dataset + directory):
      files = listdir(dataset + directory)
      for file in files:
        data, errors = extract_data(nlp, dataset + directory + '/' + file)
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
          structure['error_length'].append(error['error_length'])
  df = pd.DataFrame(data=structure)
  df.to_csv(r'./dataframe.csv')
  print(languages)

def test():
  nlp = spacy.load('en_core_web_lg')
  test1 = '/Users/leticiawanderley/Documents/CMPUT 664/project/fce-released-dataset/dataset/0100_2000_12/doc209.xml'
  test = './fce-released-dataset/dataset/0100_2000_6/doc730.xml'
  #test = './fce-released-dataset/dataset/0102_2000_6/doc2402.xml'
  data, errors = extract_data(nlp, test1)
  for e in errors:
    if e['error_type'] == 'RV':
      print(e)

if __name__ == "__main__":
  main()
  #test()