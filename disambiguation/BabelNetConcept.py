import constants as c

class BabelNetConcept(object):
	"""
	This class represents the annotation schema provided in the annotated corpus.
	There is also the field "subConceptList", used to keep in memory the concepts
	from which a concept has been generated (for example, when we merge overlapping concepts).
	"""

	def __init__(self, mention, babelNetID, type, anchorStart=-1, anchorEnd=-1, subConceptList = []):
		self.mention = mention
		self.babelNetID = babelNetID
		self.type = type
		self.anchorStart = anchorStart
		self.anchorEnd = anchorEnd
		self.subConceptList = subConceptList

		self.values = [self.mention, self.babelNetID, self.type, self.anchorStart, self.anchorEnd, self.subConceptList]
		self.fields = ["mention", "babelNetID", "type", "anchorStart", "anchorEnd", "subConceptList"]
		assert len(self.values)==len(self.fields)

	def isNullConcept(self):
		return self.babelNetID==c.NULL_BABELNET_ID

	def __eq__(self, other):
		if other==None:
			return False
		return all(this_v == other_v for this_v, other_v in zip(self.values, other.values))

	def __repr__(self):
		return " ".join(map(
			lambda x: x[0] + ":" + x[1], zip(self.fields, map(str,self.values))
		))

