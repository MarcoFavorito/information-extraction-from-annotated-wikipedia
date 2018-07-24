import sys

import utils.question_answer_generator as qa_gen
import utils.question_pattern_parser as qa_parser
import utils.relation_extractor as relext
import utils.seed_parser as seed_parser
from utils.misc import log_print


def print_usage():
    print("Usage:")
    print("main.py <IN_datadir> <IN_relation_seeds_file.tsv> <IN_question_patterns.tsv> <OUT_triples.tsv> <OUT_question_answer_pairs>")


def main():
    if len(sys.argv) != 6:
        print_usage()
        return -1
    # filepath for the directory which contains the corpus
    DATASET_DIR = sys.argv[1]

    relation_extractors = seed_parser.parse_seed_file(sys.argv[2])
    relation2patterns = qa_parser.read_question_pattern_file(sys.argv[3])
    triples_outfile = open(sys.argv[4], "w")
    questionAnswerGenerator = qa_gen.QuestionAnswerGenerator(sys.argv[5], relation2patterns)
    for r in relation_extractors:
        log_print(r)
    for i in relext.find_relation_from_datadir(DATASET_DIR, relation_extractors):
        print(i)
        print("\t".join([i.left_concept.mention, i.relation_name, i.right_concept.mention]), file=triples_outfile)

        questionAnswerGenerator.sample_instance(i)

    questionAnswerGenerator.flush_buffered_instances()
    return 0


if __name__ == '__main__':
    main()

# print(i)
# 	print(i, file=fout_triples)
# filelist = open("../search/MATERIAL-MOD.txt").read().splitlines()
# new_filelist = []
# for i, f in enumerate(filelist):
# 	if len(f.split(" "))==1:
# 		continue
# 	elif len(f.split(" "))==2:
# 		filelist[i] = filelist[i].split(" ")[1]
# 		new_filelist.append(filelist[i])
# 		print(i)
# 	else:
# 		raise Exception
# print("Start iterations")
# for i in relext.find_relation_from_filelist(filelist, relation_extractors):
# for i in relext.find_relation_from_filelist(["/home/marcofavorito/WorkFolder_Ubuntu/university_notes/NLP/hw3/babelfied-wikipediaXML//167/Monarda.xml.gz"], relation_extractors):
