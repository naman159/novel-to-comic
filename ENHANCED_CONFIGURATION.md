# Enhanced Novel to Comic Generator - Configuration Guide

## Environment Variables Setup

To use the enhanced features, set these environment variables in your `.env` file or system environment:

### Required Google Cloud Configuration

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id-here"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_CLOUD_SA_PATH="sa-key.json"
```

### Enhanced Features Configuration

#### 1. Redundancy Detection

```bash
# Enable/disable redundancy detection
export ENABLE_REDUNDANCY_DETECTION="true"

# Similarity threshold (0.0 = strict, 1.0 = lenient)
export PANEL_SIMILARITY_THRESHOLD="0.7"
```

#### 2. Continuity Tracking

```bash
# Enable/disable continuity tracking
export ENABLE_CONTINUITY_TRACKING="true"
```

#### 3. Panel Optimization

```bash
# Maximum panels per scene
export MAX_PANELS_PER_SCENE="4"

# Minimum panels per scene
export MIN_PANELS_PER_SCENE="2"
```

#### 4. Image Generation

```bash
# Image quality: high, medium, low
export IMAGE_QUALITY="high"

# Art style: manhwa, manga, western, realistic
export IMAGE_STYLE="manhwa"
```

#### 5. AI Model Selection

```bash
# Scene analysis model
export SCENE_ANALYSIS_MODEL="gemini-2.5-flash"

# Entity extraction model
export ENTITY_EXTRACTION_MODEL="gemini-2.5-flash"

# Image generation model
export IMAGE_GENERATION_MODEL="gemini-2.5-flash-image-preview"
```

#### 6. Output Configuration

```bash
# Default output directory
export DEFAULT_OUTPUT_DIR="comic_output"

# Panel naming convention: sequential, descriptive, timestamped
export PANEL_NAMING_CONVENTION="sequential"

# Enable metadata export
export ENABLE_METADATA_EXPORT="true"
```

## Complete .env File Example

Create a `.env` file in your project root with:

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id-here
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_CLOUD_SA_PATH=sa-key.json

# Enhanced Features
ENABLE_REDUNDANCY_DETECTION=true
PANEL_SIMILARITY_THRESHOLD=0.7
ENABLE_CONTINUITY_TRACKING=true
MAX_PANELS_PER_SCENE=4
MIN_PANELS_PER_SCENE=2

# Image Generation
IMAGE_QUALITY=high
IMAGE_STYLE=manhwa

# AI Models
SCENE_ANALYSIS_MODEL=gemini-2.5-flash
ENTITY_EXTRACTION_MODEL=gemini-2.5-flash
IMAGE_GENERATION_MODEL=gemini-2.5-flash-image-preview

# Output
DEFAULT_OUTPUT_DIR=comic_output
PANEL_NAMING_CONVENTION=sequential
ENABLE_METADATA_EXPORT=true
```

## Feature Tuning Guide

### Redundancy Detection Tuning

#### Strict Detection (Fewer Similar Panels)

```bash
export PANEL_SIMILARITY_THRESHOLD="0.5"
```

- **Use when**: You want maximum visual variety
- **Result**: More diverse panels, potentially more panels generated
- **Trade-off**: May slow down generation due to regeneration attempts

#### Lenient Detection (More Similar Panels Allowed)

```bash
export PANEL_SIMILARITY_THRESHOLD="0.8"
```

- **Use when**: You want faster generation
- **Result**: Faster generation, some similar panels allowed
- **Trade-off**: Less visual variety

### Panel Count Optimization

#### Action-Heavy Stories

```bash
export MAX_PANELS_PER_SCENE="5"
export MIN_PANELS_PER_SCENE="3"
```

- **Best for**: Action, adventure, fast-paced stories
- **Result**: More panels to show action sequences

#### Dialogue-Heavy Stories

```bash
export MAX_PANELS_PER_SCENE="3"
export MIN_PANELS_PER_SCENE="2"
```

- **Best for**: Character development, conversations, emotional scenes
- **Result**: Fewer panels, focus on character expressions

#### Balanced Stories

```bash
export MAX_PANELS_PER_SCENE="4"
export MIN_PANELS_PER_SCENE="2"
```

- **Best for**: General fiction, balanced pacing
- **Result**: Flexible panel count based on scene complexity

### Art Style Configuration

#### Manhwa Style (Default)

```bash
export IMAGE_STYLE="manhwa"
```

- **Characteristics**: Clean lines, vibrant colors, modern webtoon style
- **Best for**: Contemporary stories, action, romance

#### Manga Style

```bash
export IMAGE_STYLE="manga"
```

- **Characteristics**: Detailed linework, dramatic shadows, traditional manga aesthetic
- **Best for**: Fantasy, adventure, dramatic stories

#### Western Style

```bash
export IMAGE_STYLE="western"
```

- **Characteristics**: Bold colors, dynamic poses, comic book style
- **Best for**: Superhero, action, adventure stories

#### Realistic Style

```bash
export IMAGE_STYLE="realistic"
```

- **Characteristics**: Photorealistic, detailed textures, natural lighting
- **Best for**: Historical fiction, realistic drama, nature stories

## Performance Optimization

### For Faster Generation

```bash
export IMAGE_QUALITY="medium"
export ENABLE_REDUNDANCY_DETECTION="false"
export MAX_PANELS_PER_SCENE="3"
```

### For Higher Quality

```bash
export IMAGE_QUALITY="high"
export ENABLE_REDUNDANCY_DETECTION="true"
export PANEL_SIMILARITY_THRESHOLD="0.6"
```

### For Maximum Consistency

```bash
export ENABLE_CONTINUITY_TRACKING="true"
export ENABLE_REDUNDANCY_DETECTION="true"
export PANEL_SIMILARITY_THRESHOLD="0.5"
export IMAGE_STYLE="manhwa"
```

## Troubleshooting

### Common Issues

#### 1. Redundancy Detection Too Strict

**Symptoms**: Generation takes too long, many regeneration attempts
**Solution**: Increase threshold

```bash
export PANEL_SIMILARITY_THRESHOLD="0.8"
```

#### 2. Too Many Panels Generated

**Symptoms**: Excessive panels, slow reading pace
**Solution**: Reduce maximum panels

```bash
export MAX_PANELS_PER_SCENE="3"
```

#### 3. Inconsistent Art Style

**Symptoms**: Panels look different from each other
**Solution**: Ensure consistent style setting

```bash
export IMAGE_STYLE="manhwa"
export IMAGE_QUALITY="high"
```

#### 4. Continuity Issues

**Symptoms**: Scenes don't flow naturally
**Solution**: Enable continuity tracking

```bash
export ENABLE_CONTINUITY_TRACKING="true"
```

### Testing Configuration

Test your configuration with a short chapter first:

```python
from main import EnhancedNovelToComic

# Test with minimal output
comic_generator = EnhancedNovelToComic(output_dir="test_output")

# Use a short chapter for testing
test_chapter = "A brief test chapter with minimal content."
panel_paths = comic_generator.process_chapter(test_chapter)
```

## Advanced Configuration

### Custom Redundancy Weights

Modify `config.py` to adjust redundancy detection sensitivity:

```python
# In config.py, modify ComicConfig class
redundancy_weights = {
    "location": 0.4,        # Increase location importance
    "characters": 0.3,      # Standard character weight
    "panel_type": 0.2,      # Standard panel type weight
    "camera_angle": 0.1     # Reduce camera angle importance
}
```

### Custom Panel Type Optimization

```python
# In config.py, modify ComicConfig class
optimal_panels_by_scene_type = {
    "establishing": 1,       # Single establishing panel
    "action": 4,             # More action panels
    "dialogue": 3,           # More dialogue panels
    "transition": 1,         # Single transition panel
    "climax": 5,             # Maximum climax panels
}
```

## Monitoring and Debugging

### Enable Debug Output

```bash
export DEBUG_MODE="true"
export LOG_LEVEL="DEBUG"
```

### Check Feature Status

The enhanced generator will show feature status during processing:

```
🎭 Enhanced Features Summary:
   - Scenes processed: 4
   - Continuity tracking: ✅ Enabled
   - Redundancy detection: ✅ Enabled
   - Panel optimization: ✅ Enabled
```

This configuration guide helps you customize the enhanced novel-to-comic generator for your specific needs and story types.
