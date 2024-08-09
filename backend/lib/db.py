from arango import ArangoClient
from arango.http import DefaultHTTPClient
from arango.exceptions import DocumentInsertError, AQLQueryExecuteError
from threading import RLock

import requests
requests.packages.urllib3.disable_warnings()

NO_INDEX = ('logs', 'syscalls')

class DBNotUniqueError(Exception):
    pass

class ArangoConnectionFactory():

    def __init__(self, host, port, username, password, db_name, ssl=False, ssl_verify=True):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._verify = ssl_verify
        self._db_name = db_name

    def new(self):
        new_conn = ArangoConnection(self._host, self._port, self._username, self._password, self._db_name, ssl=self._ssl, ssl_verify=self._verify)
        new_conn.connect()
        return new_conn

class ArangoConnection():

    def __init__(self, host, port, username, password, db_name, ssl=False, ssl_verify=True):
        self._host = host
        self._port = port 
        self._username = username 
        self._password = password
        self._ssl = ssl
        self._verify = ssl_verify
        self._db_name = db_name
        self._db_lock = RLock()

        self._db = None
        self._conn = None
        self._cur_graph = None

    def connect(self):
        proto = "http"
        if self._ssl:
            proto = "https"

        self._conn = ArangoClient(hosts=f"{proto}://{self._host}:{self._port}", 
                                  http_client=DefaultHTTPClient(request_timeout=5*60),
                                  verify_override=self._verify)
        self._db = self._conn.db(self._db_name, username=self._username, password=self._password)


    @property
    def db(self):
        return self._db
    
    @property
    def version(self):
        return self._db.version()

    def lock(self):
        self._db_lock.acquire()

    def unlock(self):
        self._db_lock.release()

    def truncate_all_collections(self):
        """
        Remove all data in all collections. 

        DANGEROUS!
        """
        collection_list = self._db.collections()
        for collection in collection_list:
            if collection['name'].startswith("_"):
                continue
            self.truncate_collection(collection['name'])

    def truncate_collection(self, collection):
        """
        Remove all data in a collection. 

        DANGEROUS!
        """
        if self._db.has_collection(collection):
            self._db.collection(collection).truncate()

    def _insert_indexed_collection(self, graph_name, collection):
        graph = self._get_graph(graph_name)
        if not graph.has_vertex_collection(collection):
            new_collection = graph.create_vertex_collection(collection)

    def _get_graph(self, graph_name):
        """
        Get graph wrapper and ensure it exists
        """
        if not self._db.has_graph(graph_name):
            return self._db.create_graph(graph_name)
        else:
            return self._db.graph(graph_name)

    def _get_vertexes(self, graph_name, collection):
        graph = self._get_graph(graph_name)
        if not graph.has_vertex_collection(collection):
            new_collection = graph.create_vertex_collection(collection)
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
            return new_collection
        else:
            return self._db.collection(collection)

    def _extract_collection_from_id(self, id):
        return id.split("/")[0]
            
    def get_vertex_by_match(self, graph_name, collection, field, value):
        """
        Get a single vertex by match
        """
        col = self._get_vertexes(graph_name, collection)
        cursor = col.find({field: value}, skip=0, limit=1)
        if cursor.count() == 0:
            return None
        item = cursor.next()
        return item

    def get_vertex_by_id(self, graph_name, collection, id):
        """
        Get a single vertex by id value
        """
        col = self._get_vertexes(graph_name, collection)
        return col.get(id)

    def find_vertexes(self, graph_name, collection, sort_tuple=None, filter_tuple=None, limit=None, skip=0, count_only=False):
        self._insert_indexed_collection(graph_name, collection)

        aql_query = f"FOR v IN {collection}"
        bind_vars = {
            
        }

        if filter_tuple is not None:
            new_bind_vars, filter_query = self._parse_filter(collection, filter_tuple)
            bind_vars.update(new_bind_vars)
            aql_query += " FILTER " + filter_query + " "

        if sort_tuple is not None:
            aql_query += f" SORT v.{sort_tuple[0]} {sort_tuple[1]}"

        if limit is not None:
            aql_query += f" LIMIT {int(skip)}, {int(limit)}"

        if not count_only:
            aql_query += " RETURN v"
        else:
            aql_query += " COLLECT WITH COUNT INTO length RETURN length"

        # print(aql_query)
        # print(bind_vars)

        cursor = self._db.aql.execute(
            aql_query,
            bind_vars=bind_vars
        )

        items = list(cursor)
        return items


    def _get_aql_filter(self, main_collection, filter_map):

        filter_query = ""
        new_bind_vars = {}

        filter_keys = list(filter_map.keys())
        for i,filter_key in enumerate(filter_keys):
            if filter_query != "":
                filter_query += " AND "

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
            new_bind_vars[val_name] = comp_value

            final_key = filter_key
            if final_key == main_collection:
                final_key = "doc" 
            else:
                final_key = final_key + "_item"
            
            if compare == "IREGEX":
                filter_query += f" REGEX_TEST({final_key}.{filter_field}, @{val_name}, true)"
            else:
                filter_query += " " + final_key + "." + filter_field + " " + compare + " @" + val_name + ""

        # print(filter_query)
        return filter_query, new_bind_vars

    # {"test": ()}
    def get_vertex_list_joined(self, graph_name, main_collection, join_map, sort_by=None, filter_map=None, limit=None, skip=0, length_only=False):
        aql_query = f"FOR doc IN {main_collection}"
        bind_vars = {}

        join_list = list(join_map.keys())

        self._insert_indexed_collection(graph_name, main_collection)

        for i,join_col in enumerate(join_list):
            self._insert_indexed_collection(graph_name, join_col)
            aql_query += " FOR " + join_col + "_item IN " + join_col


        aql_query += " FILTER "
        first = True
        merge_list = []
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
            merge_list.append((orig_field, join_col))
        
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


        if not length_only:
            aql_query += " RETURN merge(doc, { "

            for i,merge_data in enumerate(merge_list):
                if i != 0:
                    aql_query += ", "
                aql_query += merge_data[0] + ": "  + merge_data[1] + "_item"

            aql_query += " })"
        else:
            aql_query += " COLLECT WITH COUNT INTO length RETURN length"

        # print(aql_query)
        # print(bind_vars)
            
        cursor = self._db.aql.execute(
            aql_query,
            bind_vars=bind_vars
        )

        items = list(cursor)
        return items


    def get_vertex_list_sorted(self, graph_name, collection, sort_field, sort_dir, filter_map=None, limit=None, skip=0, length_only=False):
        self._insert_indexed_collection(graph_name, collection)

        aql_query = f"FOR doc IN {collection}"
        bind_vars = {
            
        }

        aql_query += f" SORT doc.{sort_field} {sort_dir}"


        if filter_map is not None:
            filter_query, new_bind_vars = self._get_aql_filter(collection, filter_map)
            bind_vars.update(new_bind_vars)
            aql_query += filter_query
            # aql_query += " FILTER doc." + filter['filter'] + " " + filter['cond'] + " " + filter['value']

        if limit is not None:
            aql_query += f" LIMIT {skip}, {limit}"

        if not length_only:
            aql_query += " RETURN doc"
        else:
            aql_query += " COLLECT WITH COUNT INTO length RETURN length"

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
            if "unique constraint violated" in str(e) and '_key' in document:
                obj = self.get_vertex_by_match(graph_name, collection, '_key', document['_key'])
                return obj['_id']
            else:
                raise e

    def update_vertex(self, graph_name, collection, id, document):
        col = self._get_vertexes(graph_name, collection)
        if '_key' in document:
            del document['_key']
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
    

    def insert_edge_bulk(self, graph_name, collection, from_item, to_collection, to_list, unique=True):
        from_col = self._extract_collection_from_id(from_item)
        self._get_edges(graph_name, collection, from_col, to_collection, unique=unique)

        job_res = None
        with self.db.begin_batch_execution(return_result=True) as batch_db:
            batch_graph = batch_db.graph(graph_name)
            batch_col = batch_graph.edge_collection(collection)
            for item in to_list:
                job_res = batch_col.link(from_item, item)


    def _create_graph_query(self, graph_name, start_collection, start_item, end_item, edge_filter=None, max=2):
        query = f"""
FOR start IN @@startCollection FILTER start._id == @fromId
    FOR v, e, p IN 1..@max ANY start 
    GRAPH @graphName
    FILTER v._id == @endId"""
        
        bind_vars = {
            '@startCollection': start_collection,
            'endId': end_item,
            'graphName': graph_name,
            'fromId': start_item,
            'max': max
        }
        

        return query, bind_vars



    def _parse_filter(self, collection, filter_item):
        """Coverts a nest set of tuples into a string filter for AQL with binding parameters.

            Format is ('AND|OR', [
                (key, value),
                (OP, key, value),
                (OP, COL, key, value)
            ])

           Note: OP, key, or COL should not be user provided!
        
        """
        
        if filter_item[0] in ("OR", "AND"):
            filter_str = ""
            variable_map = {}
            for subfilter in filter_item[1]:
                new_vars, subfilter_str = self._parse_filter(collection, subfilter)
                variable_map.update(new_vars)
                if filter_str != "":
                    filter_str += f" {filter_item[0]} "
                filter_str += f"({subfilter_str})"
            return variable_map, filter_str
        else:
            if len(filter_item) == 2:
                var_name = f"{filter_item[0]}_val"
                return {
                    var_name: filter_item[1]
                }, f"v.{filter_item[0]} == @{var_name}"
            elif len(filter_item) == 3 or len(filter_item) == 4:
                collection = "v"
                operator = filter_item[0]
                key_name = filter_item[1]
                var_name = f"{key_name}_val"
                var_data = filter_item[2]
                if len(filter_item) == 4:
                    collection = filter_item[1]
                    var_name = f"{filter_item[2]}_val"
                    var_data = filter_item[3]
                    
                if operator == "IREGEX":
                    return {
                        var_name: var_data
                    }, f"REGEX_TEST({collection}.{key_name}, @{var_name}, true)"
                elif operator == "REGEX":
                    return {
                        var_name: var_data
                    }, f"REGEX_TEST({collection}.{key_name}, @{var_name}, false)"
                elif operator == "ILIKE":
                    return {
                        var_name: str(var_data).lower()
                    }, f"LOWER({collection}.{key_name}) LIKE @{var_name}"
                elif operator in ('==', '=', '!=', '<=', '>=', '<', '>'):
                    return {
                        var_name: var_data
                    }, f"{collection}.{filter_item[0]} {operator} @{var_name}"

                
                

    def get_connected_to(self, graph_name, from_item, end_item, filter_edges=None, filter_vertices=None, sort_by=None, max=2, direction='both', limit=0, 
                         skip=0, length_only=False, add_edges=False, return_path=False):
        """Get items connected in graph `graph_name` starting at `start_item` and ending at `end_item`. `end_item` can be the _id of another document 
        or the name of a collection. 
        
        Use `filter_edges` to limit paths explored to speed up retrieval. `filter_edges` is a list of edge collection names.
        
        """
        start_collection = from_item.split("/")[0]
        if "/" in end_item:
            end_collection = end_item.split("/")[0]
        else:
            end_collection = end_item

        bind_vars = {
            '@startCollection': start_collection,
            # '@endCollection': end_collection,
            'graphName': graph_name,
            'fromId': from_item,
            'max': max
        }

        query_dir = "ANY"
        if direction == "out":
            query_dir = "OUTBOUND"
        elif direction == "in":
            query_dir = "INBOUND"

        query = f"""
FOR start IN @@startCollection FILTER start._id == @fromId
    FOR v, e, p IN 1..@max {query_dir} start 
    GRAPH @graphName"""
        
        if filter_edges is not None and not isinstance(filter_edges, list):
            raise ValueError("filter_edges is not list")

        filter_edge_query = ""
        if filter_edges is not None:
            query += " OPTIONS { "
            query += "edgeCollections: " + repr(filter_edges)
            query += " }"

        if end_collection == end_item:
            query += f" FILTER IS_SAME_COLLECTION('{end_collection}', v._id)"
        else:
            bind_vars['endItem'] = end_item
            query += f" FILTER v._id == @endItem"

        if filter_vertices is not None:
            new_bind_vars, filter_query = self._parse_filter(end_collection, filter_vertices)
            bind_vars.update(new_bind_vars)
            query += " AND " + filter_query + " "
        
        if sort_by is not None:
            sort_item = sort_by[0] + "_item"
            if sort_by[0] == end_collection:
                sort_item = "v"
            elif sort_by[0] in filter_edges:
                sort_item = "e"

            query += f" SORT {sort_item}.{sort_by[1]} {sort_by[2]} "

        if limit > 0:
            query += "LIMIT "
            if skip > 0:
                query += "@skip, "
                bind_vars['skip'] = skip
            query += "@limit"
            bind_vars['limit'] = limit

        if length_only:
            query += "\n    COLLECT WITH COUNT INTO length RETURN length"
        elif add_edges:
            query += "\n    RETURN merge(v, {_edge: e})"
        elif return_path:
            query += "\n    RETURN p"
        else:
            query += "\n    RETURN v"

        # print(query, bind_vars)

        try:
            cursor = self._db.aql.execute(query, 
                bind_vars=bind_vars
            )
            return list(cursor)
        except AQLQueryExecuteError as e:
            print(e, e.error_code)
            if e.error_code == 1203:
                # Print We are missing a collection, probably hasn't been created yet.
                return []
            else:
                raise e

        

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
        
    def insert_bulk(self, collection, doc_array, requery=True):
        col = self._get_collection(collection)
        
        db_data = col.insert_many(doc_array, overwrite=True, overwrite_mode="replace", return_new=True)  
        if requery:
            db_data = col.get_many(doc_array)

        item_list = []
        for item in db_data:
            if isinstance(item, DocumentInsertError):
                # print(item.response.body)
                item_list.append(None)
            item_list.append(item)
        
        return item_list 

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
        try:
            item = cursor.next()
        except StopIteration:
            return None
        return item

    def get_by_id(self, collection, id):
        col = self._get_collection(collection) 
        return col.get(id)

    def delete(self, collection, query):
        pass 


    def all(self, collection):
        return self._get_collection(collection).all()

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
                # print(cursor.next())



    
