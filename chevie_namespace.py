from rdflib import Namespace, Graph

# already in CHeVIE.owl
base = Namespace("https://CHeVIE.vn/ontologies/")
dc = Namespace("http://purl.org/dc/elements/1.1/")
owl = Namespace("http://www.w3.org/2002/07/owl#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
xml = Namespace("http://www.w3.org/XML/1998/namespace")
xsd = Namespace("http://www.w3.org/2001/XMLSchema#")
core = Namespace("http://purl.org/vocab/frbr/core#")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
prov = Namespace("http://www.w3.org/ns/prov#")
rdfs = Namespace("http://www.w3.org/2000/01/rdf-schema#")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")
time = Namespace("http://www.w3.org/2006/time#")
terms = Namespace("http://purl.org/dc/terms/")
wgs84_pos = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
ontologies = Namespace("https://CHeVIE.vn/ontologies/")

# not in CHeVIE.owl
dbo = Namespace("http://dbpedia.org/ontology/")


def bind_namespaces(g: Graph):
    g.bind("dbo", dbo)
    for prefix, namespace in g.namespaces():
        g.bind(prefix, Namespace(namespace))
