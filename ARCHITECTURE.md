# Novel to Comic Generator - Architecture Document

## Overview

The Novel to Comic Generator (NTC) converts novel chapters into manhwa-style comics using Gemini 2.5 Flash on Vertex AI. It persistently manages assets and composes panels by combining separate character and location images to maintain visual consistency and narrative continuity.

## Core Architecture

### 1. Entity Management System

The system uses persistent on-disk assets and JSON registries to ensure consistency across runs:

#### Character Registry

- **Purpose**: Maintain consistent character appearances across panels and chapters
- **Storage**: `characters/` PNG files + `characters.json` metadata
- **Captured fields**: `name`, `description`, `visual_traits`, `image_path`, `last_seen_scene`

#### Location Registry

- **Purpose**: Maintain consistent location backgrounds (character-free)
- **Storage**: `locations/` PNG files + `locations.json` metadata
- **Captured fields**: `name`, `description`, `image_path`, `parent_location`, `transition_type`

#### Asset Database

- **Format**: JSON lists in `characters.json` and `locations.json`
- **Lifecycle**: Loaded at startup; saved after asset updates; reused across sessions

### 2. Chapter Processing Pipeline

High-level flow:

```
Novel Chapter → Entity Extraction → Asset Generation → Narrative Analysis → Scene Split (with continuity) → Panel Direction → Asset Fetch → Panel Composition → Comic Panels
```

- **Entity Extraction**: Extracts characters and locations with rich metadata
- **Asset Generation**: Generates or reuses character and location images
- **Narrative Analysis**: Determines scene types, flow, and optimal panel counts
- **Scene Split (Continuity)**: Builds scenes with `previous_scene`/`next_scene` references
- **Panel Direction**: Produces panel descriptions, panel types, and camera angles
- **Asset Fetch**: Ensures required images exist, generating or falling back as needed
- **Panel Composition**: Composes final panels using provided images and prompts

### 3. Asset Consistency & Safety

- **Character Consistency**: Reuses generated character portraits; tracks `last_seen_scene`
- **Location Safety**: Prompts are sanitized to enforce character-free backgrounds
- **Validation**: Image files are verified before reuse; placeholder images on failure

## Technical Implementation

### Data Structures

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

### Key Modules

- `main.py`: Enhanced pipeline (`EnhancedNovelToComic`) and data classes
- `image_utils.py`: Vertex AI clients, image generation, panel composition, placeholders, validation
- `config.py`: Pydantic-based settings loading from environment or `.env`

### AI Integration

- **Text/Planning**: `gemini-2.5-flash`
  - Entity extraction, narrative analysis, scene splitting, panel direction
- **Image Generation**: `gemini-2.5-flash-image-preview` (streaming)
  - Character portraits, location backgrounds, and final panel composition
- **Client**: `google-genai` in Vertex AI mode using service account credentials

### Error Handling & Fallbacks

- **Client Unavailable**: Uses informative placeholder entities/scenes/panels and placeholder images
- **Image Failures**: Writes placeholder images; continues pipeline gracefully
- **Validation**: Checks file existence and integrity before reuse
- **Location Safety**: Sanitizes background prompts to ensure no characters are embedded in location images

## Operational Details

### Environment Variables

- `GOOGLE_CLOUD_PROJECT` (required)
- `GOOGLE_CLOUD_LOCATION` (default: `global`)
- `GOOGLE_CLOUD_SA_PATH` (required; absolute path recommended)

### Output Directory Structure

```
output_dir/
├── characters/
├── locations/
├── panels/
├── characters.json
└── locations.json
```

## Usage

```python
from main import EnhancedNovelToComic

comic = EnhancedNovelToComic(output_dir="comic_output")
panel_paths = comic.process_chapter(chapter_text)
```

## Future Enhancements

- Manual composition improvements (PIL/OpenCV) for precise layout
- Parallel generation for throughput
- Style controls and transfer for consistent art direction
- Web UI and export formats (PDF, webtoon)

## Conclusion

NTC provides an end-to-end, continuity-aware pipeline for turning prose into comics while preserving character and location consistency. It integrates with Vertex AI via `google-genai` and is resilient to failures through placeholder strategies and validation steps.
