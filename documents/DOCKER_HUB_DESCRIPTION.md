# LitOrganizer v2

Automated Academic PDF Organization & Search — Powered by AI

## What's New in v2

- **Web Interface**: No more X11/GUI forwarding — access via browser at `http://localhost:5000`
- **AI Fallback**: Google Gemini Flash 2.0 for PDFs without DOI
- **Full-text Search**: Keyword search across your entire PDF collection with context
- **Export Results**: Download search results as Excel or Word
- **More APIs**: OpenAlex, Crossref, DataCite, Europe PMC, Semantic Scholar, Scopus, Unpaywall

## Quick Start

```bash
docker run -d -p 5000:5000 -v $(pwd)/pdfs:/app/pdf bcankara/litorganizer:v2
```

Then open your browser at **http://localhost:5000**

## Docker Compose

```yaml
services:
  litorganizer:
    image: bcankara/litorganizer:v2
    ports:
      - "5000:5000"
    volumes:
      - ./pdfs:/app/pdf
      - ./processed:/app/processed
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
```

Save as `docker-compose.yml` and run:

```bash
docker compose up -d
```

## Volumes

| Path | Description |
|------|-------------|
| `/app/pdf` | Input directory — place your PDF files here |
| `/app/processed` | Output directory for renamed/organized files |
| `/app/logs` | Log files |
| `/app/config` | `api_keys.json` — persist your API key settings |

## API Keys (Optional)

To enable AI fallback and additional metadata sources, mount a `config/api_keys.json`:

```json
{
    "gemini": { "api_key": "YOUR_GEMINI_API_KEY", "enabled": true },
    "scopus": { "api_key": "YOUR_SCOPUS_API_KEY", "enabled": false }
}
```

Or configure keys directly from the **Settings** page in the web UI.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LITORGANIZER_HOST` | `0.0.0.0` | Bind address |

## Source Code

[GitHub Repository](https://github.com/bcankara/LitOrganizer)
