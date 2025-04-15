from rdflib import Graph, URIRef, Literal, Namespace, RDF
from rdflib.namespace import XSD, RDFS

data = [
    {
        "type": "HistoricalFigure",
        "name": "Nguyen Hue",
        "birth_date": "1753-01-01",
        "death_date": "1792-01-01",
        "dynasty": "Tay Son",
        "description": "Vietnamese national hero, Emperor Quang Trung.",
        "religion": "FolkReligion",
        "academic_degree": "Tien si",
        "position": "Emperor"
    },
    {
        "type": "Festival",
        "name": "Hung Kings Festival",
        "date": "10th day of 3rd lunar month",
        "location": "Phu Tho",
        "description": "Traditional festival commemorating the Hung Kings.",
        "festival_type": "TraditionalFestival",
        "commemorates": "Hung Kings"
    }
]

from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL
from rdflib.namespace import XSD

def generate_rdf_from_chevie(data_list, ontology_path="CHeVIE.owl", output_path="chevie_output.rdf"):
    g = Graph()
    g.parse(ontology_path)

    # ✅ Cập nhật namespace CHÍNH XÁC
    CHeVIE = Namespace("https://CHeVIE.vn/ontologies/")
    g.bind("chevie", CHeVIE)

    for item in data_list:
        entity_type = item.get("type")
        name = item.get("name", "").replace(" ", "_")
        uri = URIRef(f"https://CHeVIE.vn/resource/{name}")
        g.add((uri, RDF.type, CHeVIE[entity_type]))
        g.add((uri, RDFS.label, Literal(item.get("name", ""), lang="vi")))

        # Historical Figure
        if entity_type == "HistoricalFigure":
            if "birth_date" in item:
                g.add((uri, CHeVIE.birthDate, Literal(item["birth_date"], datatype=XSD.date)))
            if "death_date" in item:
                g.add((uri, CHeVIE.deathDate, Literal(item["death_date"], datatype=XSD.date)))
            if "dynasty" in item:
                g.add((uri, CHeVIE.belongToDynasty, Literal(item["dynasty"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))
            if "religion" in item:
                g.add((uri, CHeVIE.religion, Literal(item["religion"])))
            if "academic_degree" in item:
                g.add((uri, CHeVIE.hasAcademicDegree, Literal(item["academic_degree"])))
            if "position" in item:
                g.add((uri, CHeVIE.hasPositionTitle, Literal(item["position"])))

        # Festival
        elif entity_type == "Festival":
            if "date" in item:
                g.add((uri, CHeVIE.dateHeld, Literal(item["date"])))
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))
            if "festival_type" in item:
                g.add((uri, CHeVIE.festivalType, Literal(item["festival_type"])))
            if "commemorates" in item:
                g.add((uri, CHeVIE.commemorates, Literal(item["commemorates"])))

        # Historical Dynasty
        elif entity_type == "HistoricalDynasty":
            if "start_year" in item:
                g.add((uri, CHeVIE.startYear, Literal(item["start_year"], datatype=XSD.gYear)))
            if "end_year" in item:
                g.add((uri, CHeVIE.endYear, Literal(item["end_year"], datatype=XSD.gYear)))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        # Historical Event
        elif entity_type == "HistoricalEvent":
            if "date" in item:
                g.add((uri, CHeVIE.eventDate, Literal(item["date"])))
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))
            if "event_type" in item:
                g.add((uri, CHeVIE.eventType, Literal(item["event_type"])))

        # Historical Site
        elif entity_type == "HistoricalSite":
            if "location" in item:
                g.add((uri, CHeVIE.location, Literal(item["location"])))
            if "site_type" in item:
                g.add((uri, CHeVIE.siteType, Literal(item["site_type"])))
            if "constructed_year" in item:
                g.add((uri, CHeVIE.constructedYear, Literal(item["constructed_year"], datatype=XSD.gYear)))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

        # Administrative Division
        elif entity_type == "AdministrativeDivision":
            if "level" in item:
                g.add((uri, CHeVIE.adminLevel, Literal(item["level"])))
            if "province" in item:
                g.add((uri, CHeVIE.belongsToProvince, Literal(item["province"])))
            if "description" in item:
                g.add((uri, CHeVIE.description, Literal(item["description"])))

    g.serialize(destination=output_path, format="xml")
    print(f"✅ RDF file generated at: {output_path}")


# Gọi hàm với đường dẫn thực tế tới file ontology CHeVIE.owl trên máy bạn
generate_rdf_from_chevie(data, ontology_path="CHeVIE.owl", output_path="chevie_output.rdf")