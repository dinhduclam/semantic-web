from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal, XSD
from chevie_namespace import rdf, rdfs, owl, base, dbo


def add_historical_figure_to_ontology(uri: str, g: Graph):
    results = query_historical_figure_from_dbpedia(uri)["results"]["bindings"]

    person_uri = URIRef(base + results[0]["label"]["value"].replace(" ", "_"))
    g.add((person_uri, rdf.type, base.HistoricalFigure))
    g.add((person_uri, owl.sameAs, URIRef(uri)))

    for res in results:
        if "label" in res:
            value = res["label"]["value"]
            g.add((person_uri, rdfs.label, Literal(value)))

        if "abstract" in res:
            value = res["abstract"]["value"]
            g.add((person_uri, rdfs.comment, Literal(value)))

        if "birthDate" in res:
            value = res["birthDate"]["value"]
            g.add((person_uri, base.birthDate, Literal(value, datatype=XSD.date)))

        if "deathDate" in res:
            value = res["deathDate"]["value"]
            g.add((person_uri, base.deathDate, Literal(value, datatype=XSD.date)))

        if "birthPlace" in res:
            value = res["birthPlace"]["value"]
            g.add((person_uri, base.birthPlace, URIRef(value)))

        if "deathPlace" in res:
            value = res["deathPlace"]["value"]
            g.add((person_uri, base.livedIn, URIRef(value)))

        if "religion" in res:
            value = res["religion"]["value"]
            g.add((person_uri, base.religion, URIRef(value)))

        if "title" in res:
            value = res["title"]["value"]
            g.add((person_uri, base.hasPositionTitle, URIRef(value)))

        if "father" in res:
            value = res["father"]["value"]
            father_uri = URIRef(value)
            g.add((person_uri, dbo.father, father_uri))

        if "mother" in res:
            value = res["mother"]["value"]
            mother_uri = URIRef(value)
            g.add((person_uri, dbo.mother, mother_uri))

        if "builderOf" in res:
            value = res["builderOf"]["value"]
            g.add((person_uri, base.builderOfSite, URIRef(value)))

        if "residence" in res:
            value = res["residence"]["value"]
            g.add((person_uri, base.livedIn, URIRef(value)))  # reuse livedIn

        if "ethnicity" in res:
            value = res["ethnicity"]["value"]
            g.add((person_uri, base.ethnicity, URIRef(value)))

    for predicate, obj in g.predicate_objects(subject=person_uri):
        print(f"{predicate} -> {obj}")
    print("---------------")

    sites = query_site_from_figure(uri)["results"]["bindings"]
    for site in sites:
        site_dbp_uri = site["site"]["value"]
        label = site["label"]["value"]
        site_uri = URIRef(base + label.replace(" ", "_"))
        g.add((site_uri, rdf.type, base.Site))
        g.add((site_uri, owl.sameAs, URIRef(site_dbp_uri)))

        for predicate, obj in g.predicate_objects(subject=site_uri):
            print(f"{predicate} -> {obj}")
        print("---------------")

    return person_uri


# SPARQL để lấy thông tin từ DBpedia
def query_historical_figure_from_dbpedia(uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT DISTINCT ?label ?abstract ?birthDate ?deathDate ?birthPlace ?deathPlace 
                        ?religion ?title ?father ?mother ?builderOf ?residence ?ethnicity
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
            OPTIONAL {{ <{uri}> dbo:builder ?builderOf . }}
            OPTIONAL {{ <{uri}> dbo:residence ?residence . }}
            OPTIONAL {{ <{uri}> dbo:ethnicity ?ethnicity . }}
        }}
    """)

    print(sparql.queryString)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def query_site_from_figure(figure_uri):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")
    sparql.setQuery(f"""
        SELECT ?site ?label WHERE {{
          ?site dbo:builder <{figure_uri}> .
            ?site rdfs:label ?label .
            FILTER (LANG(?label) = 'en')
        }}
    """)

    print(sparql.queryString)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()
