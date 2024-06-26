from ..keep import keep

def sync():
	yield "sync requested"

	try:
		keep.sync()
		yield "sync successful"
	except Exception as e:
		yield "sync failed"
		yield str(e)