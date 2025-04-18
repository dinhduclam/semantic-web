sample_data = [
    {
        "type": "HistoricalFigure",
        "name": "TranHungDao",
        "birth_day": "10",
        "birth_month": "06",
        "birth_year": "1228",
        "death_day": "20",
        "death_month": "08",
        "death_year": "1300",
        "dynasty": "Tran Dynasty",
        "description": "Trần Hưng Đạo là một danh tướng kiệt xuất thời nhà Trần, người chỉ huy quân Đại Việt đánh thắng quân Nguyên Mông.",
        "reference": "https://vi.wikipedia.org/wiki/Trần_Hưng_Đạo"
    }
]

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from rdflib.namespace import XSD
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON
import re

def query_dbpedia_figures(limit=10):
    sparql = SPARQLWrapper("https://dbpedia.org/sparql")

    sparql.setQuery(f"""
    SELECT DISTINCT ?person ?label ?abstract ?birthDate ?deathDate WHERE {{
      ?person rdf:type dbo:Person .
      ?person dbo:birthPlace dbr:Vietnam .
      ?person rdfs:label ?label .
      OPTIONAL {{ ?person dbo:abstract ?abstract . FILTER(lang(?abstract) = 'vi') }}
      OPTIONAL {{ ?person dbo:birthDate ?birthDate . }}
      OPTIONAL {{ ?person dbo:deathDate ?deathDate . }}
      FILTER(lang(?label) = 'en')
    }} LIMIT {limit}
    """)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results["results"]["bindings"]


# Helper: ISO 8601 date string → day, month, year
def parse_iso_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return str(dt.day), str(dt.month), str(dt.year)
    except:
        return None, None, None


# Chuyển sang định dạng dùng cho generate_rdf_from_chevie
def dbpedia_to_chevie_format(bindings):
    cheviedata = []
    for result in bindings:
        name_label = result["label"]["value"]
        name_clean = re.sub(r"[^\w]", "", name_label.replace(" ", "_"))
        item = {
            "type": "HistoricalFigure",
            "name": name_clean,
            "description": result.get("abstract", {}).get("value", ""),
            "reference": result["person"]["value"],
        }

        if "birthDate" in result:
            day, month, year = parse_iso_date(result["birthDate"]["value"])
            if day: item.update({"birth_day": day, "birth_month": month, "birth_year": year})

        if "deathDate" in result:
            day, month, year = parse_iso_date(result["deathDate"]["value"])
            if day: item.update({"death_day": day, "death_month": month, "death_year": year})

        cheviedata.append(item)

    return cheviedata

def generate_rdf_from_chevie(data_list, ontology_path="CHeVIE.owl", output_path="chevie_output.owl"):
    g = Graph()
    g.parse(ontology_path)

    CHeVIE = Namespace("https://CHeVIE.vn/ontologies/")
    TIME = Namespace("http://www.w3.org/2006/time#")
    OWL = Namespace("http://www.w3.org/2002/07/owl#")
    PROV = Namespace("http://www.w3.org/ns/prov#")

    g.bind("chevie", CHeVIE)
    g.bind("time", TIME)
    g.bind("owl", OWL)
    g.bind("prov", PROV)

    def add_date_statement(subject_uri, property_uri, name_prefix, date_label, day, month, year, calendar="LunarCalendar", reference_url=None):
        base = f"https://CHeVIE.vn/ontologies/{name_prefix}{date_label}"
        date_uri = URIRef(base)
        stmt_uri = URIRef(f"{base}Statement")
        desc_uri = URIRef(f"{base}TimeDescription")
        ref_uri = URIRef(f"{base}Reference")

        g.add((subject_uri, property_uri, stmt_uri))

        g.add((date_uri, RDF.type, OWL.NamedIndividual))
        g.add((date_uri, RDF.type, TIME.Instant))
        g.add((date_uri, TIME.hasTRS, URIRef(f"https://CHeVIE.vn/ontologies/{calendar}")))
        g.add((date_uri, TIME.inDateTime, desc_uri))
        g.add((date_uri, TIME.day, Literal(f"{int(day):02d}", datatype=XSD.gDay)))
        g.add((date_uri, TIME.month, Literal(f"{int(month):02d}", datatype=XSD.gMonth)))
        g.add((date_uri, TIME.year, Literal(year, datatype=XSD.gYear)))

        g.add((desc_uri, RDF.type, OWL.NamedIndividual))
        g.add((desc_uri, RDF.type, TIME.DateTimeDescription))

        g.add((ref_uri, RDF.type, OWL.NamedIndividual))
        g.add((ref_uri, RDF.type, CHeVIE.Reference))
        if reference_url:
            g.add((ref_uri, CHeVIE.referenceURL, Literal(reference_url)))
        g.add((ref_uri, CHeVIE.retrieved, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

        g.add((stmt_uri, RDF.type, OWL.NamedIndividual))
        g.add((stmt_uri, RDF.type, CHeVIE.Statement))
        g.add((stmt_uri, CHeVIE[f"_{property_uri.split('#')[-1]}"], date_uri))
        g.add((stmt_uri, PROV.wasDerivedFrom, ref_uri))

    for item in data_list:
        entity_type = item.get("type")
        name = item.get("name", "").replace(" ", "_")
        uri = URIRef(f"https://CHeVIE.vn/ontologies/{name}")

        g.add((uri, RDF.type, OWL.NamedIndividual))
        g.add((uri, RDF.type, CHeVIE[entity_type]))
        g.add((uri, RDFS.label, Literal(item.get("name", ""), lang="vi")))

        if entity_type == "HistoricalFigure":
            if all(k in item for k in ("birth_day", "birth_month", "birth_year")):
                add_date_statement(uri, CHeVIE.birthDate, name, "BirthDate", item["birth_day"], item["birth_month"], item["birth_year"], reference_url=item.get("reference"))
            if all(k in item for k in ("death_day", "death_month", "death_year")):
                add_date_statement(uri, CHeVIE.deathDate, name, "DeathDate", item["death_day"], item["death_month"], item["death_year"], reference_url=item.get("reference"))
            if "dynasty" in item:
                g.add((uri, CHeVIE.belongToDynasty, Literal(item["dynasty"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        elif entity_type == "HistoricalDynasty":
            if all(k in item for k in ("start_year", "start_month", "start_day")):
                add_date_statement(uri, CHeVIE.startYear, name, "StartYear", item["start_day"], item["start_month"], item["start_year"], reference_url=item.get("reference"))
            if all(k in item for k in ("end_year", "end_month", "end_day")):
                add_date_statement(uri, CHeVIE.endYear, name, "EndYear", item["end_day"], item["end_month"], item["end_year"], reference_url=item.get("reference"))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        elif entity_type == "HistoricalEvent":
            if all(k in item for k in ("event_day", "event_month", "event_year")):
                add_date_statement(uri, CHeVIE.eventDate, name, "EventDate", item["event_day"], item["event_month"], item["event_year"], reference_url=item.get("reference"))
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        elif entity_type == "HistoricalSite":
            if all(k in item for k in ("constructed_day", "constructed_month", "constructed_year")):
                add_date_statement(uri, CHeVIE.constructedYear, name, "ConstructedYear", item["constructed_day"], item["constructed_month"], item["constructed_year"], reference_url=item.get("reference"))
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        elif entity_type == "Festival":
            if all(k in item for k in ("festival_day", "festival_month", "festival_year")):
                add_date_statement(uri, CHeVIE.dateHeld, name, "FestivalDate", item["festival_day"], item["festival_month"], item["festival_year"], reference_url=item.get("reference"))
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

    g.serialize(destination=output_path, format="xml")
    print(f"RDF generated at: {output_path}")


# Bước 1: Truy vấn DBpedia
dbpedia_data = query_dbpedia_figures(limit=5)

# Bước 2: Chuyển sang định dạng RDF CHeVIE
chevie_data = dbpedia_to_chevie_format(dbpedia_data)

# Gọi hàm với đường dẫn thực tế tới file ontology CHeVIE.owl trên máy
generate_rdf_from_chevie(sample_data, ontology_path="CHeVIE.owl", output_path="chevie_output.owl")