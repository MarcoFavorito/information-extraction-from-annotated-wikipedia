import re

class QuestionPattern(object):
	"""
	This class represents a question pattern
	with the question string,
	the relation name
	and the placeholders for right and left concepts.
	"""
	def __init__(self, relation_name, question, left_placeholder="X", right_placeholder="Y"):
		self.relation_name = relation_name
		self.question = question
		self.left_placeholder = left_placeholder
		self.right_placeholder = right_placeholder

	def __str__(self):
		return self.relation_name + ":" + self.question

	def is_binary_question(self):
		return bool(re.search("\W%s\W" % self.right_placeholder, self.question))

def read_question_pattern_file(filepath):
	"""
	Parse the question pattern file. It is simply a tsv where each line represent a pattern.
	The line are formatted as follows:
	question_string\trelation name
	:param filepath: the filepath to the question-pattern file.
	:return: a dictionary
		from the relation name (string)
		to a list of question patterns
	"""
	relation2patterns = {}
	with open(filepath) as fin:
		for line in fin:
			question, relation_name = line.strip(' \n').split("\t")
			if relation_name not in relation2patterns:
				relation2patterns[relation_name]=[]
			new_question_pattern = QuestionPattern(relation_name, question)
			relation2patterns[relation_name].append(new_question_pattern)
	return relation2patterns



