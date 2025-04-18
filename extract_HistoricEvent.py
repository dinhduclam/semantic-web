from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from chevie_namespace import rdf, rdfs, owl, base
from utils import uri_exists


def add_event_to_ontology(uri: str, g: Graph):
    results = query_event_from_dbpedia(uri)["results"]["bindings"]
    name = results[0]["label"]["value"]
    event_uri = URIRef(base + name.replace(" ", "_"))

    if uri_exists(g, event_uri):
        print(f"{name} exists!")
        print("---------------")
        return event_uri

    g.add((event_uri, rdf.type, base.HistoricEvent))
    g.add((event_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            g.add((event_uri, rdfs.label, Literal(res["label"]["value"])))

        if "place" in res:
            g.add((event_uri, base.eventPlace, URIRef(res["place"]["value"])))

    for predicate, obj in g.predicate_objects(subject=event_uri):
        print(f"HistoricEvent: {predicate} -> {obj}")
    print("---------------")

    return event_uri


def query_event_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f""" 
            SELECT DISTINCT ?label ?place
            WHERE {{
                <{uri}> rdfs:label ?label .
                FILTER(LANG(?label) = 'en') .
                OPTIONAL {{ <{uri}> (dbo:place | dbp:district | dbp:country) ?place. }}
            }}
            LIMIT 10
        """)

    print(f"Query HistoricalEvent: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
