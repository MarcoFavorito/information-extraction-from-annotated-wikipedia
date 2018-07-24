from utils.seeds import RelationExtractor
import configurations as conf
def parse_seed_file(filepath):
	"""
	Parse a seed file, with the format as specified in the README.
	:return: a list of RelationExtractor objects.
	"""
	with open(filepath, "r") as f:
		s = f.read().strip("\n\t ")
		relations_seeds = s.split(";")
		if relations_seeds[-1]=="":
			relations_seeds = relations_seeds[:-1]

		relation_extractors = [get_relation_extractor(rel_string.strip("\n\t "))
							   for rel_string in relations_seeds]
	return relation_extractors

def get_relation_extractor(relation_seeds_string):
	"""

	:param relation_seeds_string: "RELATION_NAME:relational_phrase1,relational_phrase2,...
	:return: a RelationExtractor object
	"""

	relation_name, seeds = relation_seeds_string.replace("\n","").replace("\t","").split(":")
	seeds_and_sim = seeds.split("_")

	if len(seeds_and_sim)==2:
		(splitted_seeds, sim_threshold)= (seeds.split("_")[0].split(","), float(seeds.split("_")[1]))
	elif len(seeds_and_sim)==1:
		(splitted_seeds, sim_threshold) =  (seeds.split("_")[0].split(","), conf.DEFAULT_SIMILARITY_THRESHOLD)
	else:
		raise Exception("Badly formed seed file.")
	splitted_seeds = list(map(lambda x: x.strip("\n\t "), splitted_seeds))
	relation_extractor = RelationExtractor(relation_name, splitted_seeds, sim_threshold)
	return relation_extractor