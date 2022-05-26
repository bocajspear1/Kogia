
class CollectionObject():

    def __init__(self, collection, id=None):
        self._modified = False 
        # self._db = db
        self._collection = collection
        self._id = id

    @property
    def id (self):
        return self._id

    def set_modified(self):
        self._modified = True 

    def reset_modified(self):
        self._modified = False

    def to_dict(self):
        raise NotImplementedError

    def from_dict(self):
        raise NotImplementedError

    def save_doc(self, db, data):
        if self._id is None:
            self._id = db.insert_vertex(self._graph_name, self._collection, data)
        else:
            db.update_vertex(self._graph_name, self._collection, self._id, data)

    def load_doc(self, db, field=None, value=None):
        doc = None
        if field is not None:
            doc = db.get_vertex_by_match(self._graph_name, self._collection, field, value)
        else:
            if self._id is not None:
                doc = db.get_vertex_by_id(self._graph_name, self._collection, self._id)
            else:
                return None
        
        if '_id' in doc:
            self._id = doc['_id']
        
        return doc


class VertexObject():

    def __init__(self, collection, id=None):
        self._graph_name = 'kogia-graph'
        self._modified = False 
        # self._db = db
        self._collection = collection
        self._id = id

    @property
    def id (self):
        return self._id

    def set_modified(self):
        self._modified = True 

    def reset_modified(self):
        self._modified = False

    def to_dict(self):
        raise NotImplementedError

    def save_doc(self, db, data):
        if self._id is None:
            self._id = db.insert_vertex(self._graph_name, self._collection, data)
        else:
            db.update_vertex(self._graph_name, self._collection, self._id, data)

    def load_doc(self, db, field=None, value=None):
        doc = None
        if field is not None:
            doc = db.get_vertex_by_match(self._graph_name, self._collection, field, value)
        else:
            if self._id is not None:
                doc = db.get_vertex_by_id(self._graph_name, self._collection, self._id)
            else:
                return None
        
        if '_id' in doc:
            self._id = doc['_id']
        
        return doc

    def insert_edge(self, db, collection, to_item, data=None):
        db.insert_edge(self._graph_name, collection, self._id, to_item, data=data)

    def get_connected_to(self, db, edge_collection):
        return db.get_connected_to(self._graph_name, edge_collection, self._id)
