from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt


class GraphDST:
    def __init__(self):
        G = Graph()

        n = Namespace("blind_mail/")
        n.user_exchange = URIRef("blind_mail/types/user_exchange")
        n.system_exchange = URIRef("blind_mail/types/system_exchange")
        n.intent = URIRef("blind_mail/types/intent")
        n.object = URIRef("blind_mail/types/object")
        n.person = URIRef("blind_mail/types/person")
        n.mail = URIRef("blind_mail/types/mail")
        n.followed_by = URIRef("blind_mail/rel/followed_by")
        n.express_intent = URIRef("blind_mail/rel/express_intent")
        n.refers_to = URIRef("blind_mail/rel/refers_to")
        n.has_text = URIRef("blind_mail/rel/has_text")
        start_node = URIRef("blind_mail/start")

        self.exchange_count = 1
        self.last_exchange = start_node
        self.namespace = n
        self.g = G

    def exchange(self, actor, text, intent=None, slots=None):

        new_node = URIRef(f"blind_mail/exchange_{self.exchange_count}")
        self.exchange_count += 1
        self.g.add((new_node, self.namespace.has_text, Literal(text)))
        self.g.add((self.last_exchange, self.namespace.followed_by, new_node))

        if actor == "System":
            self.g.add((new_node, RDF.type, self.namespace.system_exchange))

        elif actor == "User":
            self.g.add((new_node, RDF.type, self.namespace.user_exchange))
            if intent is not None:
                self.g.add((new_node, self.namespace.express_intent, Literal(intent)))
            if slots is not None:
                for slot in slots:
                    self.g.add((new_node, self.namespace.refers_to, Literal(slot[1])))
        self.last_exchange = new_node


    def print_graph(self):

        g = rdflib_to_networkx_multidigraph(self.g)

        # Plot Networkx instance of RDF Graph
        pos = nx.spring_layout(g, scale=2)
        edge_labels = nx.get_edge_attributes(g, 'r')
        nx.draw_networkx_edge_labels(g, pos, edge_labels=edge_labels)
        nx.draw(g, with_labels=True)

        plt.show()
