from extract_HistoricalFigure import add_historical_figure_to_ontology
from extract_Site import add_site_to_ontology
from extract_HistoricalDynasty import add_dynastic_to_ontology
from extract_Festival import add_festival_to_ontology
from extract_HistoricEvent import add_event_to_ontology
from extract_AdministrativeDivision import add_ad_to_ontology
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph, URIRef, Literal, RDF, RDFS, OWL, XSD, Namespace
from chevie_namespace import bind_namespaces, base

# Load file OWL gốc
g = Graph()
g.parse("CHeVIE.owl", format="xml")

# Khai báo namespace
bind_namespaces(g)

add_dynastic_to_ontology("http://dbpedia.org/resource/Nguyễn_dynasty", g)

# add_historical_figure_to_ontology("http://dbpedia.org/resource/Gia_Long", g)
# add_site_to_ontology("http://dbpedia.org/resource/Citadel_of_Saigon", g)
# add_dynastic_to_ontology("http://dbpedia.org/resource/Nguyễn_dynasty", g)
# add_festival_to_ontology("http://dbpedia.org/resource/Perfume_Temple", g)
# add_event_to_ontology("http://dbpedia.org/resource/Vietnam_War", g)
# add_ad_to_ontology("http://dbpedia.org/resource/Ho_Chi_Minh_City", g)
# g.add((historical_figure_uri, base.liveIn, dynasty_uri))

# g.serialize("CHeVIE_Nguyen_HistoricalFigures.owl", format="xml")
# print("✅ Đã ghi OWL mới với Nguyễn dynasty và các vua đúng chuẩn CHeVIE ontology.")
