## Parser 2 output description

Each line in this dataset represents an annotated learner error.
One paragraph line in the essay XML file can contain more than one annotated error.

| Column        | Type   | Description  |
| ------------- |:------:|-------------|
| student_id    | String | Test taker identification |
| language      | String | Learner's L1    |
| overall_score | Float | Combined mark for both tasks     |
| exam_score    | String | Essay mark |
| raw_sentence  | String | Paragraph line extracted from the XML file      |
| error_type    | String | Tag associated with the error (See [Nicholls 2003](http://ucrel.lancs.ac.uk/publications/CL2003/papers/nicholls.pdf))    |
| error_length    | Integer | How many words are tagged in the error |
| correction_length      | Integer | How many words are tagged in the correction      |
| correct_sentence    | String | Sentence with all the errors replaced by their corrections |
| correct_error_index | Integer | Index of the correction in the sentence     |
| incorrect_sentence | String | Sentence with all the errors replaced by their corrections, **but the error represented by the row**      |
| incorrect_error_index      | Integer | Index of the error in the sentence        |
| correct_trigram      | List of strings | Sequence of tree words that begins at the correction index       |
| correct_trigram_tags | List of strings |Part-of-speech tags corresponding to the correction sequence       |
| correct_trigram_deps    | List of strings |Dependency tags corresponding to the correction sequence  |
| correct_trigram_poss      | List of strings |Universal part-of-speech tags corresponding to the correction sequence      |
| correct_trigram_tag_0 | String | Part-of-speech tag corresponding to the first word in the correction      |
| correct_trigram_tag_1 | String | Part-of-speech tag corresponding to the second word in the correction       |
| correct_trigram_tag_2    | String | Part-of-speech tag corresponding to the third word in the correction  |
| correct_trigram_dep_0      | String | Dependency tag corresponding to the first word in the correction       |
| correct_trigram_dep_1 | String | Dependency tag corresponding to the second word in the correction      |
| correct_trigram_dep_2    | String |Dependency tag corresponding to the third word in the correction |
| incorrect_trigram    | List of strings | Sequence of tree words that begins at the error index |
| incorrect_trigram_tags      | List of strings | Part-of-speech tags corresponding to the error sequence      |
| incorrect_trigram_deps | List of strings | Dependency tags corresponding to the error sequence       |
| incorrect_trigram_poss | List of strings | Universal part-of-speech tags corresponding to the error sequence     |
| incorrect_trigram_tag_0    | String | Part-of-speech tag corresponding to the first word in the error |
| incorrect_trigram_tag_1      | String | Part-of-speech tag corresponding to the second word in the error      |
| incorrect_trigram_tag_2 | String | Part-of-speech tag corresponding to the third word in the error      |
| incorrect_trigram_dep_0 | String | Dependency tag corresponding to the first word in the error     |
| incorrect_trigram_dep_1    | String | Dependency tag corresponding to the second word in the error |
| incorrect_trigram_dep_2      | String | Dependency tag corresponding to the third word in the error      |
| 0_0_tag | Boolean | Whether the first POS tag in the correction and the first POS tag in the error are the same      |
| 0_1_tag    | Boolean | Whether the first POS tag in the correction and the second POS tag in the error are the same |
| 0_2_tag      | Boolean | Whether the first POS tag in the correction and the third POS tag in the error are the same      |
| 1_0_tag | Boolean | Whether the second POS tag in the correction and the first POS tag in the error are the same      |
| 1_1_tag    | Boolean | Whether the second POS tag in the correction and the second POS tag in the error are the same |
| 1_2_tag      | Boolean | Whether the second POS tag in the correction and the third POS tag in the error are the same      |
| 2_0_tag | Boolean | Whether the third POS tag in the correction and the first POS tag in the error are the same      |
| 2_1_tag    | Boolean | Whether the third POS tag in the correction and the second POS tag in the error are the same |
| 2_2_tag      | Boolean | Whether the third POS tag in the correction and the third POS tag in the error are the same      |
| 0_0_dep | Boolean | Whether the first dependency tag in the correction and the first dependency tag in the error are the same     |
| 0_1_dep    | Boolean | Whether the first dependency tag in the correction and the second dependency tag in the error are the same  |
| 0_2_dep      | Boolean | Whether the first dependency tag in the correction and the third dependency tag in the error are the same       |
| 1_0_dep | Boolean | Whether the second dependency tag in the correction and the first dependency tag in the error are the same       |
| 1_1_dep    | Boolean | Whether the second dependency tag in the correction and the second dependency tag in the error are the same  |
| 1_2_dep      | Boolean | Whether the second dependency tag in the correction and the third dependency tag in the error are the same       |
| 2_0_dep | Boolean | Whether the third dependency tag in the correction and the first dependency tag in the error are the same       |
| 2_1_dep      | Boolean | Whether the third dependency tag in the correction and the second dependency tag in the error are the same       |
| 2_2_dep | Boolean | Whether the third dependency tag in the correction and the third dependency tag in the error are the same       |