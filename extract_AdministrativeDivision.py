from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal
from chevie_namespace import rdf, rdfs, owl, base
from utils import uri_exists


def add_ad_to_ontology(uri: str, g: Graph):
    results = query_ad_from_dbpedia(uri)["results"]["bindings"]
    name = results[0]["label"]["value"]
    ad_uri = URIRef(base + name.replace(" ", "_"))

    if uri_exists(g, ad_uri):
        print(f"{name} exists!")
        print("---------------")
        return ad_uri

    g.add((ad_uri, rdf.type, base.AdministrativeDivision))
    g.add((ad_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            g.add((ad_uri, rdfs.label, Literal(res["label"]["value"])))

        if "knowAs" in res:
            g.add((ad_uri, base.knowAsDivision, URIRef(res["knowAs"]["value"])))

    for predicate, obj in g.predicate_objects(subject=ad_uri):
        print(f"AdministrativeDivision: {predicate} -> {obj}")
    print("---------------")

    return ad_uri


def query_ad_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f""" 
            SELECT DISTINCT ?label ?knowAs
            WHERE {{
                <{uri}> rdfs:label ?label .
                FILTER(LANG(?label) = 'en') .
                OPTIONAL {{ <{uri}> (dbo:synonym | dbp:otherName) ?knowAs. 
                    FILTER(STRLEN(STR(?knowAs)) > 0). 
                    FILTER(LANG(?knowAs) = 'en').}}
            }}
            LIMIT 10
        """)

    print(f"Query AdministrativeDivision: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
