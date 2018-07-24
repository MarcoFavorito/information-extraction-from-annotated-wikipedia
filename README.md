# Information Extraction from Wikipedia pages   
Homework for the course of NLP (A.Y. 2016/2017) at Sapienza University. 

The task is to extract *relation instances* from *Wikipedia pages with Disambiguation of Concepts and Named Entities*.

A *relation instance*, is a triple of the form `(p1, r, p2)` where `p1` and `p2` are concepts and `r` is a relational phrase (e.g. `is located in`). 
An example of relation instance is `(Nunavut, is a part of, Canada)`.

The pages of Wikipedia are taken from the site of the paper
[Automatic Identification and Disambiguation of Concepts and Named Entities in the Multilingual Wikipedia](http://lcl.uniroma1.it/babelfied-wikipedia/).
In poor words, it is a collection of Wikipedia articles where every word is annotated with the corrisponding [BabelNet](https://babelnet.org/) synsets (concepts).


As an improvement, I'm going to implement a way to extract relations by directly connecting to Wikipedia web articles.

## Preliminaries
- install the spaCy package:
  ```
  pip install spacy
  ```
- download the `en_core_web_ms` or `en_core_web_md` model (strongly reccomended):
  ```
  python3 -m spacy download en_core_web_sm
  # or
  python3 -m spacy download en_core_web_md
  ```
        
  Further instructions: [SpaCy models](https://github.com/explosion/spacy-models).

- Download the annotated Wikipedia pages (19 GB):
  ```
  wget http://lcl.uniroma1.it/babelfied-wikipedia/files/babelfied-wikipediaXML.tar.gz
  ```
  and extract the archive:
  ```
  tar -xf babelfied-wikipediaXML.tar.gz
  ```

## How to use
The entry point for the software is "main.py".
It is callable from the command line as the following:

```
python main.py <IN_datadir> <IN_relation_seeds_file> <IN_question_patterns.tsv> <OUT_triples.tsv> <OUT_question_answer_pairs>
```

where:
  - `<IN_datadir>` is the path to the dataset directory provided from you;
  - `<IN_relation_seeds_file.tsv>` is the seed-file in the following format:
  ```
  relationName1:seed1,seed2,...,seedN[_similarityThreshold];
  relationName2:seed1,seed2,...,seedN[_similarityThreshold];
  ...
  ```
  You can see an example in src/seeds.
  - `<IN_question_patterns.tsv>` is the file of question pattern, in the format you have defined.
  - `<OUT_triples.tsv>` is the file where there will be written the extracted triples.
  - `<OUT_question_answer_pairs>` is the file where there will be written the Q/A pairs.

Example:

```
python $project_folder/main.py $project_folder/babelfied-wikipediaXML/ $project_folder/seeds $project_folder/patterns.tsv $project_folder/triples.tsv $project_folder/question_answer_pairs.txt
```

In [`./seeds`](./seeds) you can find an example of input for the program.

For further details, please refer to the [assignment](./Homework%203.pdf) and the [report](./report.pdf).