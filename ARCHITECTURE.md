# Novel to Comic Generator - Architecture Document

## Overview

The Novel to Comic Generator (NTC) is a Python application that converts novel chapters into manhwa-style comics using Google's Gemini 2.5 Flash AI models. The system maintains character and location consistency across panels and chapters through intelligent asset management.

## Core Architecture

### 1. Entity Management System

The system uses a persistent asset management approach to ensure consistency:

#### Character Registry

- **Purpose**: Maintains consistent character appearances across all panels
- **Storage**: JSON metadata + PNG image files
- **Key Features**:
  - Visual traits extraction from text
  - Consistent image generation using detailed prompts
  - Reuse of character assets across scenes and chapters

#### Location Registry

- **Purpose**: Maintains consistent location backgrounds
- **Storage**: JSON metadata + PNG image files
- **Key Features**:
  - Location description extraction
  - Establishing shot generation
  - Reuse of location assets across scenes

#### Asset Database

- **Format**: JSON files (`characters.json`, `locations.json`)
- **Structure**: Maps entity names to metadata and file paths
- **Persistence**: Survives across sessions and chapters

### 2. Chapter Processing Pipeline

The pipeline follows a structured approach to convert text to visual panels:

```
Novel Chapter → Entity Extraction → Asset Generation → Scene Segmentation → Panel Planning → Image Composition → Comic Panels
```

#### Step 1: Entity Extraction

- **Input**: Raw chapter text
- **Process**: AI analyzes text to identify characters and locations
- **Output**: Structured Character and Location objects
- **AI Prompt**: Detailed prompt for consistent entity identification

#### Step 2: Asset Generation

- **Input**: Character/Location descriptions
- **Process**: Generate consistent images using Gemini 2.5 Flash
- **Output**: PNG image files with metadata
- **Consistency**: Detailed prompts ensure visual consistency

#### Step 3: Scene Segmentation

- **Input**: Chapter text
- **Process**: AI breaks chapter into logical scenes
- **Output**: List of Scene objects with content and metadata
- **Logic**: Each scene is a self-contained narrative unit

#### Step 4: Panel Planning

- **Input**: Scene descriptions
- **Process**: AI creates 2-4 panels per scene
- **Output**: Panel objects with composition details
- **Strategy**: Each panel advances the story visually

#### Step 5: Image Composition

- **Input**: Panel descriptions + asset references
- **Process**: Compose final panel images using assets
- **Output**: Comic panel PNG files
- **Technique**: Gemini 2.5 Flash with asset-aware prompts

### 3. Asset Consistency Strategy

#### Character Consistency

- **Base Generation**: Create character portraits with detailed visual traits
- **Reuse Strategy**: Reference existing character images in panel prompts
- **Prompt Engineering**: Include character names and consistent descriptions
- **Fallback**: Placeholder images when generation fails

#### Location Consistency

- **Base Generation**: Create establishing shots for locations
- **Reuse Strategy**: Reference existing location images in panel prompts
- **Prompt Engineering**: Include location names and consistent descriptions
- **Fallback**: Placeholder images when generation fails

#### Composition Engine

- **Asset Integration**: Combine character and location references
- **Style Consistency**: Maintain manhwa/webtoon style across all images
- **Quality Control**: Validation and fallback mechanisms

## Technical Implementation

### Data Structures

#### Character

```python
@dataclass
class Character:
    name: str                    # Character name
    description: str             # Brief character description
    visual_traits: str           # Detailed visual description
    image_path: Optional[str]    # Path to generated image
```

#### Location

```python
@dataclass
class Location:
    name: str                    # Location name
    description: str             # Brief location description
    image_path: Optional[str]    # Path to generated image
```

#### Scene

```python
@dataclass
class Scene:
    content: str                 # Scene text content
    characters: List[str]        # Characters present in scene
    location: str                # Scene location
    panels: List[str]            # Panel descriptions
```

#### Panel

```python
@dataclass
class Panel:
    description: str             # What happens in the panel
    characters: List[str]        # Characters in panel
    location: str                # Panel location
    composition_prompt: str      # Detailed image generation prompt
```

### File Organization

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

### AI Integration

#### Gemini 2.5 Flash Usage

- **Entity Extraction**: Text analysis for character/location identification using `gemini-2.5-flash`
- **Scene Segmentation**: Breaking chapters into logical scenes using `gemini-2.5-flash`
- **Panel Planning**: Creating panel descriptions and composition prompts using `gemini-2.5-flash`
- **Image Generation**: Generating character, location, and panel images using `gemini-2.5-flash-image-preview`

#### Prompt Engineering Strategy

- **Consistency**: Detailed prompts ensure visual consistency
- **Style**: Manhwa/webtoon style specifications
- **Composition**: Camera angles, framing, and visual flow
- **Asset References**: Include existing asset information in prompts

### Error Handling & Fallbacks

#### API Unavailability

- **Detection**: Check for API key and client availability
- **Fallback**: Generate placeholder images and metadata
- **Graceful Degradation**: System continues to work without API

#### Image Generation Failures

- **Validation**: Check if generated images are valid
- **Retry Logic**: Attempt regeneration if needed
- **Placeholder Creation**: Create informative placeholder images

#### Asset Management

- **Validation**: Verify image files exist and are valid
- **Regeneration**: Recreate missing or corrupted assets
- **Persistence**: Save and load asset metadata

## Usage Patterns

### Basic Usage

```python
from main import NovelToComic

# Initialize generator
comic_generator = NovelToComic(output_dir="my_comic")

# Process chapter
panel_paths = comic_generator.process_chapter(chapter_text)
```

### Advanced Usage

```python
# Custom output directory
comic_generator = NovelToComic(output_dir="custom_output")

# Process multiple chapters
for chapter in chapters:
    panel_paths = comic_generator.process_chapter(chapter)
```

### Asset Reuse

- **Cross-Chapter**: Characters and locations persist across chapters
- **Incremental**: Only generate new assets when needed
- **Consistency**: Maintain visual consistency throughout the story

## Performance Considerations

### Caching Strategy

- **Asset Caching**: Reuse generated character and location images
- **Metadata Persistence**: Save entity information to JSON files
- **Validation**: Check asset validity before reuse

### API Efficiency

- **Batch Processing**: Process multiple panels efficiently
- **Error Recovery**: Handle API failures gracefully
- **Rate Limiting**: Respect API rate limits

### Storage Optimization

- **Image Compression**: Optimize PNG file sizes
- **Metadata Efficiency**: Compact JSON storage
- **Directory Structure**: Organized file management

## Future Enhancements

### Advanced Composition

- **Manual Composition**: Use PIL/OpenCV for precise asset placement
- **Style Transfer**: Apply consistent art styles across all images
- **Layout Engine**: Intelligent panel layout and composition

### Performance Improvements

- **Parallel Processing**: Generate multiple panels simultaneously
- **Caching Layer**: Redis or database for asset caching
- **CDN Integration**: Cloud storage for generated assets

### User Experience

- **Web Interface**: GUI for easier chapter input and management
- **Real-time Preview**: Live preview of generated panels
- **Export Options**: PDF, webtoon format, or other comic formats

### AI Enhancements

- **Fine-tuning**: Custom model training for specific styles
- **Multi-modal**: Support for audio and video generation
- **Interactive**: Real-time editing and refinement

## Conclusion

The Novel to Comic Generator provides a comprehensive solution for converting novels to comics while maintaining visual consistency. The architecture ensures that characters and locations remain recognizable across panels and chapters, creating a cohesive visual narrative.

The system is designed to be:

- **Scalable**: Handle multiple chapters and complex stories
- **Consistent**: Maintain visual consistency throughout
- **Robust**: Handle errors and API failures gracefully
- **Extensible**: Easy to add new features and enhancements

This architecture provides a solid foundation for AI-powered comic generation with the potential for significant enhancements in the future.
