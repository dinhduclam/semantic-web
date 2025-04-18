from rdflib import Graph, URIRef


def uri_exists(g: Graph, uri: URIRef) -> bool:
    return any(g.triples((uri, None, None)))