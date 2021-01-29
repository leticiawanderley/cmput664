import numpy as np
import pandas as pd


df = pd.read_csv('main_parser2.csv')
df = df[['student_id', 'language', 'raw_sentence']]
df['length'] = df.apply(lambda row: len(row['raw_sentence'].split()), axis=1)
df = df.drop_duplicates(subset=['raw_sentence'])
df_words = df.groupby(['student_id', 'language']).sum().reset_index()

print('Mean', df_words['length'].mean(),
      'SD', df_words['length'].std())

df_zhs_words = df_words[df_words['language'] == 'Chinese']
print('Mean', df_zhs_words['length'].mean(),
      'SD', df_zhs_words['length'].std())

print(df_words.groupby(['language']).count())
print(df.groupby(['language']).sum().reset_index())