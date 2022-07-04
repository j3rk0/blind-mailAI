from rdflib import Graph, Namespace, URIRef, RDF, Literal


G = Graph()

n = Namespace("http://progettonlp.org/")
n.user_exchange = URIRef("http://progettonlp.org/types/user_exchange")
n.system_exchange = URIRef("http://progettonlp.org/types/system_exchange")
n.intent = URIRef("http://progettonlp.org/types/intent")
n.object = URIRef("http://progettonlp.org/types/object")
n.person = URIRef("http://progettonlp.org/types/person")
n.mail = URIRef("http://progettonlp.org/types/mail")
n.followed_by = URIRef("http://progettonlp.org/types/followed_by")
n.express_intent = URIRef("http://progettonlp.org/types/express_intent")
n.refers_to = URIRef("http://progettonlp.org/types/refers_to")
n.has_text = URIRef("http://progettonlp.org/types/has_text")
start_node = URIRef("http://progettonlp.org/start")

G.add((start_node,RDF.type,n.system_exchange))
new_node = URIRef("http://progettonlp.org/node1")
G.add((new_node,RDF.type,n.user_exchange))
G.add((new_node,n.has_text,Literal("voglio creare una nuova mail")))
G.add((new_node,n.express_intent,Literal("send_mail")))
G.add((start_node,n.followed_by,new_node))

#%%

from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

url = 'https://www.w3.org/TeamSubmission/turtle/tests/test-30.ttl'


g = rdflib_to_networkx_multidigraph(G)

# Plot Networkx instance of RDF Graph
pos = nx.spring_layout(g, scale=2)
edge_labels = nx.get_edge_attributes(g, 'r')
nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
nx.draw(g, with_labels=True)

plt.show()