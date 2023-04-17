from .label import labels_of

def order(notes, reverse=False):
	couples = []
	for note in notes:
		labels = filter(lambda x: x.isnumeric(), labels_of(note))
		order = min(list(map(int, labels)) + [0xFFFFFFFF])
		couples.append((order, note))
	couples.sort(reverse=reverse, key=lambda x: x[0])
	return list(map(lambda x: x[1], couples))