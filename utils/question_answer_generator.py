import random

class QuestionAnswerGenerator(object):
	"""
	This class is used as dynamic generator of question-answer pairs
	It is initialized with:
		- outfilepath: a path to the output file
		- relation2patterns: a dict from relation_name to list of QuestionPattern object (defined in utils.question_pattern_parser.py)
		- batch_size: the max size of the buffer. When the buffer is full, it starts the generation of Q/A pairs.
			the output is flushed into the file descriptor relative to outfilepath
	"""
	def __init__(self, outfilepath, relation2patterns, batch_size=10):
		self.outfile = open(outfilepath, "w")
		self.relation2patterns = relation2patterns
		# a dictionary from relation_name to the relative buffer (i.e.: list of RelationExtraction objects).
		self.sampled_instances = dict([(relation_name,[]) for relation_name in relation2patterns])
		# a dictionary from relation_name to the counter of relation instances of that relation
		self.number_of_instances = dict([(relation_name, 0) for relation_name in relation2patterns])
		self.batch_size = batch_size

	def __del__(self):
		self.flush_buffered_instances()
		self.outfile.close()

	def __exit__(self, exc_type, exc_val, exc_tb):
		self.flush_buffered_instances()
		self.outfile.close()

	def sample_instance(self, relation_instance):
		"""
		Insert a RelationExtraction object into the generator's data structures.
		If the buffer is full, generate Q/A pairs and write them to the output file.
		:param relation_instance:a RelationExtraction object
		"""
		relation_name = relation_instance.relation_name
		self.number_of_instances[relation_name]+=1
		batch_size= self.batch_size
		self.sampled_instances[relation_name].append(relation_instance)
		if len(self.sampled_instances[relation_name])>=batch_size:
			for qa_pair in self.generate_question_answer_pairs(relation_name):
				print(qa_pair, file=self.outfile)

	def flush_buffered_instances(self):
		"""
		Flush all the buffers.
		"""
		for relation_name in self.relation2patterns:
			for qa_pair in self.generate_question_answer_pairs(relation_name):
				print(qa_pair, file=self.outfile)

	def generate_question_answer_pairs(self, relation_name):
		"""
		From a given relation_name, pick the buffer and start to generate Q/A pairs for each stored RelationExtraction.
		:param relation_name: the relation_name, which is also the identifier of the relation.
		:return: yield a Q/A string
		"""
		question_patterns = self.relation2patterns[relation_name]
		relation_instances = self.sampled_instances[relation_name]
		for rel_inst in relation_instances:
			for q in question_patterns:
				new_qa_pairs = []
				cur_relation = relation_name
				cur_sentence = rel_inst.source
				cur_source = rel_inst.left_concept.mention + "::" + rel_inst.left_concept.babelNetID
				cur_target = rel_inst.right_concept.mention + "::" + rel_inst.right_concept.babelNetID
				# If the question is not binary (i.e.: has only the "X" left concept placeholder)
				if not q.is_binary_question():
					# Only one replace
					cur_question = q.question.replace(q.left_placeholder,rel_inst.left_concept.mention)
					cur_answer = rel_inst.right_concept.mention
					new_qa_pair = "\t".join(
						[cur_question, cur_answer, cur_relation, cur_sentence, cur_source, cur_target])
					new_qa_pairs.append(new_qa_pair)
				else:
					# Two replace, both for left and right concept (X and Y)
					# Positive case
					cur_positive_question = q.question \
						.replace(q.left_placeholder, rel_inst.left_concept.mention) \
						.replace(q.right_placeholder, rel_inst.right_concept.mention)
					cur_positive_answer = "yes"
					new_positive_qa_pair = "\t".join([cur_positive_question, cur_positive_answer, cur_relation, cur_sentence, cur_source, cur_target])
					new_qa_pairs.append(new_positive_qa_pair)

					# Negative case
					if any(temp_rel_inst.left_concept.mention != rel_inst.left_concept.mention for temp_rel_inst in relation_instances):
						# Pick at random a right concept, different from the good one.
						bad_rel_inst = random.choice(relation_instances)
						while bad_rel_inst.left_concept.mention == rel_inst.left_concept.mention:
							bad_rel_inst = random.choice(relation_instances)

						cur_negative_question = q.question \
							.replace(q.left_placeholder, rel_inst.left_concept.mention) \
							.replace(q.right_placeholder, bad_rel_inst.right_concept.mention)
						cur_negtive_answer = "no"
						cur_target = bad_rel_inst.right_concept.mention + "::" + rel_inst.right_concept.babelNetID
						new_negative_qa_pair = "\t".join([cur_negative_question, cur_negtive_answer, cur_relation, cur_sentence, cur_source, cur_target])
						new_qa_pairs.append(new_negative_qa_pair)


				for qa in new_qa_pairs:
					yield qa
		self.sampled_instances[relation_name] = []
