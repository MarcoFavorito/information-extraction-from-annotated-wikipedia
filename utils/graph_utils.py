"""
This module use the networkx package to deal with graphs.
"""
from networkx import DiGraph
from networkx.algorithms.shortest_paths.unweighted import all_pairs_shortest_path
from networkx.algorithms.shortest_paths.unweighted import single_source_shortest_path

import constants as c


def build_networkXGraph_from_spaCy_depGraph(sentence):
	"""
	Given a spaCy-parsed sentence, return the relative networkXGraph.
	"""
	g = DiGraph()
	tokens = list(sentence)
	g.add_nodes_from(tokens)
	_add_edges_from_spaCy_depGraph(g, sentence.root)
	return g


def _add_edges_from_spaCy_depGraph(g, node):
	for left_child in node.lefts:
		g.add_edge(left_child, node)
		_add_edges_from_spaCy_depGraph(g, left_child)
	for right_child in node.rights:
		g.add_edge(node, right_child)
		_add_edges_from_spaCy_depGraph(g, right_child)


def find_shortest_paths(sentence):
	g = build_networkXGraph_from_spaCy_depGraph(sentence)
	all_shortest_paths = all_pairs_shortest_path(g)
	return all_shortest_paths

def find_shortest_paths_from_source(sentence, start_token):
	g = build_networkXGraph_from_spaCy_depGraph(sentence)
	shortest_paths_from_source = single_source_shortest_path(g, start_token)
	return shortest_paths_from_source


def filter_paths(paths_dict):
	"""
	Filter paths in the form provided by NetworkX (i.e.: {start_node_id: {end_node_id: [path]}})
	:return: "happy" paths, i.e. paths which satisfy some requirements
	"""
	happy_paths = []
	for start_node, end_nodes_dict in paths_dict.items():
		for end_node, path in end_nodes_dict.items():
			cur_path = paths_dict[start_node][end_node]
			if satisfyRequirements(cur_path):
				happy_paths.append(cur_path)
	return happy_paths


def satisfyRequirements(path):
	""" Method for check if the path between spaCy tokens is appropriate to be retrieved"""
	if not hasVerb(path):
		return False
	if not hasConceptsAtTheEnds(path):
		return False
	if not isConceptDefinition(path):
		return False

	return True


def hasVerb(path):
	return sum(1 for t in path if t.pos_==c.VERB_POSTAG and t.dep_ != "auxpass" and t.dep_ != "aux")<=1

def hasConceptsAtTheEnds(path):
	return (path[0].ent_id_ != c.NULL_BABELNET_ID
			or path[0].pos_ ==c.PRON_POSTAG
			or path[0].pos_ ==c.PROPN_POSTAG) and \
		path[-1].ent_id_ != c.NULL_BABELNET_ID


def isConceptDefinition(path):
	return (path[0].dep_ in c.SUBJ_DEPTAGS) and \
		   (path[-1].dep_ in c.OBJ_DEPTAGS)


def extract_triple(path):
	return (path[0], path[1:-1], path[-1])