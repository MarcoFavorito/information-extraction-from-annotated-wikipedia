class Disambiguation(object):
	"""
	This class represent a word disambiguation.
	 in the field word there is the word to which the disambiguation is related
	 in the field concept there is a BabelNetConcept object
	"""
	def __init__(self, word, concept):
		self.word = word
		self.concept = concept

	def __repr__(self):
		return " ".join([self.word, str(self.concept)])

	def __str__(self):
		return " ".join([self.word, str(self.concept)])