import os
import re

from flask import Blueprint, Flask, g, jsonify, current_app, request, send_file, send_from_directory, abort
from backend.lib.data import ExecInstance
from backend.api.helpers import json_resp_ok, json_resp_invalid, json_resp_not_found

from backend.version import VERSION 

docs_endpoints = Blueprint('docs', __name__)

def get_pages_nav(dir, subpath):
    nav_items = []
    items = os.listdir(dir)
    items.sort()
    for item in items:
        full_path = os.path.join(dir, item)
        if os.path.isfile(full_path):
            with open(full_path, "r") as in_file:
                file_data = in_file.read().strip()
                lines = file_data.split("\n")
                title = item
                if lines[0].startswith("# "):
                    title = lines[0][1:].strip()
                nav_items.append({
                    "title": title,
                    "path": os.path.join(subpath, item.replace(".md", "")),
                })
        elif os.path.isdir(full_path):
            title = item.capitalize()
            nav_items.append({
                "title": title,
                "path": "",
                "subpaths": get_pages_nav(os.path.join(dir, item), os.path.join(subpath, item))
            })
    return nav_items

@docs_endpoints.route('/<path:page>')
def get_page(page):

    path_items = page.split("/")
    for i in range(len(path_items)):
        path_items[i] = re.sub(r"[^-a-zA-Z0-9_]", "", path_items[i])

    filename = path_items[-1]
    subpath = path_items[:-1]

   

    full_path = os.path.join(current_app._docs_dir, *subpath, filename + ".md")

    if not os.path.exists(full_path):
        return json_resp_not_found("Page does not exist")
    else:
        page_data = ""
        with open(full_path, "r") as page_file:
            page_data = page_file.read()
        return json_resp_ok({
            "page": page_data,
            "navigation": get_pages_nav(current_app._docs_dir, "")
        })
