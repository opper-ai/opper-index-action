# From https://github.com/opper-ai/test-integration/blob/main/index_docs.py
from opperai import Opper
from opperai.types.indexes import DocumentIn
from opperai.types.exceptions import APIError
from opperai.types import BaseModel, Field
import os
import sys

os.environ["OPPER_API_KEY"] = sys.argv[1]
opper = Opper()

model = sys.argv[5]

try:
    index = opper.indexes.create(name=sys.argv[2])
except APIError:
    index = opper.indexes.get(name=sys.argv[2])
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
    Process the markdown file. The processing logic depends on your requirements.
    For example, you might want to read the file's content, perform some modifications,
    or simply print the file path.
    """

    file_name = file_path

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
            "Usage: python script.py <api_key> <index_name> <model> <folder_path> <file_types>"
        )
        sys.exit(1)

    folder_path = sys.argv[3]
    file_types = sys.argv[4].split()

    traverse_and_process(folder_path)
