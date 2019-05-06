import pandas as pd
from os import listdir, path
from lxml import etree
from textblob import TextBlob
from textblob.en.np_extractors import ChunkParser

def extract_data(xml_file):
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
      errors += extract_errors(a)
  return data, errors

def replace_non_alphanumeric(text):
  characters = ['-', '\"', ',', '(', ')', ':', ';', '!', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '?', '/', '#', '£', '%', '$', '*', '+', '&', '|', '.']
  for c in characters:
    text = text.replace(c, '')
  return text

def extract_errors(answer):
  headers = ['exam_score']
  errors_sentences = []
  exam_score = None

  for header in headers:
    for h in answer.iter(header):
      exam_score = h.text
  for p in answer.iter('p'):
    if p.find('NS') != None:
        sentence_element = p
        nodes = sentence_element.xpath("child::node()")
        errors = list(sentence_element.iter('NS'))
        num_errors = len(errors)
        while num_errors > 0:
          correct_sentence = ''
          line = ''
          num_errors -= 1
          error_position = None
          error_type = None
          for node in nodes:
            if type(node) == etree._Element: # if the node is an error node (<NS></NS>)
              if node == errors[num_errors]: # if it is the error at the position examined
                error_type = node.attrib['type']
                error_position = len(line.split()) # recording error position
              for child in list(node): # loop through wrong and corrected utterances
                if child.tag == 'c' and child.text:
                  correct_sentence += replace_non_alphanumeric(child.text)
                  if not error_type:
                    line += replace_non_alphanumeric(child.text)
                elif child.tag == 'i' and child.text and error_type:
                  line += replace_non_alphanumeric(child.text)
            else: # if the node only contains unicode text
              text = replace_non_alphanumeric(node)
              line += text
              correct_sentence += text
                                 
          if error_type and 'P' not in error_type and error_position is not None: # filtering punctuation and nested errors
            error_bigram = get_pos_ngram(line, error_position, 2, error_type)
            correct_bigram = get_pos_ngram(correct_sentence, error_position, 2)
            error_trigram = get_pos_ngram(line, error_position, 3, error_type)
            correct_trigram = get_pos_ngram(correct_sentence, error_position, 3)
            error_pos = get_pos_ngram(line, error_position, 1, error_type)
            correct_pos = get_pos_ngram(correct_sentence, error_position, 1)
            errors_sentences.append({'line': line, 'correct_sentence': correct_sentence, 'exam_score': exam_score,
              'error_type': error_type, 'error_position': error_position,
              'error_trigram': error_trigram, 'correct_trigram': correct_trigram,
              'error_bigram': error_bigram, 'correct_bigram': correct_bigram,
              'error_pos': error_pos, 'correct_pos': correct_pos})
  return errors_sentences

def get_pos_ngram(sentence, index, n, error_type=None):
  blob = TextBlob(sentence)
  blob.parse()
  tags = blob.tags
  pos_tags = ''
  if error_type and 'M' in error_type: # adding a blank tag for 'missing' error types
    n -= 1
    pos_tags = '_ '
  tags.extend([('', '*')] * n)
  for i in range(index, index + n):
    pos_tags += tags[i][1] + " "
  return pos_tags

def main():
  structure = {'head': [], 'language': [], 'score': [], 'exam_score': [], 'line': [], 'error_position': [], 'error_type': [],
    'correct_sentence': [], 'error_trigram': [], 'correct_trigram': [], 'error_bigram': [], 'correct_bigram': [], 'error_pos': [], 'correct_pos': []}
  languages = {}
  dataset = './fce-released-dataset/dataset/'
  directories = listdir(dataset)
  for directory in directories:
    if path.isdir(dataset + directory):
      files = listdir(dataset + directory)
      for file in files:
        data, errors = extract_data(dataset + directory + '/' + file)
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
  df = pd.DataFrame(data=structure)
  df.to_csv(r'./dataframe.csv')
  print(languages)

def test():
  test = './fce-released-dataset/dataset/0100_2001_6/doc2968.xml'
  data, errors = extract_data(test)
  print(data, errors)

if __name__ == "__main__":
  main()
  #test()