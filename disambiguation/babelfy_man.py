import copy

import configurations as conf
import constants as c
from disambiguation.BabelNetConcept import BabelNetConcept
from disambiguation.Disambiguation import Disambiguation


def disambiguate_sentences(sentences, annotations):
    """
	Method for disambiguate a list of sentences from a list of annotation,
	usually corresponding to the list of sentences and annotation of an entire Wikipedia article
	:param sentences: a list of sentences. One sentence is a list of words (strings)
	:param annotations: a list of Annotation object.
	:return: a list of disambiguated sentences. A disambiguated sentence consists in a list of Disambiguation objects.
	"""
    start_tag_index = 0
    end_tag_index = 0
    nb_annotations = 0
    disambiguated_sentences = []

    for i, sent in enumerate(sentences):
        end_tag_index = start_tag_index + len(sent)
        sent_annotations = filter(lambda x:
                                  int(x.anchorStart) >= start_tag_index and
                                  int(x.anchorEnd) < end_tag_index,
                                  annotations[nb_annotations:])

        norm_sent_annotations = list(map(lambda x: _normalize_annotation(x, start_tag_index), sent_annotations))
        nb_annotations += len(norm_sent_annotations)

        disamb_sent = disambiguate_sentence(sent, norm_sent_annotations)

        disambiguated_sentences.append(disamb_sent)
        # beacuse between each sentence of the corpus, a sort of "null tag" is counted...
        start_tag_index = end_tag_index + 1

    return disambiguated_sentences


def disambiguate_sentence(sentence, sent_annotations):
    """
	Disambiguate a single sentence.
	:param sentence: a list of tokens (strings)
	:param sent_annotations: a list of Annotation objects
	:return: a list of Disambiguation objects
	"""

    disambiguation_dict_list = []

    # get a dictionary
    # from ranges of indexes
    # to BabelNetConcept that summarize the annotations which fall into that range
    # 	and merge all of them.
    #
    # for example:
    # 	consider this words: "public law school"
    # 	consider that the concepts are (independently from the type!): "public law"; "law school"
    # 	the merged concept will be: "public law school", with a new concept ID (stored in configurations.NEW_CONCEPTS)
    # 	the new variable is similar to the following dict: {(0,3): BabelNetConcept("public law school")}
    #
    #
    # 	notice however that configurations.NEW_CONCEPTS is not used in any particular way,
    # 	it is a way to keep track of changes.
    #
    merged_sent_annotations = _merge_overlapping_concepts(sent_annotations)

    # For each word of the sentence,
    # map it to a Disambiguation object,
    # that will be stored in a list at the same index of the word
    for i, word in enumerate(sentence):

        range_key = [r for r in merged_sent_annotations if i >= r[0] and i < r[1]]

        assert len(range_key) <= 1
        if range_key == []:
            concept = _default_concept(word, i)
        else:
            concept = merged_sent_annotations[range_key[0]]

        disambiguation_dict_list.append(
            Disambiguation(word, concept)
        )

    return disambiguation_dict_list


def _default_concept(word, anchorStart):
    """
	Returns a null concept from a single word.
	:param word: the word (string)
	:param anchorStart: the start index in the sentence
	:return: a BabelNetConcept (a null one)
	"""
    kargs = {
        "mention": word,
        "babelNetID": c.NULL_BABELNET_ID,
        "type": c.NULL_TYPE,
        "anchorStart": anchorStart,
        "anchorEnd": anchorStart + 1,
        "subConceptList": []
    }
    return BabelNetConcept(**kargs)


def _normalize_annotation(annotation, tag_index):
    """
	Normalize the annotation anchorStart and anchorEnd,
	in the sense that we start to count the position
	from the beginning of the sentence
	and not from the beginning of the disambiguated page.
	:param annotation: Annotation object
	:param tag_index: start index (int)
	:return: a new Annotation object
	"""
    # norm_annotation = copy.deepcopy(annotation)
    norm_annotation = annotation
    norm_annotation.anchorStart = int(annotation.anchorStart) - tag_index
    norm_annotation.anchorEnd = int(annotation.anchorEnd) - tag_index

    return copy.copy(norm_annotation)


def _merge_overlapping_concepts(sent_annotations):
    """
	From a list of annotation, produce a dictionary
	from the range of indexes to a BabelNetConcept object
	which summarize the subconcept in that range.
	:param sent_annotations: a list of Annotation object
	:return: a dictionary
		from a tuple of indexes (start, end)
		to a BabelNetConcept object which contains all the annotations in that range
	"""

    # the returned dictionary
    anchorRange2concept = {}

    # produce a list of the largest non-overlapping ranges from a list of annotation ranges
    ranges = list(map(lambda x: (x.anchorStart, x.anchorEnd), sent_annotations))
    merged_ranges = _merge_ranges(ranges)

    # a dictionary from a range to a list of Annotations.
    # It will be used for merge annotations which fall in the same merged range
    anchorRange2annotation = {k: [] for k in merged_ranges}

    # for each annotation:
    # 	1 - find the range to which the annotation belongs;
    # 	2 - add it to the list of annotation that belongs to that range
    for annotation in sent_annotations:
        range_key = [r for r in anchorRange2annotation
                     if annotation.anchorStart >= r[0] and
                     annotation.anchorEnd <= r[1]
                     ][0]
        anchorRange2annotation[range_key] += [annotation]

    # for each range of annotations:
    # 	1 - find the annotation with the largest range
    # 		if there is only one (i.e.: there is a "dominant" concept as wide as the range)
    # 			create a new concept with the "dominant" mention and put all the annotation in the subConceptList
    # 		if not (it probably means that there exist overlapping annotations
    # 			merge all the annotation (call the function "_merge_concept_from_annotations")
    for r, annotation_list in anchorRange2annotation.items():
        largest_range_annotation = [(i, ann) for i, ann in enumerate(annotation_list) if
                                    ann.anchorStart == r[0] and ann.anchorEnd == r[1]]

        if len(largest_range_annotation) == 1:
            idx, ann = largest_range_annotation[0]
            kargs = {
                "mention": ann.mention,
                "babelNetID": ann.babelNetID,
                "type": ann.type,
                "anchorStart": ann.anchorStart,
                "anchorEnd": ann.anchorEnd,
                "subConceptList": annotation_list
            }
            anchorRange2concept[r] = BabelNetConcept(**kargs)
        else:
            merged_concept = _merge_concept_from_annotations(annotation_list)
            anchorRange2concept[r] = merged_concept

    return anchorRange2concept


def _merge_ranges(ranges):
    """
	From a list of ranges (i.e.: list of tuples (start_idx, end_idx)
	Produce a list of non-overlapping ranges, merging those which overlap.
	:param ranges: list of tuples (start_idx, end_idx)
	:return: list of tuples (start_idx, end_idx)
	"""
    if ranges == []:
        return []
    ranges = sorted(ranges)
    merged_ranges = []

    cur_range = ranges[0]
    for r in ranges[1:]:
        if r[0] >= cur_range[0] and r[0] < cur_range[1]:
            cur_range = (cur_range[0], max(r[1], cur_range[1]))
        else:
            merged_ranges.append(cur_range)
            cur_range = r

    merged_ranges.append(cur_range)
    return merged_ranges


def _merge_concept_from_annotations(annotation_list):
    """
	Merge overlapping annotations to a single BabelNetConcept object
	:param annotation_list: a list of Annotation objects
	:return: a BabelNetConcept object:
		- with all the input annotations as subconcept;
		- with only one main concept selected (or created) from the annotations
	"""
    max_end = 0
    merged_mention = ""
    annotation_list = sorted(annotation_list, key=lambda x: (x.anchorStart, x.anchorEnd))
    min_start = annotation_list[0].anchorStart

    # iterate over all the annotations for merge the mention string.
    # all this unreadable code compute the mention considering the
    # overlapping of the mentions.
    for annotation in annotation_list:
        r = (annotation.anchorStart, annotation.anchorEnd)
        if max_end < r[1]:
            new_start_index = max_end - r[0]
            new_start_index = new_start_index if new_start_index >= 0 else 0
            spl_mention = annotation.mention.split()
            l = spl_mention[new_start_index:]
            merged_mention += " " + " ".join(spl_mention[new_start_index:])
            max_end = r[1]

    # remove the first character if it is a space
    if merged_mention[0] == " ":
        merged_mention = merged_mention[1:]

    # create a new concept with the merged mention and a new concept ID
    kargs = {
        "mention": merged_mention,
        "babelNetID": conf.NUM_NEW_CONCEPT,
        "type": c.CUSTOM_TYPE,
        "anchorStart": min_start,
        "anchorEnd": max_end,
        "subConceptList": annotation_list
    }

    new_concept = BabelNetConcept(**kargs)

    # store in the global data structure.
    conf.NEW_CONCEPTS[conf.NUM_NEW_CONCEPT] = new_concept
    conf.NUM_NEW_CONCEPT += 1
    return new_concept
