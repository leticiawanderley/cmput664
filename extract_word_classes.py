import pandas as pd

def remove_word_class(value):
  if  len(value) > 1:
    return value[:-1]
  return value

def extract_word_classes(filename):
  df = pd.read_csv(filename)
  df['error_type'] = df['error_type'].apply(remove_word_class)
  df.to_csv('main_error_type_dataframe.csv')

extract_word_classes('dataframe.csv')