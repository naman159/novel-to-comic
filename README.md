# Novel to Comic Generator (NTC)

A Python application that converts novel chapters into manhwa-style comics using Google's Gemini 2.5 Flash AI models. The system maintains character and location consistency across panels and chapters.

## Architecture Overview

### Core Components

1. **Entity Management System**

   - **Character Registry**: Stores character descriptions, visual traits, and generated images
   - **Location Registry**: Stores location descriptions and generated background images
   - **Asset Database**: Persistent JSON storage mapping entity names to asset metadata and image paths

2. **Chapter Processing Pipeline**

   - **Scene Segmentation**: AI breaks chapter into logical scenes
   - **Panel Planning**: AI determines how many panels per scene and their content
   - **Asset Identification**: Extract which characters/locations appear in each panel
   - **Image Generation**: Compose panels using consistent assets

3. **Asset Consistency Strategy**
   - **Character Templates**: Generate character base images with consistent style
   - **Location Templates**: Generate location base images
   - **Composition Engine**: Combine assets using Gemini 2.5 Flash for final panel generation

### Data Flow

```
Novel Chapter → Entity Extraction → Asset Generation → Scene Segmentation → Panel Planning → Image Composition → Comic Panels
```

## Features

- **Character Consistency**: Maintains consistent character appearances across panels
- **Location Consistency**: Reuses location backgrounds for visual coherence
- **AI-Powered Scene Analysis**: Automatically identifies scenes and creates appropriate panels
- **Persistent Asset Storage**: Saves generated assets for reuse across chapters
- **Manhwa Style**: Generates images in modern manhwa/webtoon style

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd ntc
   ```

2. **Install dependencies**:

   ```bash
   pip install -e .
   ```

3. **Set up Google Gemini API**:
   - Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Set the environment variable:
     ```bash
     export GOOGLE_API_KEY="your-api-key-here"
     ```

## Usage

### Basic Usage

```python
from main import NovelToComic

# Initialize the comic generator
comic_generator = NovelToComic(output_dir="my_comic")

# Process a chapter
chapter_text = """
Chapter 1: The Beginning

Sarah stood at the edge of the ancient forest, her heart pounding with anticipation...
"""

# Generate comic panels
panel_paths = comic_generator.process_chapter(chapter_text)

print(f"Generated {len(panel_paths)} panels:")
for i, path in enumerate(panel_paths):
    print(f"  Panel {i+1}: {path}")
```

### Advanced Usage

```python
# Custom output directory
comic_generator = NovelToComic(output_dir="custom_output")

# Process multiple chapters
chapters = [
    "Chapter 1 text...",
    "Chapter 2 text...",
    "Chapter 3 text..."
]

for i, chapter in enumerate(chapters):
    print(f"Processing Chapter {i+1}...")
    panel_paths = comic_generator.process_chapter(chapter)
    print(f"Generated {len(panel_paths)} panels for Chapter {i+1}")
```

## Project Structure

```
ntc/
├── main.py              # Main application logic
├── image_utils.py       # Image generation utilities
├── pyproject.toml       # Project configuration
├── README.md           # This file
└── comic_output/       # Generated assets (created at runtime)
    ├── characters/     # Character images
    ├── locations/      # Location images
    ├── panels/         # Generated comic panels
    ├── characters.json # Character metadata
    └── locations.json  # Location metadata
```

## API Reference

### NovelToComic Class

#### Constructor

```python
NovelToComic(output_dir: str = "comic_output")
```

#### Methods

- `extract_entities(chapter: str) -> Tuple[List[Character], List[Location]]`

  - Extracts characters and locations from chapter text using AI

- `generate_character_image(character: Character) -> str`

  - Generates a consistent character image using Gemini 2.5 Flash

- `generate_location_image(location: Location) -> str`

  - Generates a consistent location image using Gemini 2.5 Flash

- `split_scenes(chapter: str) -> List[Scene]`

  - Splits chapter into individual scenes using AI

- `direct_panel(scene_description: str, characters: List[str], location: str) -> List[Panel]`

  - Creates panel descriptions for a scene

- `fetch_assets(panel: Panel) -> Dict[str, str]`

  - Identifies and fetches required assets for a panel

- `generate_panel_image(panel: Panel, assets: Dict[str, str]) -> str`

  - Generates the final panel image by composing assets

- `process_chapter(chapter: str) -> List[str]`
  - Main pipeline: converts chapter to list of panel image paths

### Data Classes

#### Character

```python
@dataclass
class Character:
    name: str
    description: str
    visual_traits: str
    image_path: Optional[str] = None
```

#### Location

```python
@dataclass
class Location:
    name: str
    description: str
    image_path: Optional[str] = None
```

#### Scene

```python
@dataclass
class Scene:
    content: str
    characters: List[str]
    location: str
    panels: List[str]
```

#### Panel

```python
@dataclass
class Panel:
    description: str
    characters: List[str]
    location: str
    composition_prompt: str
```

## Configuration

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key (required)

### Output Directory Structure

The application creates the following directory structure:

```
output_dir/
├── characters/          # Character images
│   ├── character1.png
│   └── character2.png
├── locations/           # Location images
│   ├── location1.png
│   └── location2.png
├── panels/              # Generated comic panels
│   ├── panel_0.png
│   ├── panel_1.png
│   └── ...
├── characters.json      # Character metadata
└── locations.json       # Location metadata
```

## Technical Details

### Image Generation

The system uses Google's Gemini 2.5 Flash Image Preview model for image generation with the following approach:

1. **Character Generation**: Creates consistent character portraits with detailed visual traits
2. **Location Generation**: Creates establishing shots for locations
3. **Panel Composition**: Combines characters and locations into cohesive comic panels

### Asset Management

- **Persistent Storage**: All assets are saved to disk and reused across sessions
- **Validation**: Image files are validated before use
- **Fallback**: Placeholder images are generated if actual generation fails

### AI Prompts

The system uses carefully crafted prompts to ensure:

- Consistent manhwa/webtoon style
- Character consistency across panels
- Proper composition and framing
- High-quality output

## Limitations

- Requires Google Gemini API access
- Image generation quality depends on AI model performance
- Processing time scales with chapter length and complexity
- Character consistency relies on AI model understanding

## Future Enhancements

- **Advanced Composition**: Manual image composition using PIL/OpenCV
- **Style Transfer**: Apply consistent art styles across all generated images
- **Batch Processing**: Process multiple chapters in parallel
- **Web Interface**: GUI for easier chapter input and panel management
- **Export Options**: PDF, webtoon format, or other comic formats

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
