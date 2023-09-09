from flask import current_app
from pyoxigraph import NamedNode, Literal, DefaultGraph, Triple, Quad, Variable
from uuid_extensions import uuid7str

#lang_bp = Blueprint("lang", __name__, url_prefix="/lang", template_folder="templates")

XSD_NAMES = ["int", "integer", "double", "float", "date", "time", "dateTime"]
LANGUAGES = ["cz", "en", "fr"]


class Prefix:
	def __init__(self, url, name):
		self.url = url
		self.name = name

	def inv(self, x):
		if x not in self:
			raise ValueError(f"{ x } does not belong to { self.url } prefix space")
		return x.value[len(self.url):]

	def __getattr__(self, name: str) -> NamedNode:
		return NamedNode(self.url + name)

	def __getitem__(self, name: str) -> NamedNode:
		return self.__getattr__(name)

	def __contains__(self, item: NamedNode) -> bool:
		return item.value.startswith(self.url)


zmt = Prefix("https://zmet.krnak.cz/ns/", "")
xsd = Prefix("http://www.w3.org/2001/XMLSchema#", "xsd")
rdf = Prefix("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "rdf")
rdfs = Prefix("http://www.w3.org/2000/01/rdf-schema#", "rdfs")
owl = Prefix("http://www.w3.org/2002/07/owl#", "owl")

PREFIXES = [zmt, xsd, rdf, rdfs, owl]


def bnode():
	return NamedNode("urn:uuid:" + uuid7str())


def log(x):
	current_app.logger.info(x)
	#print(x)
	#pass

def parse(text: str):
	quads = []

	# STATE
	subjects = []
	#bnode = []
	current_graph = DefaultGraph()
	edges_attributes = []
	last_triple = None
	text_lang = None

	splitter = "\r\n" if "\r\n" in text else "\n"
	lines = text.split(splitter)
	lines.reverse() # to be able to pop

	def add_triple(s, p, o):
		triple = Triple(s, p, o)
		log("adding triple " + show(triple) + " to " + str(current_graph))
		quads.append(Quad(s, p, o, current_graph))
		last_triple = triple
		for attr in edges_attributes:
			quads.append(Quad(triple, attr[0], attr[1], current_graph))

	def literal(x):
		return Literal(x, language=text_lang)

	def parse_subject(line):
		word1 = line.split(" ")[0]
		rest = line[len(word1)+1:]
		if word1 == "()":
			return bnode(), rest
		else:
			try:
				return parse_predicate(line)
			except ValueError:
				raise ValueError(f"cannot parse { word1 } as subject")

	def parse_predicate(line):
		word1 = line.split(" ")[0]
		rest = line[1+len(word1):]
		if word1.startswith("http"):
			return NamedNode(word1), rest
		elif ":" in word1:
			pre, *rest = word1.split(":")
			for prefix in PREFIXES:
				if pre == prefix.name:
					return prefix[word1[1+len(pre):]], rest
			else:
				raise ValueError(f"unknown prefix: { pre }")
		elif word1.isidentifier():
			return zmt[word1], line[len(word1) + 1:]
		else:
			raise ValueError(f"cannot parse { word1 } as predicate")

	def parse_object(line):
		log(f"parsing object of: \"{line}\"")
		if line == "()":
			log("parsed bnode")
			return bnode()
		if line.startswith(" "):
			log("parsed literal")
			return literal(line[1:])
		word1 = line.split(" ")[0]
		if word1 in XSD_NAMES:
			log("parsed xsd datatype")
			return Literal(line[1+len(word1):], datatype=xsd[word1])
		if word1 in LANGUAGES:
			log("parsed language tagged string")
			return Literal(line[1+len(word1):], language=word1)
		if line.isidentifier():
			log("parsed zmet isidentifier")
			return zmt[line]
		if line[0] == '"' and line[-1] == '"':
			log("parsed escaped string")
			assert len(line) >= 2
			# TODO unescape symbols
			return literal(line[1:-2])
		if line == '"""':
			log("opening text block")
			text_lines = []
			line = lines.pop()
			while line != '"""':
				log("appending line:" + line)
				text_lines.append(line)
			text = "\n".join(text_lines)
			log("closing text block")
			return literal(text)
		log("parsed as literal")
		return literal(line)


	while lines:
		line = lines.pop()
		# RESET CONTEXT
		if line == "":
			subjects = []
			last_triple = None
			continue

		indent_level = 0
		while line.startswith("  "):
			line = line[2:]
			indent_level += 1
		# trim subjects
		subjects = subjects[:indent_level + 1]

		if indent_level == 0:
			# SET GRAPH
			if line.startswith("graph "):
				name = line[len("graph "):]
				log(f"switching to graph { name }")
				if name == "default":
					current_graph = DefaultGraph()
				else:
					current_graph = zmt[name]
				continue
			
			# SET EDGES PROPERTY
			elif line.startswith("edges "):
				pred, line = parse_predicate(line)
				obj = parse_object(line)
				edges_attributes.append((pred, obj))
				continue

			# SET LANGUAGE
			elif line.startswith("lang "):
				text_lang = line[len("lang "):]
				continue

		if not subjects:
			subj, line = parse_subject(line)
			log("=== " + show(subj) + " ===")
			subjects.append(subj)
			# PARSE TRIPLE LINE
			if line:
				log("moving rest of the line to next parse cycle")
				lines.append(line)
			continue
		else:
			pred, line = parse_predicate(line)
			obj = parse_object(line)
			add_triple(subjects[indent_level], pred, obj)
			subjects.append(obj)

	return quads


def show(x):
	if isinstance(x, NamedNode):
		url = x.value
		if x in zmt:
			return zmt.inv(x)
		if x in xsd:
			return "xsd:" + xsd.inv(x)
		if url.startswith("urn:uuid:"):
			return "(uuid:" + url[-6:] + ")"
		return str(x)
	if isinstance(x, Literal):
		suffix = ""
		if x.datatype:
			suffix = "^" + show(x.datatype)[4:]
		if x.language:
			suffix = "^" + x.language
		if suffix == "^string":
			suffix = ""
		return '"' + x.value + '"' + suffix
	if isinstance(x, Triple):
		return f"({ show(x.subject ) } { show(x.predicate) } { show(x.object) })"
	if isinstance(x, Quad):
		suffix = ""
		if x.graph_name != DefaultGraph():
			suffix = "@" + show(x.graph_name)
		return f"({ show(x.subject ) } { show(x.predicate) } { show(x.object) }){ suffix }"
	if isinstance(x, list):
		return "\n".join(map(show, x))
	raise ValueError(f"unknow type: { type(x) }")


if __name__ == "__main__":
	with open("/home/agi/zmet/cache/graph.txt") as file:
		data = file.read()
	triples = parse(data)
	print(show(triples))


