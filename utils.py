from rdflib import Graph, URIRef


def uri_exists(g: Graph, uri: URIRef) -> bool:
    # if not isinstance(uri, URIRef):
    #     return True

    return any(g.triples((uri, None, None)))
