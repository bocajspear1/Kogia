import hashlib
import os
import logging

logger = logging.getLogger(__name__)

from .db import ArangoConnection, DBNotUniqueError


class FilestoreObject():
    """Object for a single file in the filestore.
    """
    
    
    def __init__(self, filestore, file_id, filename):
        self._file_id = file_id
        self._filestore = filestore
        self._name = filename
        self._modified = False
        self._hash = None

        self._handle = None

    def update_hash(self):
        sha256 = hashlib.sha256()

        handle = self.open_file()
        while True:
            data = handle.read(65536)
            if not data:
                break
            sha256.update(data)
        self.close_file()

        self._hash = sha256.hexdigest()

    def create_file(self):
        self._handle = self._filestore.create_file(self._file_id)
        return self._handle

    def open_file(self):
        self._handle = self._filestore.open_file(self._file_id)
        return self._handle
    
    def copy_file_from(self, src_path):
        self._filestore.copy_file_from(src_path, self._file_id)
    
    def close_file(self):
        if self._handle is not None:
            return self._filestore.close_file(self._file_id, self._handle)
        
    @property
    def extension(self):
        if self._name is not None:
            _, ext = os.path.splitext(self._name)
            return ext
        else:
            return None
        
    @property
    def file_id(self):
        return self._file_id

    @property
    def name(self):
        return self._name
    
    @property
    def hash(self):
        return self._hash


class CollectionObject():
    """Object stored as a regular document in the database.
    """

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

    def save_doc(self, db : ArangoConnection, data):
        if self._id is None:
            self._id = db.insert(self._collection, data)
        else:
            db.update(self._collection, self._id, data)

    def load_doc(self, db : ArangoConnection, field=None, value=None):
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

        if doc is None:
            return None
        
        return doc


class VertexObject():
    """Object to be stored as a vertex in the graph database.
    """
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

    def save_doc(self, db : ArangoConnection, data):
        if self._id is None:
            self._id = db.insert_vertex(self.GRAPH_NAME, self._collection, data)
        else:
            db.update_vertex(self.GRAPH_NAME, self._collection, self._id, data)

    def load_doc(self, db : ArangoConnection, field=None, value=None):
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

    def insert_edge(self, db : ArangoConnection, collection, to_item, data=None):
        db.insert_edge(self.GRAPH_NAME, collection, self._id, to_item, data=data)

    def insert_edge_bulk(self, db : ArangoConnection, collection, to_collection, to_items):
        db.insert_edge_bulk(self.GRAPH_NAME, collection, self._id, to_collection, to_items)

    def get_connected_to(self, db : ArangoConnection, end_item, filter_edges=None, filter_vertices=None, 
                         max=2, direction='both', limit=0, skip=0, sort_by=None, add_edges=False, return_path=False):
        # We can't have anything connected to if we don't know our ID. We're probably a new object with nothing in the DB yet.
        if self._id is None:
            return []
        return db.get_connected_to(self.GRAPH_NAME, self._id, end_item, filter_edges=filter_edges, filter_vertices=filter_vertices, max=max, 
                                   direction=direction, limit=limit, skip=skip, sort_by=sort_by, add_edges=add_edges, return_path=return_path)
    
    def count_connected_to(self, db : ArangoConnection, end_item, filter_edges=None, filter_vertices=None, max=2, direction='both'):
        results = db.get_connected_to(self.GRAPH_NAME, self._id, end_item, filter_edges=filter_edges, 
                                   filter_vertices=filter_vertices, max=max, direction=direction, length_only=True)
        if len(results) > 0:
            return results[0]
        else:
            return 0

class Metadata(VertexObject):
    """Object that contains Key-Value data.
    """

    COLLECTION = 'metadata'

    @classmethod
    def get_search_tuple(cls, search):
        return ('OR', [
            ('ILIKE', "key", f"%{search}%"),
            ('ILIKE', "value", f"%{search}%"),
        ])

    @classmethod
    def list_dict(cls, db : ArangoConnection, skip=0, limit=20, search=None):
        filter_tuple = None
        if search is not None:
            filter_tuple = cls.get_search_tuple()

        results = db.find_vertexes(cls.GRAPH_NAME, cls.COLLECTION, filter_tuple=filter_tuple, limit=limit, skip=skip)
        return results

    @classmethod
    def bulk_insert(cls, db, insert_items):
        insert_metadata = []
        for metadata in insert_items:
            if metadata.is_modified:
                insert_metadata.append(metadata.to_dict())

        return db.insert_bulk(cls.COLLECTION, insert_metadata)
        
    def __init__(self, uuid=None, id=None):
        super().__init__(self.COLLECTION, id)
        self._key = "" 
        self._value = ""
        self._uuid = uuid

    @property
    def key(self):
        return self._key 

    @key.setter
    def key(self, new_key):
        self.set_modified()
        self._key = new_key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self.set_modified()
        self._value = new_value

    @property
    def uuid(self):
        return self._uuid
    
    def _gen_uuid(self):
        my_uuid  = hashlib.sha256((self._key + ":" + self._value).encode())
        self._uuid = my_uuid.hexdigest()
        self.set_modified()

    def to_dict(self):
        if self._uuid is None:
            self._gen_uuid()
        return {
            "key": self._key,
            "value": self._value,
            "uuid": self._uuid,
            "_key": self._uuid
        }

    def from_dict(self, data_obj):
        self._uuid = data_obj.get('_key', '')
        self._key = data_obj.get('key', '')
        self._value = data_obj.get('value', '')

    def save(self, db):
        try:
            self.save_doc(db, self.to_dict())
        except DBNotUniqueError:
            pass

    def load(self, db):
        document = {}
        if self.id is None:
            if self._uuid == "":
                self._gen_uuid()
            document = self.load_doc(db, field='_key', value=self.uuid)
        else:
            document = self.load_doc(db)

        self.from_dict(document)

    def __str__(self):
        return "{} - {}:{}".format(self._uuid, self._key, self._value)


class VertexObjectWithMetadata(VertexObject):
    """VertexObject but with built-in functions for storing Metadata

    NOTE: Functions that inherit this will need to call self.save_metadata(db)
          in their save functions, otherwise Metadata will not be saved!
    """
    
    def __init__(self, collection, metadata_edge_col, id):
        super().__init__(collection, id)
        self._metadata = []
        self._metadata_total = 0 # Stores total metadata for current filter and mtype set
        self._edge_col = metadata_edge_col

    @property
    def metadata(self):
        return self._metadata

    @property
    def metadata_total(self):
        return self._metadata_total

    # We load metadata seperately so we don't grab everything every time.
    # Saves lots of time
    def load_metadata(self, db, as_dict=False, mtype=None, skip=0, limit=None, filter=None):
        self._metadata = []
        items = []
        logger.debug("Loading metadata")

        if limit is not None:
            filter_list = ('key', mtype)
            if filter is not None:
                filter_list = ('AND', [filter_list, ('ILIKE', 'value', "%" + filter + "%")])
            
            items = self.get_connected_to(db, 'metadata', filter_edges=[self._edge_col], filter_vertices=filter_list, skip=skip, limit=limit)
            logger.debug("Counting metadata")
            self._metadata_total = self.count_connected_to(db, 'metadata', filter_edges=[self._edge_col], filter_vertices=filter_list)
        elif filter is not None:
            filter_list = ('ILIKE', 'value', "%" + filter + "%")
            items = self.get_connected_to(db, 'metadata', filter_edges=[self._edge_col], filter_vertices=filter_list)
            self._metadata_total = self.count_connected_to(db, 'metadata', filter_edges=[self._edge_col], filter_vertices=filter_list)
        else:
            items = self.get_connected_to(db, 'metadata', filter_edges=[self._edge_col])
            self._metadata_total = self.count_connected_to(db, 'metadata', filter_edges=[self._edge_col])
        logger.debug("Got metadata")
        if not as_dict:
            for item in items:
                load_data = Metadata(id=item['_id'])
                load_data.from_dict(item)
                self._metadata.append(load_data)
        else:
            self._metadata = items
    
    def save_metadata(self, db):
        # Check if metadata has been loaded our added
        # None indicates not loaded and no additions
        if len(self._metadata) > 0:
            new_items = Metadata.bulk_insert(db, self._metadata)
            id_list = []
            for item in new_items:
                if item is not None:
                    id_list.append(item['_id'])
            self.insert_edge_bulk(db, self._edge_col, Metadata.COLLECTION, id_list)
    
    def add_metadata(self, key, value):
        # if self._metadata is None:
        #     raise ValueError("Must call load_metadata before adding new metadata")

        new_data = Metadata()
        new_data.key = key
        new_data.value = value
        self._metadata.append(new_data)
        return new_data

    def add_metadata_unique(self, key, value):
        # if self._metadata is None:
        #     raise ValueError("Must call load_metadata before adding new metadata")

        found = False
        for data in self._metadata:
            if data.key == key:
                found = True
                data.value = value 
                return data

        if not found:
            new_data = Metadata()
            new_data.value = value
            new_data.key = key
            self._metadata.append(new_data)
            return new_data
        
    def get_metadata_types(self):
        return_map = {}

        for item in self._metadata:
            if item.key not in return_map:
                return_map[item.key] = 0
            return_map[item.key] += 1
        
        return return_map

    def get_metadata_by_type(self, metadata_type, data_filter=None):
        return_list = []

        for item in self._metadata:
            if item.key == metadata_type:
                if data_filter is not None:
                    if data_filter.lower() not in item.value.lower():
                        continue

                return_list.append(item.value)
        
        return return_list