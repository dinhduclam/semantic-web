from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from chevie_namespace import rdf, rdfs, owl, base, dbo, time
from utils import uri_exists
import GeminiAPI
import extract_HistoricalFigure


def add_dynastic_to_ontology(uri: str, g: Graph):
    if uri_exists(g, uri):
        print(f"{uri} exists!")
        print("---------------")
        return uri

    try:
        results = query_dynasty_from_dbpedia(uri)["results"]["bindings"]
    except:
        print(f"An exception occurred for uri {uri}")
        return uri

    if results is None or len(results) == 0:
        print(f"No data from DBpedia found for {uri}")
        return uri

    name = results[0]["label"]["value"]
    slug = name.replace(" ", "_")
    dynasty_uri = URIRef(base + slug)

    if uri_exists(g, dynasty_uri):
        print(f"{name} exists!")
        print("---------------")
        return dynasty_uri

    g.add((dynasty_uri, rdf.type, base.HistoricalDynasty))
    g.add((dynasty_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            label = res["label"]["value"]
            g.add((dynasty_uri, rdfs.label, Literal(label)))

        interval_uri = URIRef(base + f"{slug}_ExistenceTime")
        g.add((interval_uri, rdf.type, time.Interval))
        g.add((dynasty_uri, base.span, interval_uri))

        if "begin" in res:
            start = res["begin"]["value"]
            g.add((interval_uri, time.hasBeginning, Literal(start, datatype=XSD.date)))

        if "end" in res:
            end = res["end"]["value"]
            g.add((interval_uri, base.hasEnd, Literal(end, datatype=XSD.date)))

        if "formIn" in res:
            country = res["formIn"]["value"]
            g.add((dynasty_uri, base.formedIn, URIRef(country)))

    if not any(g.triples((dynasty_uri, base.hasEvent, None))):
        figure_list = GeminiAPI.get_historical_figure_list_from_dynasty(name)
        for figure in figure_list:
            figure_uri = extract_HistoricalFigure.add_historical_figure_to_ontology(figure["link"], g)
            g.add((figure_uri, base.liveIn, URIRef(dynasty_uri)))

    for predicate, obj in g.predicate_objects(subject=dynasty_uri):
        print(f"HistoricalDynasty: {predicate} -> {obj}")
    print("---------------")

    return dynasty_uri


def query_dynasty_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT DISTINCT ?label ?formIn ?begin ?end WHERE {{
          <{uri}> rdfs:label ?label .
          FILTER(LANG(?label) = 'en') .
          OPTIONAL {{ <{uri}> dbp:country ?formIn . }}
          OPTIONAL {{ <{uri}> dbo:foundingDate ?begin . }}
          OPTIONAL {{ <{uri}> dbo:dissolutionDate ?end . }}
        }}
        """)

    print(f"Query HistoricalDynasty: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()