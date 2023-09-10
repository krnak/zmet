from ..keep import keep

def find_ref(ref):
	result = None
	for candidate in keep.find("&" + ref):
		words = candidate.title.split()
		matches = words and (words[-1] == ("&" + ref))
		if matches and result:
			raise ValueError(f"duplicated ref: { ref }")
		if matches:
			result = candidate
	if result is None:
		raise ValueError(f"ref not found: { ref }")

	return result