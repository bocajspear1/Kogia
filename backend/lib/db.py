from arango import ArangoClient

class ArangoConnectionFactory():

    def __init__(self, host, port, username, password, db_name, ssl=False):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._db_name = db_name

    def new(self):
        return ArangoConnection(self._host, self._port, self._username, self._password, self._db_name, ssl=self._ssl)

class ArangoConnection():

    def __init__(self, host, port, username, password, db_name, ssl=False):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._db_name = db_name

        self._db = None
        self._conn = None
        self._cur_graph = None

    def connect(self):
        proto = "http"
        if self._ssl:
            proto = "https"

        self._conn = ArangoClient(hosts=f"{proto}://{self._host}:{self._port}")
        self._db = self._conn.db(self._db_name, username=self._username, password=self._password)


    @property
    def db(self):
        return self._db

    def _get_graph(self, graph_name):
        if not self._db.has_graph(graph_name):
            return self._db.create_graph(graph_name)
        else:
            return self._db.graph(graph_name)

    def _get_vertexes(self, graph_name, collection):
        graph = self._get_graph(graph_name)
        if not graph.has_vertex_collection(collection):
            return graph.create_vertex_collection(collection)
        else:
            return graph.vertex_collection(collection)

    def _get_edges(self, graph_name, collection, from_collection, to_collection):
        graph = self._get_graph(graph_name)
        if not graph.has_edge_definition(collection):
            return graph.create_edge_definition(
                edge_collection=collection,
                from_vertex_collections=[from_collection],
                to_vertex_collections=[to_collection]
            )
        else:
            return graph.edge_collection(collection)

    def _get_collection(self, collection):
        if not self._db.has_collection(collection):
            return self._db.create_collection(collection)
        else:
            return self._db.collection(collection)

    def _extract_collection_from_id(self, id):
        return id.split("/")[0]
            
    def get_vertex_by_match(self, graph_name, collection, field, value):
        col = self._get_vertexes(graph_name, collection)
        cursor = col.find({field: value}, skip=0, limit=1)
        return cursor.next()

    def get_vertex_by_id(self, graph_name, collection, id):
        col = self._get_vertexes(graph_name, collection)
        return col.get(id)

    def insert_vertex(self, graph_name, collection, document):
        col = self._get_vertexes(graph_name, collection)
        out = col.insert(document)
        if "_id" in out:
            return out['_id']
        else:
            return None

    def insert_edge(self, graph_name, collection, from_item, to_item, data=None, unique=True):
        from_col = self._extract_collection_from_id(from_item)
        to_col = self._extract_collection_from_id(to_item)
        col = self._get_edges(graph_name, collection, from_col, to_col)
        if unique:
            cursor = col.find({"_from": from_item, "_to": to_item})
            if cursor.count() != 0:
                print("duplicate!")
                return
        if data is not None:
            col.link(from_item, to_item, data=data)
        else:
            col.link(from_item, to_item)


    def insert(self, collection, document):
        col = self._get_collection(collection)
        out = col.insert(document)
        if "_id" in out:
            return out['_id']
        else:
            return None
        

    def update_replace(self, collection, id, data):
        pass 

    def delete(self, collection, query):
        pass 



    
