from sqlalchemy.sql.functions import current_date

import utils.file_manager as fman
import configurations as conf
import datetime
import constants as c
import utils.misc as misc
import utils.semantic_graph_builder as sgb
import utils.graph_utils as gu
from utils.misc import log_print, to_nltk_tree
import disambiguation.babelfy_man as bfm
import utils.dependency_parser as dep_parser


def find_relation_from_filelist(filepath_list, relation_extractors):
    for xml_path in filepath_list:

        try:
            cur_xml_man = fman.LxmlParser(xml_path)
        except Exception as e:
            log_print("Problem with " + xml_path)
            continue

        cur_sentences = list(cur_xml_man.get_sentences(num_of_sentences=conf.NUM_FIRST_WIKI_SENTENCES))
        len_sentences = sum(len(sent) for sent in cur_sentences) + len(cur_sentences)
        cur_annotations = list(
            cur_xml_man.get_annotations_by_range(0, len_sentences))

        for inst in analyze_xml(cur_sentences, cur_annotations, dep_parser.get_spacy_parser(), relation_extractors):
            log_print(xml_path)
            yield inst
    pass


def find_relation_from_datadir(data_dir, relation_extractors):
    # Iterate over the whole dataset.
    # subdir is the integer representing the current subdirectory that is under analysis;
    # xml_path_list is the list of filepaths of the files in that subdirectoy
    for subdir, xml_path_list in fman.get_docs_list_by_subdir(data_dir):

        # time measurement
        start_subdir = datetime.datetime.now()

        start = datetime.datetime.now()
        log_print(start, "Loading from subdir %03d" % subdir)
        cur_xml_list = []

        for xml_path in xml_path_list:
            try:
                # XML manager for parse the Wikipedia page in XML format
                cur_xml_man = fman.LxmlParser(xml_path)
            except Exception as e:
                log_print("Problem with " + xml_path)
                continue

            # read the first default number of sentences.
            cur_sentences = list(cur_xml_man.get_sentences(num_of_sentences=conf.NUM_FIRST_WIKI_SENTENCES))

            # retrieve only the usable annotations, relative to only the retrieved sentences
            len_sentences = sum(len(sent) for sent in cur_sentences) + len(cur_sentences)
            cur_annotations = list(cur_xml_man.get_annotations_by_range(0, len_sentences))

            # for every RelationExtraction object (i.e.: relation instance) retrieved, yield it.
            for inst in analyze_xml(cur_sentences, cur_annotations, dep_parser.get_spacy_parser(), relation_extractors):
                log_print(xml_path)
                yield inst

        log_print(datetime.datetime.now(), "Total Time elapsed: ", datetime.datetime.now() - start_subdir)
        log_print("-" * 50)


def analyze_xml(sentences, annotations, parser, relation_extractors):
    """
	This is the core method that implements the described procedure.
	From a disambiguation mapping (computed from annotations, in the module disambiguation.babelfy_man)
	and a dependency parsed sentence (computed in the utils.semantic_graph_builder)
	compute the syntactic-semantic graph.
	From it, compute shortest paths, filter by some criteria, check for similarity thanks to the RelationExtractor object
		(defined in the module utils.seeds)
	Yield the paths which are compliant with the RelationExtractor.
	Iterate over all the RelationExtractors in input.
	:param sentences: a list of splitted sentences
	:param annotations: a list of annotations
	:param parser: the spaCy parser
	:param relation_extractors: a list of RelationExtraction object; each of them represents a relation we are looking for.
	:return: a RelationExtraction (i.e.: a relation instance)
	"""

    # compute a list of disambiguated sentences. Each disambiguated sentence is a list of Disambiguation object.
    # the class Disambiguation is defined in disambiguation.Disambiguation
    disambiguations = bfm.disambiguate_sentences(sentences, annotations)
    if len(sentences) == 0 or len(disambiguations) == 0: return []

    # initialize the "concept of the page" to None
    # if it is found in the first sentence, it will be replaced to every subject in following sentences.
    main_concept_of_the_page = None
    main_concept_disambiguations = None

    for sent_idx, (sent, sent_disambiguation) in enumerate(zip(sentences, disambiguations)):
        tok_to_sub = None

        try:
            # try to clean the sentence from useless substrings
            sent, sent_disambiguation = misc.clean_sentence(sent, sent_disambiguation)
        except:
            continue

        # parse the sentence with spaCy, producing a dependency parsed tree.
        sents = list(parser(" ".join(sent)).sents)
        if len(sents) != 1:
            continue
        dependency_parsed_sentence = sents[0]

        try:
            # try to build the syntactic-semantic graph
            semantic_graph, token2concept = sgb.build_one_semantic_graph(dependency_parsed_sentence,
                                                                         sent_disambiguation)
        except Exception as e:
            log_print("Exception on building semantic graph for: " + dependency_parsed_sentence.text)
            continue

        # find the subjects in the dependency tree
        nsubj_idx = [i for i, t in enumerate(semantic_graph) if t.dep_ in c.SUBJ_DEPTAGS]

        # if there is no subject, skip this sentence
        if len(nsubj_idx) == 0: continue

        # otherwise, pick the first subject
        nsubj_tok = semantic_graph[nsubj_idx[0]]

        # if first sentence, it is the main concept:
        if sent_idx == 0:
            main_concept_of_the_page, main_concept_disambiguations = nsubj_tok, token2concept[nsubj_tok.i]
        # otherwise, keep track of the token that will be replaced by the main concept,
        # but only if it satisfies some constrain, such as:
        # 	- it is a subject
        # 	- the main concept is not found
        # 	- the POS tag is a PROPN, PRON or a NOUN
        elif sent_idx != 0 and \
                (nsubj_tok.pos_ == c.PROPN_POSTAG or nsubj_tok.pos_ == c.PRON_POSTAG or nsubj_tok.pos_ == c.NOUN_POSTAG) \
                and nsubj_tok.dep_ in c.SUBJ_DEPTAGS \
                and main_concept_of_the_page != None:
            tok_to_sub = nsubj_tok

        # find all the shortest paths from the subject of the sentence
        paths_from_nsubj = gu.find_shortest_paths_from_source(semantic_graph, nsubj_tok)

        # filter paths by some criteria (explained in the report)
        filtered_paths = gu.filter_paths({nsubj_tok: paths_from_nsubj})
        triples = [gu.extract_triple(p) for p in filtered_paths]

        # iterate for every candidate triple and for every RelationExtractor, check if
        # the candidate triple is compliant with that relation.
        for t in triples:
            for relation_extractor in relation_extractors:
                if relation_extractor.is_compliant(" ".join(map(lambda x: x.text, t[1]))):
                    # if some conditions hold, substitute the subject with the main concept of the page (if any)
                    if tok_to_sub != None and t[
                        0] == tok_to_sub and main_concept_of_the_page != None and main_concept_disambiguations != None:
                        source_sentence = " ".join(sent).replace(t[0].text, main_concept_of_the_page.text, 1)
                        left_concept = main_concept_disambiguations
                    # otherwise, return the triple as is
                    else:
                        source_sentence = " ".join(sent)
                        left_concept = token2concept[t[0].i]

                    right_concept = token2concept[t[2].i]
                    relation_name = relation_extractor.name

                    # fix concept (i.e.: check if it is a CUSTOM_TYPE concept)
                    # if it is the case, return the most compliant subconcept
                    fixed_left_concept = misc.fix_concept(left_concept)
                    fixed_right_concept = misc.fix_concept(right_concept)

                    yield RelationExtraction(relation_name, fixed_left_concept, fixed_right_concept, source_sentence)


class RelationExtraction(object):
    """
	This class represent a relation instance.
	"""

    def __init__(self, relation_name, left_concept, right_concept, source):
        self.relation_name = relation_name
        self.left_concept = left_concept
        self.right_concept = right_concept
        self.source = source

    def __str__(self):
        return \
            "relation_name:" + self.relation_name + "\n" + \
            "left_concept.mention:" + self.left_concept.mention + "\n" + \
            "right_concept.mention:" + self.right_concept.mention + "\n" + \
            "source:" + self.source
