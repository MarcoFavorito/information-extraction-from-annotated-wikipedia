import configurations as conf
from nltk import Tree
import re
import constants as c

def log_print(*args, **kwargs):
	"""
	A simple wrapper of the built-in print function.
	It prints only if configuration.VERBOSE is true
	"""
	if "verbosity" in kwargs:
		verbosity = kwargs["verbosity"]
		del kwargs["verbosity"]
	else:
		verbosity = 1
	if (conf.VERBOSE and verbosity<=conf.VERBOSITY):
		print(*args, **kwargs)

def tok_format(tok):
	"""
	Make a summary string from a spaCy token, containing:
	 tok.orth_, which is the word[s];
	 tok.ent_id_, which is the entity id,
	 tok.dep_, which is the dependency tag
	"""
	return "_".join([tok.orth_, tok.ent_id_, tok.pos_, tok.dep_])

def to_nltk_tree(node):
	"""
	Returns a nltk.Tree object from a spaCy dependency graph.
	It should be calld with node set as the root node of the dependency graph.
	"""
	if node.n_lefts + node.n_rights > 0:
		return Tree(tok_format(node), [to_nltk_tree(child) for child in node.children])
	else:
		return Tree(tok_format(node), [])

def clean_sentence(sentence, disambiguations):
	"""
	Clean a sentence from some useless stuff (brackets, quotation marks etc.)
	:param sentence: a list of tokens (string), representing a sentence.
	:param disambiguations: a list of Disambiguation objects, wrt each word in the sentence.
	:return: the same pair of (sentence, disambiguations) without the tokens relative to bad substrings.
	"""
	assert len(sentence)==len(disambiguations)
	# We need to recover the entire string, then delete bad substring
	# and remove relative Disambiguation objects from the list "disambiguations".
	sentence_string = " ".join(sentence)

	ranges_to_delete = []
	# regex that solves out problem
	p = re.compile(" ?(\(|\[) .+? (\)|\])| ?``| ?''")
	for m in p.finditer(sentence_string):
		ranges_to_delete.append((m.start(), m.end()))

	if len(ranges_to_delete)!=0:
		# build the new sentence, without the matched substrings
		new_sentence = ""
		previous_index = 0
		for start_idx, end_idx in ranges_to_delete:
			new_sentence = new_sentence + sentence_string[previous_index:start_idx]
			previous_index = end_idx
		new_sentence = new_sentence + sentence_string[previous_index:]
		sentence = new_sentence.split()

		# delete relative disambiguations
		i = -1
		for i, token in enumerate(sentence):
			while token != disambiguations[i].word:
				del disambiguations[i]
		del disambiguations[i+1:]

	assert len(sentence)==len(disambiguations)
	return sentence, disambiguations


def fix_concept(concept):
	"""
	Transform each "custom_type" concept with an original one from the original annotations.
	It is a needed step, since at the end we need to write in the question_answer_pair.txt file
	a "real" disambiguation, not one found by the program.
	Obviously, this function applies only for concept with type "custom_type" (nor BABELFY, MCS or HL).
	The original annotations are stored in the subConceptList field. They are BabelNetConcept as well.
	The criterion is:
		1 - pick the concepts with the greatest anchorEnd field (with the rightmost end)
		2 - from the output of step 1, pick the longest concept (with the leftmost start)
	:param concept: a BabelNetConcept object
	:return: the concept of the concept.subConceptList which satisfy the above criterion.
	"""
	if concept.type == c.CUSTOM_TYPE:
		max_anchorEnd = max([co.anchorEnd for co in concept.subConceptList])
		rightmost_subconcepts = [co for co in concept.subConceptList if co.anchorEnd==max_anchorEnd]
		longest_rightmost_subconcept = max(rightmost_subconcepts, key=lambda x: -x.anchorStart)
		return longest_rightmost_subconcept
	else:
		return concept