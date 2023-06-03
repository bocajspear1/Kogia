
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

    def get_list(self):
        pass

    def save_doc(self, db, data):
        if self._id is None:
            self._id = db.insert(self._collection, data)
        else:
            db.update(self._collection, self._id, data)

    def load_doc(self, db, field=None, value=None):
        doc = None
        if field is not None:
            doc = db.get_by_match(self._collection, field, value)
        else:
            if self._id is not None:
                doc = db.get_by_id(self._collection, self._id)
            else:
                return None
        
        if '_id' in doc:
            self._id = doc['_id']
        
        return doc


class VertexObject():

    GRAPH_NAME = 'kogia-graph'

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

    @property
    def is_modified(self):
        return self._modified

    def to_dict(self):
        raise NotImplementedError

    def save_doc(self, db, data):
        if self._id is None:
            self._id = db.insert_vertex(self.GRAPH_NAME, self._collection, data)
        else:
            db.update_vertex(self.GRAPH_NAME, self._collection, self._id, data)

    def load_doc(self, db, field=None, value=None):
        doc = None
        if field is not None:
            doc = db.get_vertex_by_match(self.GRAPH_NAME, self._collection, field, value)
        else:
            if self._id is not None:
                doc = db.get_vertex_by_id(self.GRAPH_NAME, self._collection, self._id)
            else:
                return None

        if doc is None:
            return None
        
        if '_id' in doc:
            self._id = doc['_id']
        
        return doc

    def get_list(self):
        pass

    def insert_edge(self, db, collection, to_item, data=None):
        db.insert_edge(self.GRAPH_NAME, collection, self._id, to_item, data=data)

    def get_connected_to(self, db, end_collection, filter_edges=None, max=2, direction='both', limit=0, skip=0):
        return db.get_connected_to(self.GRAPH_NAME, self._id, end_collection, filter_edges=filter_edges, max=max, direction=direction, limit=limit, skip=skip)
    
    def count_connected_to(self, db, end_collection, filter_edges=None, max=2, direction='both'):
        return db.get_connected_to(self.GRAPH_NAME, self._id, end_collection, filter_edges=filter_edges, max=max, direction=direction, length_only=True)
    
    def get_in_path(self, db, end_item, path_pos, edges, max=2, return_fields=None):
        return db.get_in_path(self.GRAPH_NAME, self._id, end_item, path_pos, edges, max=max, return_fields=return_fields)
