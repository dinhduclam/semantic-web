from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from chevie_namespace import rdf, rdfs, owl, base, dbo
from GeminiAPI import get_festival_list_from_site, get_historic_event_list_from_site
from extract_Festival import add_festival_to_ontology
from extract_HistoricEvent import add_event_to_ontology
import extract_HistoricalFigure
from utils import uri_exists


def add_site_to_ontology(uri: str, g: Graph):
    if uri_exists(g, uri):
        print(f"{uri} exists!")
        print("---------------")
        return uri

    try:
        results = query_site_from_dbpedia(uri)["results"]["bindings"]
    except:
        print(f"An exception occurred for uri {uri}")
        return uri

    if results is None or len(results) == 0:
        print(f"No data from DBpedia found for {uri}")
        return uri

    name = results[0]["label"]["value"]
    site_uri = URIRef(base + name.replace(" ", "_"))

    if uri_exists(g, site_uri):
        print(f"{name} exists!")
        print("---------------")
        return site_uri

    g.add((site_uri, rdf.type, base.Site))
    g.add((site_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            g.add((site_uri, rdfs.label, Literal(res["label"]["value"])))

        if "location" in res:
            g.add((site_uri, base.sitePlace, URIRef(res["location"]["value"])))

        if "builder" in res:
            g.add((site_uri, base.builtBy, URIRef(res["builder"]["value"])))

        if "dynasty" in res:
            g.add((site_uri, base.buildIn, URIRef(res["dynasty"]["value"])))

        if "memorial" in res:
            g.add((site_uri, base.commemorate, URIRef(res["memorial"]["value"])))

        if "event" in res:
            g.add((site_uri, base.hasEvent, URIRef(res["event"]["value"])))

        if "festival" in res:
            g.add((site_uri, base.hasFestival, URIRef(res["festival"]["value"])))

        if "level" in res:
            g.add((site_uri, base.siteLevel, Literal(res["level"]["value"])))

    if not any(g.triples((site_uri, base.hasFestival, None))):
        festival_list = get_festival_list_from_site(name)
        for festival in festival_list:
            festival_uri = add_festival_to_ontology(festival["link"], g)
            g.add((site_uri, base.hasFestival, URIRef(festival_uri)))

    if not any(g.triples((site_uri, base.hasEvent, None))):
        event_list = get_historic_event_list_from_site(name)
        for event in event_list:
            event_uri = add_event_to_ontology(event["link"], g)
            g.add((site_uri, base.siteCommemorateEvent, URIRef(event_uri)))

    for s, p, o in g.triples((site_uri, base.builtBy, None)):
        if isinstance(o, URIRef):
            figure_uri = extract_HistoricalFigure.add_historical_figure_to_ontology(o, g)
            g.add((site_uri, base.builtBy, figure_uri))

    for predicate, obj in g.predicate_objects(subject=site_uri):
        print(f"Site: {predicate} -> {obj}")
    print("---------------")

    return site_uri


def query_site_from_dbpedia(site_uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT ?label ?location ?builder ?dynasty ?memorial ?event ?festival ?level WHERE {{
          <{site_uri}> rdfs:label ?label .
          FILTER(LANG(?label) = 'en')
          OPTIONAL {{ <{site_uri}> dbo:location ?location . }}
          OPTIONAL {{ <{site_uri}> dbo:builder ?builder . }}
          OPTIONAL {{ <{site_uri}> dbo:dynasty ?dynasty . }}
          OPTIONAL {{ <{site_uri}> dbo:dedicatedTo ?memorial . }}
          OPTIONAL {{ <{site_uri}> dbo:knownFor ?event . }}
          OPTIONAL {{ <{site_uri}> dbo:festival ?festival . }}
          OPTIONAL {{ <{site_uri}> dbp:level ?level . }}
        }}
        """)

    print(f"Query Site: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()