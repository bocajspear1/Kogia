from arango import ArangoClient
from arango.exceptions import DocumentInsertError
from threading import RLock

NO_INDEX = ('logs',)

class DBNotUniqueError(Exception):
    pass

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

    def _get_collection(self, collection, create_index=True):
        if not self._db.has_collection(collection):
            new_collection = self._db.create_collection(collection)
            if create_index and collection not in NO_INDEX:
                new_collection.add_hash_index(fields=['uuid'], unique=True)
            return new_collection
        else:
            return self._db.collection(collection)

    def _extract_collection_from_id(self, id):
        return id.split("/")[0]
            
    def get_vertex_by_match(self, graph_name, collection, field, value):
        col = self._get_vertexes(graph_name, collection)
        cursor = col.find({field: value}, skip=0, limit=1)
        if cursor.count() == 0:
            return None
        item = cursor.next()
        return item

    def get_vertex_by_id(self, graph_name, collection, id):
        col = self._get_vertexes(graph_name, collection)
        return col.get(id)

    # {"test": ()}
    def get_vertex_list_joined(self, main_collection, join_map, sort_by=None, filter_map=None, limit=None, skip=0):
        aql_query = f"FOR doc IN {main_collection}"
        bind_vars = {}

        join_list = list(join_map.keys())

        for i,join_col in enumerate(join_list):
            aql_query += " FOR " + join_col + "_item IN " + join_col


        aql_query += " FILTER "
        first = True
        for i,join_col in enumerate(join_list):
            if first:
                first = False
            else:
                 aql_query += " AND "
            join_info = join_map[join_col]
            join_field = join_info[0]
            compare = "=="
            orig_field = ""
            if len(join_info) == 3:
                compare = join_info[1]
                orig_field = join_info[2]
            else:
                orig_field = join_info[1]
            

            # bind_vars["join_col_" + str(i) + "_field"] = join_map[join_col][0]
            aql_query += " " + join_col + "_item." + join_field + " " + compare + " doc." + orig_field

        
        if filter_map is not None:
            aql_query += " AND ("
            filter_keys = list(filter_map.keys())
            first = True
            for filter_key in filter_keys:
                if first:
                    first = False
                else:
                    aql_query += " AND "

                filter_line = filter_map[filter_key]
                filter_field = filter_line[0]
                compare = "=="
                comp_value = ""
                if len(filter_line) == 3:
                    compare = filter_line[1]
                    comp_value = filter_line[2]
                else:
                    comp_value = filter_line[1]

                val_name = "filter_key_" + str(i) + "_value"
                bind_vars[val_name] = comp_value

                final_key = filter_key
                if final_key == main_collection:
                    final_key = "doc" 
                else:
                    final_key = final_key + "_item"
                
                
                aql_query += " " + final_key + "." + filter_field + " " + compare + " @" + val_name + ""
            aql_query += ")"

        if sort_by is not None:
            sort_item = sort_by[0] + "_item"
            if sort_by[0] == main_collection:
                sort_item = "doc"
            aql_query += f" SORT {sort_item}.{sort_by[1]} {sort_by[2]}"

        if limit is not None:
            aql_query += f" LIMIT {skip}, {limit}"

        aql_query += " RETURN { " + main_collection + ": doc "

        for i,join_col in enumerate(join_list):
            aql_query += ", " + join_col + ": "  + join_col + "_item"
        aql_query += " }"
        print(aql_query)
        print(bind_vars)
            
        cursor = self._db.aql.execute(
            aql_query,
            bind_vars=bind_vars
        )

        items = list(cursor)
        return items



        

    def get_vertex_list_sorted(self, collection, sort_field, sort_dir, filter=None, limit=None, skip=0):

        aql_query = f"FOR doc IN {collection}"
        bind_vars = {
            
        }

        aql_query += f" SORT doc.{sort_field} {sort_dir}"


        if filter is not None:
            aql_query += " FILTER doc." + filter['filter'] + " " + filter['cond'] + " " + filter['value']

        if limit is not None:
            aql_query += f" LIMIT {skip}, {limit}"

        aql_query += " RETURN doc"

        cursor = self._db.aql.execute(
            aql_query,
            bind_vars=bind_vars
        )

        items = list(cursor)
        return items

    def get_vertex_list(self, graph_name, collection, filter=None, limit=None, skip=0, order=None):
        col = self._get_vertexes(graph_name, collection)
        cursor = None

        
        if filter:
            if not limit:
                cursor = col.find(filter,skip=skip)
            else:
                cursor = col.find(filter,skip=skip, limit=1)
        else:
            if not limit:
                cursor = col.all(skip=skip)
            else:
                cursor = col.all(skip=skip, limit=1)

        items = list(cursor)
        return items

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
        if 'uuid' in document:
            del document['uuid']
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
    

    def get_in_path(self, graph_name, from_item, end_item, path_pos, edges, max=2, return_fields=None):
        start_collection = from_item.split("/")[0]

        query = f"""
FOR start IN @@startCollection FILTER start._id == @fromId
    FOR v, e, p IN 1..@max ANY start 
    GRAPH @graphName
    FILTER v._id == @endId"""

        filter_edge_query = ""
        if len(edges) <= 0:
            raise ValueError("must have edges for get_in_path")

        for edge in edges:
            if filter_edge_query == "":
                filter_edge_query = f" AND (IS_SAME_COLLECTION('{edge}', e._id)"
            else:
                filter_edge_query += f" OR IS_SAME_COLLECTION('{edge}', e._id)"


        query += filter_edge_query + ")"

        if return_fields is None:
            query += "    RETURN p['vertices'][@pos]"
        else:
            query += "    RETURN {"
            for return_field in return_fields:
                query += f" {return_field}: p['vertices'][@pos].{return_field}, "
            query += "}"

        print(query)

        cursor = self._db.aql.execute(query, 
            bind_vars={
                '@startCollection': start_collection,
                'endId': end_item,
                'graphName': graph_name,
                'fromId': from_item,
                'max': max,
                "pos": path_pos
            })
        return list(cursor)


    def get_connected_to(self, graph_name, from_item, end_collection, filter_edges=None, max=2):

        start_collection = from_item.split("/")[0]

        query = f"""
FOR start IN @@startCollection FILTER start._id == @fromId
    FOR v, e, p IN 1..@max OUTBOUND start 
    GRAPH @graphName
    FILTER IS_SAME_COLLECTION('{end_collection}', v._id)"""

        filter_edge_query = ""
        if filter_edges is not None:
            for edge in filter_edges:
                if filter_edge_query == "":
                    filter_edge_query = f" AND (IS_SAME_COLLECTION('{edge}', e._id)"
                else:
                    filter_edge_query += f" OR IS_SAME_COLLECTION('{edge}', e._id)"

            if filter_edge_query != "":
                query += filter_edge_query + ")"

        query += "    RETURN v"

        print(query)

        cursor = self._db.aql.execute(query, 
            bind_vars={
                '@startCollection': start_collection,
                # '@endCollection': end_collection,
                'graphName': graph_name,
                'fromId': from_item,
                'max': max
            })
        return list(cursor)

        # from_col = self._extract_collection_from_id(from_item)
        # col = self._get_edges(graph_name, collection, from_col, None)
        # if col is None:
        #     return []
        # items = list(col.find({"_from": from_item}))
        # return items
        


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

    def get_list_by_match(self, collection, field, value, skip=0, limit=0):
        col = self._get_collection(collection) 
        cursor = None
        if limit != 0:
            cursor = col.find({field: value}, skip=skip, limit=limit)
        else:
            cursor = col.find({field: value}, skip=skip)
        return list(cursor)

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



    
