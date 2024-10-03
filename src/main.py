# From https://github.com/opper-ai/test-integration/blob/main/index_docs.py
from opperai import Opper
from opperai.types.indexes import DocumentIn
from opperai.types.exceptions import APIError
from opperai.types import BaseModel, Field
import os
import sys
import urllib.parse

os.environ["OPPER_API_KEY"] = sys.argv[1]
opper = Opper()

index_name = sys.argv[2]
folder_path = sys.argv[3]
file_types = sys.argv[4].split()
model = sys.argv[5]

# Get GitHub-related information from environment variables
repository = os.environ.get("GITHUB_REPOSITORY")
github_ref = os.environ.get("GITHUB_REF")


try:
    index = opper.indexes.create(name=index_name)
except APIError:
    index = opper.indexes.get(name=index_name)
    if not index:
        raise Exception("Index not found")


class Object(BaseModel):
    name: str = Field(
        ..., description="Header or a few words of what the page is about"
    )
    keywords: str = Field(..., description="Top 5 keywords of the object contents")
    last_modified: str = Field(..., description="The date this was last modified")
    size: str = Field(..., description="The size of the object")
    source: str = Field(
        ..., description="The technical identifier of the object, preferably full path"
    )


def create_metadata(file_data: dict) -> Object:
    """Assemble an object that describes the doc item"""


def process_markdown_file(file_path):
    """
    Process the markdown file and create a URL for the file in the GitHub repository.
    """
    file_name = os.path.basename(file_path)

    with open(file_path) as f:
        lines = f.readlines()
    contents = "\n".join(lines)

    stats = os.stat(file_path)

    file_data = dict(
        (key, getattr(stats, key)) for key in dir(stats) if key.startswith("st_")
    )
    file_data["path"] = file_path
    file_data["contents"] = contents

    meta_data, _ = opper.call(
        name="create_metadata", input=file_data, output_type=Object, model=model
    )
    meta_data = dict(meta_data)
    meta_data["name"] = file_name

    # Create the GitHub URL for the file
    relative_path = os.path.relpath(file_path, folder_path)
    encoded_path = urllib.parse.quote(os.path.join(folder_path, relative_path))
    github_url = f"https://github.com/{repository}/blob/{github_ref}/{encoded_path}"
    meta_data["url"] = github_url

    print(meta_data)

    index_document(key=file_name, metadata=meta_data, content=contents)


def traverse_and_process(folder_path):
    """
    Recursively traverse the given folder, processing each markdown file found.
    """
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.endswith(file_type) for file_type in file_types):
                file_path = os.path.join(root, file)
                process_markdown_file(file_path)


def index_document(key, metadata, content):
    _ = index.add(doc=DocumentIn(content=content, key=key, metadata=metadata))


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "Usage: python script.py <api_key> <index_name> <folder_path> <file_types> <model>"
        )
        sys.exit(1)

    traverse_and_process(folder_path)
