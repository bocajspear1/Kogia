from arango import ArangoClient
from arango.exceptions import DocumentInsertError
from threading import RLock

class ArangoConnectionFactory():

    def __init__(self, host, port, username, password, db_name, ssl=False):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._db_name = db_name

    def new(self):
        new_conn = ArangoConnection(self._host, self._port, self._username, self._password, self._db_name, ssl=self._ssl)
        new_conn.connect()
        return new_conn

class ArangoConnection():

    def __init__(self, host, port, username, password, db_name, ssl=False):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._db_name = db_name
        self._db_lock = RLock()

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

    def lock(self):
        self._db_lock.acquire()

    def unlock(self):
        self._db_lock.release()

    def _get_graph(self, graph_name):
        if not self._db.has_graph(graph_name):
            return self._db.create_graph(graph_name)
        else:
            return self._db.graph(graph_name)

    def _get_vertexes(self, graph_name, collection):
        graph = self._get_graph(graph_name)
        if not graph.has_vertex_collection(collection):
            new_collection = graph.create_vertex_collection(collection)
            new_collection.add_hash_index(fields=['uuid'], unique=True)
            return new_collection
        else:
            return graph.vertex_collection(collection)

    def _get_edges(self, graph_name, collection, from_collection, to_collection, unique=True):
        graph = self._get_graph(graph_name)
        if not graph.has_edge_definition(collection):
            if to_collection is None:
                return None
            new_edge_col =  graph.create_edge_definition(
                edge_collection=collection,
                from_vertex_collections=[from_collection],
                to_vertex_collections=[to_collection]
            )
            new_edge_col.add_hash_index(fields=['_to', '_from'], unique=True)

            return new_edge_col
        else:
            return graph.edge_collection(collection)

    def _get_collection(self, collection):
        if not self._db.has_collection(collection):
            new_collection = self._db.create_collection(collection)
            new_collection.add_hash_index(fields=['uuid'], unique=True)
            return new_collection
        else:
            return self._db.collection(collection)

    def _extract_collection_from_id(self, id):
        return id.split("/")[0]
            
    def get_vertex_by_match(self, graph_name, collection, field, value):
        col = self._get_vertexes(graph_name, collection)
        cursor = col.find({field: value}, skip=0, limit=1)
        item = cursor.next()
        return item

    def get_vertex_by_id(self, graph_name, collection, id):
        col = self._get_vertexes(graph_name, collection)
        return col.get(id)

    def insert_vertex(self, graph_name, collection, document):
        col = self._get_vertexes(graph_name, collection)
        try:
            out = col.insert(document)
            if "_id" in out:
                return out['_id']
            else:
                return None
        except DocumentInsertError as e:
            if "unique constraint violated" in str(e) and 'uuid' in document:
                obj = self.get_vertex_by_match(graph_name, collection, 'uuid', document['uuid'])
                return obj['_id']
            else:
                raise e

    def update_vertex(self, graph_name, collection, id, document):
        col = self._get_vertexes(graph_name, collection)
        col.update_match({"_id": id}, document)


    def insert_edge(self, graph_name, collection, from_item, to_item, data=None, unique=True):
        from_col = self._extract_collection_from_id(from_item)
        to_col = self._extract_collection_from_id(to_item)
        col = self._get_edges(graph_name, collection, from_col, to_col, unique=unique)
       
        try:
            if data is not None:
                col.link(from_item, to_item, data=data)
            else:
                col.link(from_item, to_item)
        except DocumentInsertError:
            pass
        

    def get_connected_to(self, graph_name, collection, from_item):
        from_col = self._extract_collection_from_id(from_item)
        col = self._get_edges(graph_name, collection, from_col, None)
        if col is None:
            return []
        items = list(col.find({"_from": from_item}))
        return items
        


    def insert(self, collection, document):
        col = self._get_collection(collection)
        out = col.insert(document)
        if "_id" in out:
            return out['_id']
        else:
            return None
        

    def update(self, collection, id, document):
        col = self._get_collection(collection) 
        col.update_match({"_id": id}, document)

    def get_by_match(self, collection, field, value):
        col = self._get_collection(collection) 
        cursor = col.find({field: value}, skip=0, limit=1)
        item = cursor.next()
        return item

    def get_by_id(self, collection, id):
        col = self._get_collection(collection) 
        return col.get(id)

    def delete(self, collection, query):
        pass 


    def count(self, collection, filter=None, unique_by=None):
        if filter == None and unique_by == None:
            col = self._get_collection(collection)
            return col.count()
        elif filter is not None and unique_by is None:

            pass

            # for item in filter:
#              query = """
# FOR doc IN @collection COLLECT WITH COUNT INTO length
# AGGREGATE minAge = MIN(u.age), maxAge = MAX(u.age)
#             """

        else:

            if filter is None:
                query = """
FOR doc IN @collection COLLECT 
AGGREGATE uniqueCount = UNIQUE(doc.@unique_by)
RETURN { "uniqueCount": uniqueCount }
                """

                cursor = self._db.aql.execute(query, 
                    bind_vars={
                        'collection': collection,
                        'unique_by': unique_by,
                    })
                print(cursor.next())



    
