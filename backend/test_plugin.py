import argparse 
import json 
import os
from re import sub
import shutil

import sys
import os 

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
sys.path.append(os.curdir)


from lib.submission import Submission, SubmissionFile
from lib.plugin_manager import PluginManager
from lib.job import Job


TEST_SUBMISSION_DIR = "/tmp/kodiatest"
COUNTER = 1

def get_number():
    global COUNTER
    ret = COUNTER
    COUNTER += 1
    return ret

class DBStub():
    
    def lock(self):
        pass

    def unlock(self):
        pass

    def get_vertex_by_match(self, graph_name, collection, field, value):
        col = self._get_vertexes(graph_name, collection)
        cursor = col.find({field: value}, skip=0, limit=1)
        item = cursor.next()
        return item

    def get_vertex_by_id(self, graph_name, collection, id):
        col = self._get_vertexes(graph_name, collection)
        return col.get(id)

    def insert_vertex(self, graph_name, collection, document):
        print(f"Graph: {graph_name}, Collection: {collection}")
        print(f"{collection}: " + json.dumps(document, indent=4))
        return f"{collection}/{get_number()}"
      
    def insert_edge(self, graph_name, collection, from_item, to_item, data=None, unique=True):
        print(f"Graph: {graph_name}, Collection: {collection}")
        print(f"{from_item} => {to_item}")
        if data is not None:
            print(json.dumps(data, indent=4))
        return f"{collection}/{get_number()}"

    def insert(self, collection, document):
        print(collection)
        print(json.dumps(document, indent=4))
        return f"{collection}/{get_number()}"
        
    def update_vertex(self, graph_name, collection, id, document):
        print(f"Graph: {graph_name}, Collection: {collection}")
        print(f"{collection}/{id}: " + json.dumps(document, indent=4))
        return f"{collection}/{get_number()}" 

    def delete(self, collection, query):
        pass 



     

def main():
    parser = argparse.ArgumentParser(description='Test a plugin')
    parser.add_argument('--file', help='File(s) to test with', action='append', required=True)
    parser.add_argument('--plugin', help='Plugin to test', required=True)
    parser.add_argument('--meta', help='Metadata to add to submission', action='append')
    parser.add_argument('--mimetype', help='Set mimetype of file')

    args = parser.parse_args()

    db = DBStub()

    

    submission = Submission.new(TEST_SUBMISSION_DIR)

    if os.path.exists(TEST_SUBMISSION_DIR):
        shutil.rmtree(TEST_SUBMISSION_DIR)
    os.mkdir(TEST_SUBMISSION_DIR)

    primary = None
    for item in args.file:
        
        filename = os.path.basename(item)
        new_path = os.path.join(TEST_SUBMISSION_DIR, filename)
        
        new_file = submission.generate_file(filename)
        shutil.copy(item, new_file.file_path)
        submission.add_file(new_file)
        
        if primary is None:
            primary = new_file

    submission.save(db)

    manager = PluginManager()
    manager.load()

    plugin = manager.get_plugin(args.plugin)
    if plugin is None:
        print(f"Invalid plugin {args.plugin}")
        return

    print(f"Primary file is {primary.file_path}")

    job = Job.new(submission, primary, db)

    if args.mimetype is not None:
        primary.mime_type = args.mimetype

    if plugin.operates_on(primary):
        new_files = plugin.run(job, primary)
        submission.save(db)
    else:
        print("Does not operate on this file type")
    

    

main()