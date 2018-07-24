import gzip
import os
import re

import xmltodict
from lxml import etree

import constants as c



def get_docs_list_by_subdir(wikipedia_dir):
	"""
	read into the dataset_dir and yield subdirs and files.
	:param wikipedia_dir: the path to the dataset directory
	:return: a tuple (current_subdir, list_of_filepaths), where:
		- current_subdir is the integer representing the subdirectory name;
		- list_of_filepaths is the list of filepaths into the current subdirectory.
	"""
	for subdir in sorted(os.listdir(wikipedia_dir), key=lambda x: int(x)):
		d = wikipedia_dir + "/" + subdir + "/"
		yield int(subdir), list(map(lambda x: d + x, os.listdir(d)))


class LxmlParser(object):
	"""
	This class is used for the parsing of Wikipedia pages in XML format, compressed.
	"""

	def __init__(self, xml_path):
		"""

		:param xml_path:
		"""
		self.xml_path = xml_path
		self.parsed_xml = etree.parse(xml_path)

	def get_text(self):
		"""
		return the entire text of the Wikipedia page
		"""
		text = self.parsed_xml.getroot()[c.TEXT_TAG_IDX].text
		if text == None:
			text = ""
		return text.replace("\n", "")

	def get_sentences(self, num_of_sentences=-1):
		"""
		Get the first "num_of_sentences" sentences.
		If num_of_sentences=-1, returns all the sentences from the Wikipedia page.
		:param num_of_sentences:
		:return:
		"""
		try:
			spl_lines = iter(self.parsed_xml.getroot()[c.TEXT_TAG_IDX].text.splitlines())
		except AttributeError:
			return []
		for i, line in enumerate(spl_lines):
			if num_of_sentences==-1 or i<num_of_sentences:
				spl_line = re.split(" +", line)
				if spl_line[-1]=='':
					del spl_line[-1]
				yield spl_line
			else:
				break

	def get_annotations_by_type_and_range(self, type, anchorStart, anchorEnd):
		"""
		Get annotations from the Wikipedia page in the range defined by anchorStart and anchorEnd,
		filtered by type.
		:param type: "BABELFY", "MCS" or "HL".
		:param anchorStart: start index of the range used for filter the annotations.
		:param anchorEnd: end index of the range used for filter the annotations.
		:return: a list of Annotations objects.
		"""
		for ann_el in self.parsed_xml.getroot()[c.ANNOTATIONS_TAG_IDX]:
			try:
				ann_anchorStart = int(ann_el[c.ANNOTATION_ANCHORSTART_POS].text)
				ann_anchorEnd = int(ann_el[c.ANNOTATION_ANCHOREND_POS].text)
			except:
				continue
			if ann_anchorStart>=anchorStart and ann_anchorEnd<=anchorEnd:
				if ann_el[c.ANNOTATION_TYPE_TAG_POS].text==type:
					yield Annotation(
						ann_el[c.ANNOTATION_BABELNETID_TAG_POS].text,
						ann_el[c.ANNOTATION_MENTION_POS].text,
						ann_el[c.ANNOTATION_ANCHORSTART_POS].text,
						ann_el[c.ANNOTATION_ANCHOREND_POS].text,
						ann_el[c.ANNOTATION_TYPE_TAG_POS].text,
					)
				else:
					continue
			else:
				break

	def get_annotations_by_range(self, anchorStart, anchorEnd):
		"""
		Get annotations from the Wikipedia page in the range defined by anchorStart and anchorEnd.
		:param anchorStart: start index of the range used for filter the annotations.
		:param anchorEnd: end index of the range used for filter the annotations.
		:return: a list of Annotations objects.
		"""
		for ann_el in self.parsed_xml.getroot()[c.ANNOTATIONS_TAG_IDX]:
			try:
				ann_anchorStart = int(ann_el[c.ANNOTATION_ANCHORSTART_POS].text)
				ann_anchorEnd = int(ann_el[c.ANNOTATION_ANCHOREND_POS].text)
			except:
				continue
			if ann_anchorStart>=anchorStart and ann_anchorEnd<=anchorEnd:
				yield Annotation(
					ann_el[c.ANNOTATION_BABELNETID_TAG_POS].text,
					ann_el[c.ANNOTATION_MENTION_POS].text,
					ann_el[c.ANNOTATION_ANCHORSTART_POS].text,
					ann_el[c.ANNOTATION_ANCHOREND_POS].text,
					ann_el[c.ANNOTATION_TYPE_TAG_POS].text,
				)
			else:
				break



class Annotation(object):
	"""
	This class represent the annotation element in the provided XML schema.
	"""

	def __init__(self, babelNetID, mention, anchorStart, anchorEnd, type):
		self.babelNetID = babelNetID
		self.mention = mention
		self.anchorStart = anchorStart
		self.anchorEnd = anchorEnd
		self.type = type

	def __repr__(self):
		return " ".join([self.babelNetID, self.mention, str(self.anchorStart), str(self.anchorEnd), self.type])




# OLD STUFF: not used anymore.
# def get_docs(wikipedia_dir):
# 	for subdir in sorted(os.listdir(wikipedia_dir), key=lambda x: int(x)):
# 		for xml_file in os.listdir(wikipedia_dir + "/" + subdir):
# 			cur_path = wikipedia_dir + "/" + subdir + "/" + xml_file
# 			yield int(subdir), cur_path
#
#
# def open_gzip_file(gzip_filepath):
# 	return gzip.open(gzip_filepath)
#
# class XmlToDictParser(object):
# 	def __init__(self, xml_text):
# 		self.doc = xmltodict.parse(xml_text)
#
# 	def get_sentences(self):
# 		sentences = self.doc[c.DISAMBIGUATED_ARTICLE_TAG][c.TEXT_TAG]
# 		if sentences != None:
# 			ss = list(map(lambda x: re.split(" +", x), sentences.splitlines()))
# 			for s in ss:
# 				if s[-1]=='':
# 					del s[-1]
# 			return ss
# 		else:
# 			return []
#
#
# 	def get_annotations(self):
# 		res = self.doc[c.DISAMBIGUATED_ARTICLE_TAG][c.ANNOTATIONS_TAG]
# 		if res==None:
# 			return []
# 		res = res[c.ANNOTATION_TAG]
# 		try:
# 			assert res.__class__==list
# 		except:
# 			res = [res]
#
# 		res = [Annotation(
# 			ann[c.BABELNET_ID_TAG],
# 			ann[c.MENTION_TAG],
# 			ann[c.ANCHOR_START_TAG],
# 			ann[c.ANCHOR_END_TAG],
# 			ann[c.TYPE_TAG],
# 		)for ann in res
# 		]
# 		return res