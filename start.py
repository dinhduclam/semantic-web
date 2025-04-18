from extract_HistoricalFigure import add_historical_figure_to_ontology
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, XSD, Namespace
from chevie_namespace import bind_namespaces, base

# Load file OWL gốc
g = Graph()
g.parse("CHeVIE.owl", format="xml")

# Khai báo namespace
bind_namespaces(g)

# Tạo cá thể Nguyễn Dynasty
def create_nguyen_dynasty(g: Graph, ns: Namespace):
    dynasty_uri = URIRef(ns + "Nguyen_Dynasty")
    g.add((dynasty_uri, RDF.type, ns.HistoricalDynasty))
    g.add((dynasty_uri, RDFS.label, Literal("Nguyễn dynasty")))
    g.add((dynasty_uri, ns.hasStartDate, Literal("1802", datatype=XSD.gYear)))
    g.add((dynasty_uri, ns.hasEndDate, Literal("1945", datatype=XSD.gYear)))
    return dynasty_uri


dynasty_uri = create_nguyen_dynasty(g, base)

historical_figure_uri = add_historical_figure_to_ontology("http://dbpedia.org/resource/Gia_Long", g)
g.add((historical_figure_uri, base.liveIn, dynasty_uri))

g.serialize("CHeVIE_Nguyen_HistoricalFigures.owl", format="xml")
print("✅ Đã ghi OWL mới với Nguyễn dynasty và các vua đúng chuẩn CHeVIE ontology.")
