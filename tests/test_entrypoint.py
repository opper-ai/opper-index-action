"""Run with: python -m unittest discover -s tests -v (inside the action image)."""

import tempfile
import unittest
from pathlib import Path

from fixture_api import FixtureAPI


class RepositoryEntrypointTests(unittest.TestCase):
    def check_repository(self, existing):
        with tempfile.TemporaryDirectory() as directory, FixtureAPI(existing=existing) as api:
            root = Path(directory)
            (root / "docs" / "nested folder").mkdir(parents=True)
            files = {
                "docs/start.md": "# Getting started\nUseful instructions\n",
                "docs/nested folder/guide space.md": "# Nested guide\nRecursive content\n",
                "docs/notes.txt": "Plain text notes\n",
                "docs/ignored.png": "Not selected",
                "docs/ignored.md.bak": "Not selected",
                "docs/ignored.MD": "Case sensitive extension",
                "outside.md": "Outside configured folder",
            }
            for name, contents in files.items():
                (root / name).write_text(contents)
            result = api.run(
                "fixture-api-key", "fixture-index", "docs", ".md .txt", "fixture/custom-model",
                cwd=directory,
                extra_env={"GITHUB_REPOSITORY": "example/repository", "GITHUB_REF": "refs/heads/fixture-branch"},
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(len(api.documents), 3)
            docs = {doc["key"]: doc for doc in api.documents}
            self.assertEqual(set(docs), {"start.md", "guide space.md", "notes.txt"})
            for path in ("docs/start.md", "docs/nested folder/guide space.md", "docs/notes.txt"):
                doc = docs[Path(path).name]
                self.assertEqual(doc["content"], "\n".join(files[path].splitlines(keepends=True)))
                self.assertEqual(doc["metadata"]["name"], Path(path).name)
                self.assertEqual(doc["metadata"]["keywords"], "fixture, documentation")
                self.assertIn(Path(path).name, result.stdout)
            self.assertEqual(
                docs["guide space.md"]["metadata"]["url"],
                "https://github.com/example/repository/blob/refs/heads/fixture-branch/docs/nested%20folder/guide%20space.md",
            )
            self.assertEqual(len(api.calls), 3)
            metadata_inputs = [call["input"] for call in api.calls]
            self.assertEqual({item["path"] for item in metadata_inputs},
                             {"docs/start.md", "docs/nested folder/guide space.md", "docs/notes.txt"})
            for call in api.calls:
                self.assertEqual(call["name"], "create_metadata")
                self.assertEqual(call["model"], "fixture/custom-model")
                self.assertEqual(set(call["output_schema"]["required"]),
                                 {"name", "keywords", "last_modified", "size", "source"})
                self.assertTrue(call["parent_span_uuid"])
            self.assertEqual(len(api.created_indexes), 0 if existing else 1)
            if not existing:
                self.assertEqual(api.created_indexes[0]["name"], "fixture-index")
            spans = [body for method, path, body in api.requests if (method, path) == ("POST", "/v1/spans")]
            self.assertEqual(len(spans), 1)
            self.assertEqual(spans[0]["name"], "traverse_and_process")
            self.assertTrue(any(method == "PUT" and path.startswith("/v1/spans/")
                                for method, path, _ in api.requests))

    def test_create_index_and_recursively_index_selected_files(self):
        self.check_repository(existing=False)

    def test_reuse_existing_index_and_preserve_metadata(self):
        self.check_repository(existing=True)

    def test_excluded_files_produce_no_metadata_calls_or_documents(self):
        with tempfile.TemporaryDirectory() as directory, FixtureAPI(existing=True) as api:
            Path(directory, "ignored.txt").write_text("Excluded content")
            result = api.run("fixture-api-key", "fixture-index", directory, ".md", "fixture/model")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(api.calls, [])
            self.assertEqual(api.documents, [])

    def test_document_api_failure_is_not_silently_successful(self):
        with tempfile.TemporaryDirectory() as directory, FixtureAPI(existing=True, reject_document=True) as api:
            Path(directory, "guide.md").write_text("Fixture documentation")
            result = api.run("fixture-api-key", "fixture-index", directory, ".md", "fixture/model")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Failed to add document", result.stderr)
            self.assertEqual(len(api.calls), 1)
            self.assertEqual(api.documents, [])


if __name__ == "__main__":
    unittest.main()
