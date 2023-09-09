def sort(graph):
    """
    implementation of Kahn's algoritm for graph topological sorting
    INPUT:
        graph := [node := {"ins": [int], "outs": [int]}]
    OUTPUT:
        [int]  # topographically ordered of nodes 
    """
    # Empty list that will contain the sorted elements
    L = []
    # Set of all nodes with no incoming edge
    S = [n for n, node in enumerate(graph) if not node["ins"]]

    while S:
        n = S.pop()
        L.append(n)
        while graph[n]["outs"]:
            # remove edge
            m = graph[n]["outs"].pop()
            graph[m]["ins"].remove(n)
            if not graph[m]["ins"]:
                S.append(m)

    if any(n["ins"] or n["outs"] for n in graph):
        return ValueError("graph has at least one cycle")
    else:
        return L