import constants as c
import utils.misc as misc
from utils.misc import log_print

def build_semantic_graphs(dependency_graphs, disambiguations):
	"""
	Transform each pair of dependency parsed sentence-disambiguated sentence
	 into a syntactis-semantic graph.
	:param dependency_graphs: a spaCy dependency parsed sentence
	:param disambiguations: a list of Disambiguation objects
	:return:
	"""
	semantic_graphs = []

	for Gd, Sd in zip(dependency_graphs, disambiguations):
		cur_semantic_graph, _= build_one_semantic_graph(Gd, Sd)
		semantic_graphs.append(cur_semantic_graph)
	return dependency_graphs

def build_one_semantic_graph(Gd, Sd):
	"""

	:param Gd: Dependency parsed sentence (through spaCy). The method does side-effect on this variable.
	:param Sd: list of Disambiguation objects, one per word.
	:return: A tuple of two elements:
		0 - the same dependency parsed sentence, but with the nodes merged by following the disambiguations
		1 - a mapping from indexes of the tags in the new parsed sentence to concepts.
	"""

	cur_Gd = Gd
	tokenIndex2concept_mapping = {}
	temp = cur_Gd.root


	sentence = list(Gd)
	if len(sentence)!=len(Sd):
		merge_unfolded_nodes_from_tokenization(Gd, Sd)

	assert(len(list(Gd))==len(Sd))
	# misc.to_nltk_tree(Gd.root).pretty_print()

	lost_positions = 0
	tot_lost_positions = 0
	cur_index=0

	# merge nodes that belongs to the same super-concept
	# through the spaCy API (the "merge" function)
	for i, disambiguation in enumerate(Sd):
		if (lost_positions>0):
			lost_positions-=1
			continue

		word = disambiguation.word
		concept = disambiguation.concept

		cur_index = i-tot_lost_positions
		tokenIndex2concept_mapping[cur_index] = concept
		concept_mention = concept.mention
		concept_mention_length = len(concept_mention.split())

		cur_span = Gd[cur_index: cur_index + concept_mention_length]
		if not concept.isNullConcept():
			# If there is some subject or object in the element of the merge,
			# Preserve it in the final merged node
			if any(t.dep_ in c.SPECIAL_DEP_TAGS for t in cur_span):
				if any(t.dep_ in c.SUBJ_DEPTAGS for t in cur_span):
					cur_dep_ = c.NSUBJ_DEPTAG
				elif any(t.dep_ in c.OBJ_DEPTAGS for t in cur_span):
					cur_dep_ = c.POBJ_DEPTAG
				else:
					Exception("Misconfiguration: SPECIAL_DEP_TAGS is either in SUBJ_DEPTAGS or in OBJ_DEPTAGS")
				cur_span.merge(ent_id_=concept.babelNetID, dep_=cur_dep_)

			# Otherwise, let spaCy do the job of choose the appropriate dependency tag
			else:
				cur_span.merge(ent_id_=concept.babelNetID)
			lost_positions = concept_mention_length-1
			tot_lost_positions += lost_positions
		else:
			Gd[cur_index].ent_id_ = concept.babelNetID

	return Gd, tokenIndex2concept_mapping


def merge_unfolded_nodes_from_tokenization(Gd, Sd):
	"""
	Fix some misalignment between the syntactic graph (Gd) and
	the disambiguation mapping (Sd) (a list of Disambiguation)
	for example: words as "mother-in-law" are parsed differently between
	the spaCY parser and the format provided by the corpus.
	"""

	cur_index = 0
	lost_positions = 0
	tot_lost_positions = 0
	cur_word = ""
	for i in range(len(Gd)):
		cur_token = Gd[i-tot_lost_positions]
		cur_word += cur_token.text
		cur_mapped_word = Sd[cur_index].word
		if cur_word == cur_mapped_word:
			merged_node = Gd[cur_index: cur_index+1+lost_positions]
			if len(merged_node)!=1:
				merged_node.merge()
				tot_lost_positions+=lost_positions
				lost_positions = 0
			cur_index += 1
			cur_word  = ""
		else:
			lost_positions += 1

	assert cur_word == ""


