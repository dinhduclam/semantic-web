import json

with open("data.json", "r", encoding="utf-8") as f:
    data_list = json.load(f)

print("Danh sách vua triều Nguyễn:")
for king in data_list:
    print(f"- {king['name']} → {king['link']}")












import json

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, Namespace, URIRef, Literal, RDF, RDFS, OWL, XSD

# Load file OWL gốc
g = Graph()
g.parse("CHeVIE.owl", format="xml")

# Khai báo namespace
CHEVIE = Namespace("https://CHeVIE.vn/ontologies/")
g.bind("chevie", CHEVIE)

# g.add((person_uri, chevie.belongsToPeriod, dynasty_uri))

# Tạo cá thể Nguyễn Dynasty
def create_nguyen_dynasty(graph):
    dynasty_uri = URIRef(CHEVIE + "NguyenDynasty")
    graph.add((dynasty_uri, RDF.type, CHEVIE.Period))
    graph.add((dynasty_uri, RDFS.label, Literal("Nguyễn dynasty")))
    graph.add((dynasty_uri, CHEVIE.hasStartDate, Literal("1802", datatype=XSD.gYear)))
    graph.add((dynasty_uri, CHEVIE.hasEndDate, Literal("1945", datatype=XSD.gYear)))
    return dynasty_uri


dynasty_uri = create_nguyen_dynasty(g)


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

# Load danh sách vua từ file JSON
with open("data.json", "r", encoding="utf-8") as f:
    kings = json.load(f)

# Duyệt từng vua
for king in kings:
    uri = king["link"]
    name = king["name"].replace(" ", "_")
    result = query_historical_figure_from_dbpedia(uri)

    person_uri = URIRef(CHEVIE + name)
    g.add((person_uri, RDF.type, CHEVIE.HistoricalFigure))
    g.add((person_uri, OWL.sameAs, URIRef(uri)))
    g.add((person_uri, CHEVIE.belongsToPeriod, dynasty_uri))  # LINK dynasty đúng CHeVIE.owl

    for res in result["results"]["bindings"]:
        if "label" in res:
            value = res["label"]["value"]
            g.add((person_uri, RDFS.label, Literal(value)))

        if "abstract" in res:
            value = res["abstract"]["value"]
            g.add((person_uri, RDFS.comment, Literal(value)))

        if "birthDate" in res:
            value = res["birthDate"]["value"]
            g.add((person_uri, CHEVIE.birthDate, Literal(value, datatype=XSD.date)))

        if "deathDate" in res:
            value = res["deathDate"]["value"]
            g.add((person_uri, CHEVIE.deathDate, Literal(value, datatype=XSD.date)))

        if "birthPlace" in res:
            value = res["birthPlace"]["value"]
            g.add((person_uri, CHEVIE.birthPlace, URIRef(value)))

        if "deathPlace" in res:
            value = res["deathPlace"]["value"]
            g.add((person_uri, CHEVIE.livedIn, URIRef(value)))

        if "religion" in res:
            value = res["religion"]["value"]
            g.add((person_uri, CHEVIE.religion, URIRef(value)))

        if "title" in res:
            value = res["title"]["value"]
            g.add((person_uri, CHEVIE.hasPositionTitle, URIRef(value)))

        if "father" in res:
            value = res["father"]["value"]
            father_uri = URIRef(value)
            g.add((person_uri, CHEVIE.hasFather, father_uri))

        if "mother" in res:
            value = res["mother"]["value"]
            mother_uri = URIRef(value)
            g.add((person_uri, CHEVIE.hasMother, mother_uri))

        if "builderOf" in res:
            value = res["builderOf"]["value"]
            g.add((person_uri, CHEVIE.builderOfSite, URIRef(value)))

        if "residence" in res:
            value = res["residence"]["value"]
            g.add((person_uri, CHEVIE.livedIn, URIRef(value)))  # reuse livedIn

        if "ethnicity" in res:
            value = res["ethnicity"]["value"]
            g.add((person_uri, CHEVIE.ethnicity, URIRef(value)))

    for predicate, obj in g.predicate_objects(subject=person_uri):
        print(f"{predicate} -> {obj}")
    print("---------------")

    sites = query_site_from_figure(uri)["results"]["bindings"]
    for site in sites:
        site_dbp_uri = site["site"]["value"]
        label = site["label"]["value"]
        site_uri = URIRef(CHEVIE + label.replace(" ", "_"))
        g.add((site_uri, RDF.type, CHEVIE.Site))
        g.add((site_uri, OWL.sameAs, URIRef(site_dbp_uri)))

        for predicate, obj in g.predicate_objects(subject=site_uri):
            print(f"{predicate} -> {obj}")
        print("---------------")

# Ghi kết quả ra file OWL mới
g.serialize("CHeVIE_Nguyen_HistoricalFigures.owl", format="xml")
print("✅ Đã ghi OWL mới với Nguyễn dynasty và các vua đúng chuẩn CHeVIE ontology.")
