# Novel to Comic Generator (NTC)

A Python application that converts novel chapters into manhwa-style comics using Google's Gemini 2.5 Flash models on Vertex AI. It persistently manages characters and locations and composes panels by combining character assets with character-free location backgrounds.

## Features

- **Entity extraction**: Identifies characters and locations from chapter text
- **Consistent assets**: Generates and reuses character portraits and location backgrounds
- **Continuity-aware scenes**: Narrative structure analysis and continuity tracking across scenes
- **Panel direction**: Varying panel types and camera angles per scene
- **Asset composition**: Combines separate character and location images for final panels
- **Graceful fallback**: Generates placeholders when the API is unavailable or image generation fails

## Requirements

- Python 3.11+
- Google Cloud project with Vertex AI enabled
- Service account with Vertex AI permissions and a JSON key file

## Installation

```bash
pip install -e .
```

Optionally use a virtual environment.

## Setup (Vertex AI)

This project uses `google-genai` in Vertex AI mode with a service account.

Set the following environment variables (a `.env` file is supported):

```bash
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"        # or "global" (default)
export GOOGLE_CLOUD_SA_PATH="/absolute/path/to/your-sa-key.json"
```

Ensure Vertex AI is enabled in your project and the service account has appropriate permissions.

## Quick Start

```python
from main import EnhancedNovelToComic

chapter_text = """
Chapter 1: The Beginning

Sarah stood at the edge of the ancient forest, her heart pounding with anticipation...
"""

comic = EnhancedNovelToComic(output_dir="my_comic")
panel_paths = comic.process_chapter(chapter_text)

print(f"Generated {len(panel_paths)} panels:")
for i, path in enumerate(panel_paths, start=1):
    print(f"  Panel {i}: {path}")
```

See `example.py` for a longer runnable example and richer output.

## Project Structure

```
ntc/
├── main.py              # Core pipeline and data classes
├── image_utils.py       # Vertex AI image generation, composition, placeholders
├── config.py            # Pydantic settings for environment configuration
├── example.py           # End-to-end example script
├── ARCHITECTURE.md      # Deep-dive into the system
├── README.md            # This file
└── comic_output/        # Generated assets (created at runtime)
    ├── characters/      # Character images
    ├── locations/       # Location images (no characters)
    ├── panels/          # Final composed comic panels
    ├── characters.json  # Character metadata
    └── locations.json   # Location metadata
```

## API Reference

### Class

```python
class EnhancedNovelToComic:
    def __init__(self, output_dir: str = "comic_output"): ...
```

### Pipeline methods

- `extract_entities(chapter: str) -> Tuple[List[Character], List[Location]]`
  - Uses Gemini to extract characters and locations with rich metadata
- `generate_character_image(character: Character) -> str`
  - Generates/updates a consistent character image and returns its path
- `generate_location_image(location: Location) -> str`
  - Generates a character-free background image and returns its path
- `analyze_narrative_structure(chapter: str) -> Dict[str, Any]`
  - Determines scene counts, types, flow, and target panel counts
- `split_scenes_with_continuity(chapter: str) -> List[Scene]`
  - Breaks chapter into scenes, preserving continuity links
- `direct_panels_with_continuity(scene_description: str, characters: List[str], location: str, scene_type: str, narrative_flow: str, target_panels: int) -> List[Panel]`
  - Directs panels with panel type and camera angle variety
- `fetch_assets(panel: Panel) -> Dict[str, str]`
  - Ensures required images exist (generates or falls back) and returns asset paths
- `generate_panel_image(panel: Panel, assets: Dict[str, str]) -> str`
  - Composes the final panel by combining character and location images
- `process_chapter(chapter: str) -> List[str]`
  - Runs the full pipeline and returns generated panel image paths
- `test_asset_generation() -> bool`
  - Utility for verifying character/location generation and validation

### Data classes

```python
@dataclass
class Character:
    name: str
    description: str
    visual_traits: str
    image_path: Optional[str] = None
    last_seen_scene: Optional[str] = None

@dataclass
class Location:
    name: str
    description: str
    image_path: Optional[str] = None
    parent_location: Optional[str] = None
    transition_type: Optional[str] = None  # "interior" | "exterior" | "transitional"

@dataclass
class Scene:
    content: str
    characters: List[str]
    location: str
    scene_type: str
    narrative_flow: str
    estimated_panels: int
    previous_scene: Optional[str] = None
    next_scene: Optional[str] = None

@dataclass
class Panel:
    description: str
    characters: List[str]
    location: str
    composition_prompt: str
    panel_type: str
    camera_angle: str

@dataclass
class NarrativeFlow:
    current_scene: Optional[str] = None
    scene_sequence: List[str] = None
    location_transitions: List[Tuple[str, str, str]] = None
    character_arcs: Dict[str, List[str]] = None
    panel_count_optimization: Dict[str, int] = None
```

## Configuration

Configured via environment variables (supports `.env`):

- `GOOGLE_CLOUD_PROJECT` (required)
- `GOOGLE_CLOUD_LOCATION` (default: `global`)
- `GOOGLE_CLOUD_SA_PATH` (required; absolute path recommended)

## Technical Details

- **Libraries**: `google-genai` (Vertex AI mode), `Pillow`, `pydantic-settings`, `python-dotenv`
- **Models**:
  - Text/planning: `gemini-2.5-flash`
  - Image generation: `gemini-2.5-flash-image-preview` (streaming)
- **Location safety**: Prompts are sanitized to enforce character-free backgrounds
- **Validation**: Generated files are verified before reuse; placeholders are created on failure

## Troubleshooting

- Ensure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_SA_PATH` are set and the SA key file exists
- Verify Vertex AI API is enabled and the service account has permissions
- If generation fails or no client is available, placeholders will be created in the output directories

## License

MIT
