from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt


class GraphDST:
    def __init__(self):
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

        self.exchange_count = 1
        self.last_exchange = start_node
        self.namespace = n
        self.g = G

    def exchange(self,actor,text,intent=None,slots=None):

        new_node = URIRef(f"http://progettonlp.org/exchange_{self.exchange_count}")
        self.g.add((new_node,self.namespace.has_text,Literal(text)))
        self.g.add((self.last_exchange,self.namespace.followed_by,new_node))

        if (actor == "System"):
            self.g.add((new_node,RDF.type,self.namespace.system_exchange))

        elif (actor == "User"):
            self.g.add((new_node,RDF.type,self.namespace.user_exchange))
            self.g.add((new_node,self.namespace.express_intent,Literal(intent)))
            if (slots is not None):
                for slot in slots:
                    self.g.add((new_node,self.namespace.refers_to,Literal(slot[1])))


    def print_graph(self):

        g = rdflib_to_networkx_multidigraph(self.g)

        # Plot Networkx instance of RDF Graph
        pos = nx.spring_layout(g, scale=2)
        edge_labels = nx.get_edge_attributes(g, 'r')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
        nx.draw(g, with_labels=True)

        plt.show()



