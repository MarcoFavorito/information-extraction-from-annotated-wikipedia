"""
A "singleton" module for retrieve the loaded-only-once-in-memory spaCy model, when needed.
"""
import spacy


# lazy initialization
spacy_parser = None

def get_spacy_parser():
	global spacy_parser
	if spacy_parser==None:
		try:
			spacy_parser = spacy.load("en_core_web_md")
		except IOError:
			spacy_parser = spacy.load("en_core_web_sm")
	return spacy_parser
