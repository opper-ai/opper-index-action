# Github action to index repository files in Opper

This GitHub Action indexes specified file types in Opper.

## Inputs

- `apikey`: The Opper API key (required)
- `index`: The Opper index name (default: `repo-docs`)
- `folder`: The folder to index (default: `.`)
- `file_types`: JSON array of file extensions to index (default: `.md .mdx .txt`)
- `model`: Custom model to use for indexing (optional)

## Example Usage

### Basic Usage

```yaml
name: Index Docs in Opper
on:
  push:
    branches: [main]
jobs:
  index-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Index docs in Opper
        uses: opper-ai/opper-index-action@v1.0.0
        with:
          apikey: ${{ secrets.OPPER_API_KEY }}
```

### Custom Folder and Index Name

```yaml
name: Index Docs in Opper
on:
  push:
    branches: [main]
jobs:
  index-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Index docs in Opper
        uses: opper-ai/opper-index-action@v1.0.0
        with:
          folder: 'docs'
          apikey: ${{ secrets.OPPER_API_KEY }}
          index: 'my-custom-index'
```

### Using a Custom Model

```yaml
name: Index Docs in Opper
on:
  push:
    branches: [main]
jobs:
  index-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Index docs in Opper
        uses: opper-ai/opper-index-action@v1.0.0
        with:
          apikey: ${{ secrets.OPPER_API_KEY }}
          model: 'azure/gpt-4o-eu'
```


### Customizing File Types

```yaml
name: Index Docs in Opper
on:
  push:
    branches: [main]
jobs:
  index-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Index docs in Opper
        uses: opper-ai/opper-index-action@v1.0.0
        with:
          apikey: ${{ secrets.OPPER_API_KEY }}
          file_types: '.md .mdx .txt .html .js'
```
