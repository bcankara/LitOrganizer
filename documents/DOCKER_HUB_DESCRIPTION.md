# LitOrganizer

Organize your academic literature efficiently with a graphical user interface.

## Features

- **Smart Metadata Extraction**: Automatically extracts DOIs and retrieves complete metadata from academic APIs
- **Citation-based Renaming**: Renames PDF files using APA7 format
- **Intelligent Categorization**: Organizes PDFs into folders by journal, author, year, or subject
- **Full-text Search**: Search across your entire PDF collection
- **OCR Support**: Extract text from scanned documents

## Usage

This Docker image includes a graphical user interface which requires X11 forwarding.

### For Windows:

1. Install and run an X server like [VcXsrv](https://sourceforge.net/projects/vcxsrv/) or [Xming](https://sourceforge.net/projects/xming/)
2. Run XLaunch with these settings:
   - Display settings: Multiple windows
   - Client startup: Start no client
   - Extra settings: ✓ Disable access control
3. Run the container:

```bash
docker run -it --rm -e DISPLAY=host.docker.internal:0 -v %cd%/pdfs:/app/pdf bcankara/litorganizer
```

### For Linux:

```bash
docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $(pwd)/pdfs:/app/pdf bcankara/litorganizer
```

### For macOS:

1. Install and run [XQuartz](https://www.xquartz.org/)
2. Run these commands:

```bash
xhost + 127.0.0.1
docker run -it --rm -e DISPLAY=host.docker.internal:0 -v $(pwd)/pdfs:/app/pdf bcankara/litorganizer
```

## Volumes

- `/app/pdf`: Directory for PDF files to be processed
- `/app/processed`: Directory for processed/renamed files
- `/app/logs`: Log files directory
- `/app/config`: Configuration files directory

## Environment Variables

- `DISPLAY`: Required for GUI forwarding
- `LANG` and `LC_ALL`: Set to tr_TR.UTF-8 by default for Turkish language support

## Source Code

[GitHub Repository](https://github.com/bcankara/LitOrganizer) 