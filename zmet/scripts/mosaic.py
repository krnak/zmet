from ..keep import keep
from .refs import find_ref

class Mosaic:
	def __init__(self, note):
		self.note = note
		self.blocks = []

		# parse blocks
		block = {"ref": None, "head": None, "body": []}
		for line in note.text.split("\n"):
			words = line.split()
			if words and words[-1].startswith("*"):
				# new fragment found
				if block["head"] or block["body"]:
					self.blocks.append(block)
				ref = words[-1][1:]  # remove '*' symbol
				if ref == "endref":
					ref = None
				block = {"ref": ref, "body": [], "head": line}
			else:
				block["body"].append(line)

		# append last block
		if block["head"] or block["body"]:
			self.blocks.append(block)

		# merge body lines
		for block in self.blocks:
			block["text"] = "\n".join(block["body"])
			del block["body"]

	def refs(self):
		return list(filter(lambda x: x is not None, map(lambda x: x["ref"], self.blocks)))

	def finalize(self):
		lines = []
		for block in self.blocks:
			if block["head"]:
				lines.append(block["head"])
			if block["text"]:
				lines.append(block["text"])
		self.note.text = "\n".join(lines)


def update_mosaics():
	yield "running script update_mosaics"
	yield "syncing keep"
	keep.sync()

	# find and parse all mosaics
	mosaics = []
	for note in keep.find(labels=[keep.findLabel("mosaic")]):
		mosaic = Mosaic(note)
		mosaics.append(mosaic)
		yield f'found mosaic with title \"{ mosaic.note.title }\" includes:'
		for block in mosaic.blocks:
			if block["ref"]:
				yield f'- fragment *{ block["ref"] }'
			else:
				yield f'- text block'
	if not mosaics:
		yield "no mosaics found"

	# find all related references
	searched_refs = set([ref for m in mosaics for ref in m.refs()])
	refs = dict()
	versions = dict()
	for ref in searched_refs:
		try:
			note = find_ref(ref)
		except ValueError as e:
			yield str(e)

			return
		yield f"ref &{ ref } found"
		refs[ref] = note
		versions[ref] = {note.timestamps.edited: note.text}


	# consider updates from mosaics
	for mosaic in mosaics:
		for block in mosaic.blocks:
			if block["ref"]:
				versions[block["ref"]][mosaic.note.timestamps.edited] = block["text"]


	# update all sources from mosaics
	for ref, note in refs.items():
		last_edited = max(versions[ref].keys())
		new_text = versions[ref][last_edited]
		if note.text != new_text:
			note.text = new_text
			yield f'&{ ref } updated from a mosaic'
		else:
			yield f"&{ ref } unchanged"


	# update all mosaic fragmets to newest version
	for m in mosaics:
		yield f"updating mosaic with title \"{ m.note.title }\""
		for block in m.blocks:
			if block["ref"]:
				new_text = refs[block["ref"]].text

				if new_text != block["text"]:
					block["text"] = new_text
					yield f'- &{ block["ref"] } updated from source'
				else:
					yield f'- &{ block["ref"] } unchanged'

		m.finalize()

	yield "syncing keep"
	keep.sync()
	yield "mosaics updated"