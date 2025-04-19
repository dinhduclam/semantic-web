from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from chevie_namespace import rdf, rdfs, owl, base
from utils import uri_exists


def add_festival_to_ontology(uri: str, g: Graph):
    if uri_exists(g, uri):
        print(f"{uri} exists!")
        print("---------------")
        return uri

    try:
        results = query_festival_from_dbpedia(uri)["results"]["bindings"]
    except:
        print(f"An exception occurred for uri {uri}")
        return uri

    if results is None or len(results) == 0:
        print(f"No data from DBpedia found for {uri}")
        return uri

    name = results[0]["label"]["value"]
    festival_uri = URIRef(base + name.replace(" ", "_"))

    if uri_exists(g, festival_uri):
        print(f"{name} exists!")
        print("---------------")
        return festival_uri

    g.add((festival_uri, rdf.type, base.Festival))
    g.add((festival_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            g.add((festival_uri, rdfs.label, Literal(res["label"]["value"])))

        if "place" in res:
            g.add((festival_uri, rdfs.festivalPlace, URIRef(res["place"]["value"])))

        if "religion" in res:
            g.add((festival_uri, base.relatedToReligion, URIRef(res["religion"]["value"])))

        if "ethnic" in res:
            g.add((festival_uri, base.relatedToEthnicGroup, URIRef(res["ethnic"]["value"])))

    for predicate, obj in g.predicate_objects(subject=festival_uri):
        print(f"Festival: {predicate} -> {obj}")
    print("---------------")

    return festival_uri


def query_festival_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f""" 
            SELECT DISTINCT ?label ?place ?religion ?ethnic
            WHERE {{
                <{uri}> rdfs:label ?label .
                FILTER(LANG(?label) = 'en') .
                OPTIONAL {{ <{uri}> (dbo:place | dbp:district | dbp:country) ?place. }}
                OPTIONAL {{ <{uri}> dbo:religion ?religion. }}
                OPTIONAL {{ <{uri}> dbo:ethnicGroup ?ethnic. }}
            }}
            LIMIT 10
        """)

    print(f"Query Festival: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
