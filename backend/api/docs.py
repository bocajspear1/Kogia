import os
import re

from fastapi import APIRouter, Request, HTTPException, Response

from backend.lib.data import Process

from .types import OptionalStrParam, DocsResponse


from backend.version import VERSION 

router = APIRouter(tags=['docs'])

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
            # Ignore images directory
            if item == "images":
                continue
            title = item.capitalize()
            nav_items.append({
                "title": title,
                "path": "",
                "subpaths": get_pages_nav(os.path.join(dir, item), os.path.join(subpath, item))
            })
    return nav_items

@router.get('/{page:path}')
def get_page(req : Request, page: str) -> DocsResponse:

    extension = ""

    if page.endswith(".png"):
        extension = ".png"
        page = page.replace(".png", "")

    path_items = page.split("/")
    for i in range(len(path_items)):
        path_items[i] = re.sub(r"[^-a-zA-Z0-9_]", "", path_items[i])

    filename = path_items[-1]

    if path_items[0] == "images":
        full_path = os.path.join(req.app._docs_dir, "images", filename + extension)

        return Response(content=open(full_path, "rb").read(), media_type='image/png')
    else:
        subpath = path_items[:-1]

    

        full_path = os.path.join(req.app._docs_dir, *subpath, filename + ".md")

        if not os.path.exists(full_path):
            raise HTTPException(404, detail="Page not found")
        else:
            page_data = ""
            with open(full_path, "r") as page_file:
                page_data = page_file.read()
            return DocsResponse(page=page_data, navigation=get_pages_nav(req.app._docs_dir, ""))
