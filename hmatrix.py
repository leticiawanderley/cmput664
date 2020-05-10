import json
import pandas as pd

languages = ["Spanish", "Chinese", "German", "French", "Russian"]
ruleset = {
  "A": "Agreement", "F": "Form", "M": "Missing", "R": "Replace",
  "U": "Unnecessary", "D": "Derived", "C": "Countability", "S": "Spelling",
  "T": "Tense", "W": "Word Order", "X": "Negative", "L": "Label",
  "I": "Incorrect"
}

marianas_data = pd.read_csv('aux_toefl_table.csv')

data = pd.read_csv('main_parser2.csv')

data['rule'] = data['error_type'] + " "

data = data[data.language.isin(languages)]

df = data.groupby(['student_id', 'language', 'rule']).size().\
  unstack(fill_value=0).stack().reset_index(name='error_count_per_student')

df2 = df.groupby(['language', 'rule']).\
        apply(lambda x: (x['error_count_per_student'] > 0).sum()).\
        reset_index(name='file_count')

print(df2)

df['category'] = df['rule'].str[:1]
df['category'].replace(ruleset, inplace=True)

df = df.groupby(['language', 'rule', 'category']).\
  agg(error_count=('error_count_per_student', 'sum')).\
    reset_index()

df['tot_essays'] = len(data.student_id.unique())

print(df)

df = df.merge(df2, left_on=['language', 'rule'], right_on=['language', 'rule'])

print(df)

df.to_json(r'hmatrix_output.json', orient='records')
