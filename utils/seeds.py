import utils.dependency_parser as dep_parser
import configurations as conf

parser = dep_parser.get_spacy_parser()



class RelationExtractor(object):
	"""
	This class represent the extractor object which compute all it is needed for retrieve new relation instances.
	"""
	def __init__(self, name, seeds, similarity_threshold=conf.DEFAULT_SIMILARITY_THRESHOLD):
		self.name = name
		# a list of strings
		self.initial_seeds = seeds
		# a float
		self.similarity_threshold = similarity_threshold
		# a list of tuples in the form (dep_parsed_rel_phrase, similarity_handicap), where:
		# 	- dep_parsed_rel_phrase is the object returned by the spaCy dependency parser
		# 		over the fictitious sentence (adding "X" and "Y");
		# 	- similarity_handicap is 1.0 for root seeds; for second or higher level seeds,
		# 		this value is exactly the similarity that brings them in the RelationExtractor.
		# 		It is used for decrease the computed similarity with not-root seeds
		self.parsed_seeds = [(next(parser("X " + relational_phrase + " Y").sents), 1.) for relational_phrase in seeds]

		# a list of strings, contains zero-level seeds and higher-level ones when they are inserted.
		self.current_seeds = seeds[:]

	def is_compliant(self, relational_phrase):
		"""
		Decides if a relational phrase (i.e. a string) has enough similarity to one of the seeds.
		:param relational_phrase: a string
		:return: a boolean:
			True if the relational phrase has enough similarity with at least one of the seeds;
			False otherwise
		"""
		if relational_phrase in self.current_seeds:
			return True

		# parse the relational phrase with two fictitious subject and objects
		# however, these two tokens are not considered directly in the similarity computation
		artificial_rel_ph = "X " + relational_phrase + " Y"
		parsed_artificial_rel_ph =list(parser(artificial_rel_ph).sents)

		# this "if" manages the case when the parser identify two sentences, instead than one.
		if len(parsed_artificial_rel_ph) != 1:
			return False
		else:
			parsed_artificial_rel_ph =parsed_artificial_rel_ph[0]

		for (s, sim_threshold) in self.parsed_seeds:
			new_sim = s[1:-1].similarity(parsed_artificial_rel_ph[1:-1])
			if new_sim*sim_threshold >= self.similarity_threshold:
				self.parsed_seeds.append((parsed_artificial_rel_ph, new_sim*sim_threshold))
				self.current_seeds.append(relational_phrase)
				return True
		return False

	def __str__(self):
		return self.name + ":" + ",".join(self.current_seeds)+"\t"+str(self.similarity_threshold)
