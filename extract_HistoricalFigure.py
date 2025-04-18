from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from chevie_namespace import rdf, rdfs, owl, base, dbo
from extract_Site import add_site_to_ontology
from utils import uri_exists
from extract_AdministrativeDivision import add_ad_to_ontology


def add_historical_figure_to_ontology(uri: str, g: Graph):
    results = query_historical_figure_from_dbpedia(uri)["results"]["bindings"]
    name = results[0]["label"]["value"]
    figure_uri = URIRef(base + name.replace(" ", "_"))

    if uri_exists(g, figure_uri):
        print(f"{name} exists!")
        print("---------------")
        return figure_uri

    g.add((figure_uri, rdf.type, base.HistoricalFigure))
    g.add((figure_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            value = res["label"]["value"]
            g.add((figure_uri, rdfs.label, Literal(value)))

        if "abstract" in res:
            value = res["abstract"]["value"]
            g.add((figure_uri, rdfs.comment, Literal(value)))

        if "birthDate" in res:
            value = res["birthDate"]["value"]
            g.add((figure_uri, base.birthDate, Literal(value, datatype=XSD.date)))

        if "deathDate" in res:
            value = res["deathDate"]["value"]
            g.add((figure_uri, base.deathDate, Literal(value, datatype=XSD.date)))

        if "birthPlace" in res:
            value = res["birthPlace"]["value"]
            g.add((figure_uri, base.birthPlace, URIRef(value)))

        if "deathPlace" in res:
            value = res["deathPlace"]["value"]
            g.add((figure_uri, base.livedIn, URIRef(value)))

        if "religion" in res:
            value = res["religion"]["value"]
            g.add((figure_uri, base.religion, URIRef(value)))

        if "title" in res:
            value = res["title"]["value"]
            g.add((figure_uri, base.positionTitle, URIRef(value)))

        if "father" in res:
            value = res["father"]["value"]
            father_uri = URIRef(value)
            g.add((figure_uri, dbo.father, father_uri))

        if "mother" in res:
            value = res["mother"]["value"]
            mother_uri = URIRef(value)
            g.add((figure_uri, dbo.mother, mother_uri))

        if "residence" in res:
            value = res["residence"]["value"]
            g.add((figure_uri, base.livedIn, URIRef(value)))

        if "ethnicity" in res:
            value = res["ethnicity"]["value"]
            g.add((figure_uri, base.ethnicity, URIRef(value)))

    for predicate, obj in g.predicate_objects(subject=figure_uri):
        print(f"Historical Figure: {predicate} -> {obj}")
    print("---------------")

    for s, p, o in g.triples((figure_uri, base.birthPlace, None)):
        if isinstance(o, URIRef):
            ad_uri = add_ad_to_ontology(o, g)
            g.add((figure_uri, base.birthPlace, ad_uri))

    for s, p, o in g.triples((figure_uri, base.deathPlace, None)):
        if isinstance(o, URIRef):
            ad_uri = add_ad_to_ontology(o, g)
            g.add((figure_uri, base.deathPlace, ad_uri))

    sites = query_sites_from_figure(uri)["results"]["bindings"]
    for site in sites:
        site_dbp_uri = site["site"]["value"]
        chevie_site_uri = add_site_to_ontology(site_dbp_uri, g)
        g.add((chevie_site_uri, base.builtBy, figure_uri))

    return figure_uri


# SPARQL để lấy thông tin từ DBpedia
def query_historical_figure_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT DISTINCT ?label ?abstract ?birthDate ?deathDate ?birthPlace ?deathPlace 
                        ?religion ?title ?father ?mother ?residence ?ethnicity
        WHERE {{
            <{uri}> rdfs:label ?label .
            FILTER(LANG(?label) = 'en')

            OPTIONAL {{ <{uri}> dbp:abstract ?abstract . FILTER(LANG(?abstract) = 'en') }}
            OPTIONAL {{ <{uri}> dbp:birthDate ?birthDate . }}
            OPTIONAL {{ <{uri}> dbp:deathDate ?deathDate . }}
            OPTIONAL {{ <{uri}> dbp:birthPlace ?birthPlace . }}
            OPTIONAL {{ <{uri}> dbp:deathPlace ?deathPlace . }}
            OPTIONAL {{ <{uri}> dbp:religion ?religion . }}
            OPTIONAL {{ <{uri}> dbp:title ?title . }}

            OPTIONAL {{ <{uri}> dbp:father ?father . }}
            OPTIONAL {{ <{uri}> dbp:mother ?mother . }}
            OPTIONAL {{ <{uri}> dbo:residence ?residence . }}
            OPTIONAL {{ <{uri}> dbo:ethnicity ?ethnicity . }}
        }}
    """)

    print(f"Query Historical Figure: {sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def query_sites_from_figure(figure_uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT ?site ?label WHERE {{
          ?site dbo:builder <{figure_uri}> .
            ?site rdfs:label ?label .
            FILTER (LANG(?label) = 'en')
        }}
    """)

    print(f"Query Site of Historical Figure:\n{sparql.queryString}")
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
