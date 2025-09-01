#!/usr/bin/env python3
"""
Enhanced Novel to Comic Generator

This module provides functionality to convert novel chapters into manhwa-style comics
using AI-generated images and scene composition with improved continuity and consistency.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from google import genai
from google.oauth2 import service_account
from config import Secrets
from image_utils import (
    generate_image_with_gemini,
    compose_panel_with_assets,
    validate_image_path,
)

secrets = Secrets()


def clean_json_response(text: str) -> str:
    """
    Clean common JSON formatting issues from AI model responses.
    """
    # Remove markdown code blocks
    if text.startswith("```json"):
        text = text[7:]  # Remove ```json
    if text.endswith("```"):
        text = text[:-3]  # Remove ```

    text = text.strip()

    # Fix trailing commas before closing brackets/braces
    text = re.sub(r",(\s*[}\]])", r"\1", text)

    # Fix trailing commas before closing parentheses
    text = re.sub(r",(\s*\))", r"\1", text)

    # Remove any trailing commas at the end of the text
    text = re.sub(r",\s*$", "", text)

    return text


def validate_location_image_prompt(prompt: str) -> str:
    """
    Ensure location image prompts don't include character generation.
    """
    # Keywords that indicate character presence
    character_keywords = [
        "character",
        "person",
        "people",
        "human",
        "figure",
        "silhouette",
        "someone",
        "anyone",
        "crowd",
        "passerby",
        "occupant",
        "resident",
    ]

    # Check if prompt contains character-related keywords
    prompt_lower = prompt.lower()
    for keyword in character_keywords:
        if keyword in prompt_lower:
            # Remove or replace character-related content
            prompt = prompt.replace(keyword, "environment")
            prompt = prompt.replace("people", "architecture")
            prompt = prompt.replace("figures", "structures")

    # Add explicit instruction if not already present
    if "NO characters" not in prompt and "NO people" not in prompt:
        prompt += "\n\nCRITICAL: Generate ONLY the environment/background with NO characters, people, or living beings."

    return prompt


# Initialize Vertex AI client
def init_vertexai_client():
    """Initialize Vertex AI client using google-genai."""
    try:
        project = secrets.GOOGLE_CLOUD_PROJECT or "nove-470619"
        location = secrets.GOOGLE_CLOUD_LOCATION
        print(f"Project: {project}")

        credentials = service_account.Credentials.from_service_account_file(
            secrets.GOOGLE_CLOUD_SA_PATH,
            scopes=[
                "https://www.googleapis.com/auth/generative-language",
                "https://www.googleapis.com/auth/cloud-platform",
            ],
        )

        client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
            credentials=credentials,
        )
        return client
    except Exception as e:
        print(f"Failed to initialize Vertex AI client: {e}")
        return None


# Initialize Vertex AI client
client = init_vertexai_client()


@dataclass
class Character:
    name: str
    description: str
    visual_traits: str
    image_path: Optional[str] = None
    last_seen_scene: Optional[str] = None  # Track where character was last seen


@dataclass
class Location:
    name: str
    description: str
    image_path: Optional[str] = None
    parent_location: Optional[str] = (
        None  # For location hierarchy (e.g., "room" within "building")
    )
    transition_type: Optional[str] = None  # "interior", "exterior", "transitional"


@dataclass
class Scene:
    content: str
    characters: List[str]
    location: str
    scene_type: str  # "establishing", "action", "dialogue", "transition", "climax"
    narrative_flow: str  # "setup", "conflict", "resolution", "transition"
    estimated_panels: int  # AI-estimated optimal panel count
    previous_scene: Optional[str] = None  # For continuity tracking
    next_scene: Optional[str] = None  # For continuity tracking


@dataclass
class Panel:
    description: str
    characters: List[str]
    location: str
    composition_prompt: str
    panel_type: str  # "establishing", "action", "reaction", "transition"
    camera_angle: str  # "wide", "medium", "close", "bird_eye", "worm_eye"
    redundancy_score: float = 0.0  # How similar to previous panels


@dataclass
class NarrativeFlow:
    """Tracks the narrative progression and ensures continuity"""

    current_scene: Optional[str] = None
    scene_sequence: List[str] = None
    location_transitions: List[Tuple[str, str, str]] = (
        None  # (from, to, transition_type)
    )
    character_arcs: Dict[str, List[str]] = None  # Character development tracking
    panel_count_optimization: Dict[str, int] = None  # Optimal panels per scene type

    def __post_init__(self):
        if self.scene_sequence is None:
            self.scene_sequence = []
        if self.location_transitions is None:
            self.location_transitions = []
        if self.character_arcs is None:
            self.character_arcs = {}
        if self.panel_count_optimization is None:
            self.panel_count_optimization = {}


class EnhancedNovelToComic:
    def __init__(self, output_dir: str = "comic_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Asset directories
        self.characters_dir = self.output_dir / "characters"
        self.locations_dir = self.output_dir / "locations"
        self.panels_dir = self.output_dir / "panels"

        for dir_path in [self.characters_dir, self.locations_dir, self.panels_dir]:
            dir_path.mkdir(exist_ok=True)

        # Asset registries
        self.characters: Dict[str, Character] = {}
        self.locations: Dict[str, Location] = {}

        # Narrative flow tracking
        self.narrative_flow = NarrativeFlow()

        # Panel redundancy detection
        self.generated_panels: List[Panel] = []
        self.panel_similarity_threshold = 0.7

        # Load existing assets
        self._load_assets()

    def _load_assets(self):
        """Load existing character and location assets from disk"""
        # Load characters
        char_file = self.output_dir / "characters.json"
        if char_file.exists():
            with open(char_file, "r") as f:
                char_data = json.load(f)
                for char_dict in char_data:
                    char = Character(**char_dict)
                    self.characters[char.name] = char

        # Load locations
        loc_file = self.output_dir / "locations.json"
        if loc_file.exists():
            with open(loc_file, "r") as f:
                loc_data = json.load(f)
                for loc_dict in loc_data:
                    loc = Location(**loc_dict)
                    self.locations[loc.name] = loc

    def _save_assets(self):
        """Save character and location assets to disk"""
        # Save characters
        with open(self.output_dir / "characters.json", "w") as f:
            json.dump([asdict(char) for char in self.characters.values()], f, indent=2)

        # Save locations
        with open(self.output_dir / "locations.json", "w") as f:
            json.dump([asdict(loc) for loc in self.locations.values()], f, indent=2)

    def _sanitize_filename(self, name: str) -> str:
        """Sanitize a string to be used as a filename by replacing invalid characters."""
        invalid_chars = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]
        safe_name = name.lower().replace(" ", "_")
        for char in invalid_chars:
            safe_name = safe_name.replace(char, "_")
        return safe_name

    def extract_entities(self, chapter: str) -> Tuple[List[Character], List[Location]]:
        """
        Extract characters and locations from the chapter using AI with enhanced analysis.
        Returns lists of Character and Location objects.
        """
        if client is None:
            print(
                "Warning: Vertex AI client not available. Using placeholder entities."
            )
            # Create placeholder entities for testing
            characters = [
                Character(
                    name="Main Character",
                    description="The protagonist of the story",
                    visual_traits="Generic appearance for testing",
                )
            ]
            locations = [
                Location(
                    name="Story Location",
                    description="The main setting of the story",
                    transition_type="interior",
                )
            ]

            for char in characters:
                self.characters[char.name] = char
            for loc in locations:
                self.locations[loc.name] = loc

            self._save_assets()
            return characters, locations

        prompt = f"""
        Analyze this novel chapter and extract all characters and locations with enhanced context.
        
        Chapter:
        {chapter}
        
        For each character, provide:
        - name: character's name
        - description: brief character description
        - visual_traits: detailed visual description for consistent image generation
        
        For each location, provide:
        - name: location name
        - description: brief location description
        - parent_location: if this is a sub-location (e.g., "room" within "building"), otherwise null
        - transition_type: "interior", "exterior", or "transitional" (like corridors, doorways)
        
        Return as JSON:
        {{
            "characters": [
                {{"name": "...", "description": "...", "visual_traits": "..."}}
            ],
            "locations": [
                {{"name": "...", "description": "...", "parent_location": "...", "transition_type": "..."}}
            ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        print(f"Response text: {response.text}")
        print(f"Response type: {type(response)}")
        print(f"Response has text: {hasattr(response, 'text')}")

        # Clean and parse JSON response
        text = clean_json_response(response.text)

        try:
            entities = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response text: {text[:200]}...")
            # Fallback to placeholder entities
            return [
                Character(
                    name="Main Character",
                    description="The protagonist of the story",
                    visual_traits="Generic appearance for testing",
                )
            ], [
                Location(
                    name="Story Location",
                    description="The main setting of the story",
                    transition_type="interior",
                )
            ]

        # Create Character and Location objects
        characters = []
        for char_data in entities["characters"]:
            char = Character(**char_data)
            characters.append(char)
            self.characters[char.name] = char

        locations = []
        for loc_data in entities["locations"]:
            loc = Location(**loc_data)
            locations.append(loc)
            self.locations[loc.name] = loc

        self._save_assets()
        return characters, locations

    def generate_character_image(self, character: Character) -> str:
        """Generate a consistent character image using Gemini 2.5 Flash"""
        prompt = f"""
        Create a character portrait with these specifications:
        
        Character: {character.name}
        Description: {character.description}
        Visual Traits: {character.visual_traits}
        
        Style: Modern manhwa/webtoon/comic style, clean lines, vibrant colors
        Pose: Neutral standing pose, full body shot
        Background: Simple, clean background
        Quality: High resolution, detailed but not overly complex
        """

        # Save the generated image
        safe_filename = self._sanitize_filename(character.name)
        image_path = self.characters_dir / f"{safe_filename}.png"

        # Generate the image using our utility function
        success = generate_image_with_gemini(prompt, image_path)

        # Always set the image path, even if generation failed (placeholder will be created)
        character.image_path = str(image_path)
        self._save_assets()

        return str(image_path)

    def generate_location_image(self, location: Location) -> str:
        """Generate a consistent location image using Gemini 2.5 Flash"""
        prompt = f"""
        Create a location/background with these specifications:
        
        Location: {location.name}
        Description: {location.description}
        Type: {location.transition_type or 'interior'}
        
        Style: Modern manhwa/webtoon style, clean lines, vibrant colors
        Perspective: Wide establishing shot
        Quality: High resolution, detailed but not overly complex
        
        IMPORTANT: This should be a PURE BACKGROUND/LOCATION image with NO characters, 
        people, or living beings. Only show the environment, architecture, landscape, 
        or setting. Characters will be added separately during panel composition.
        """

        # Validate and clean the prompt to ensure no character generation
        prompt = validate_location_image_prompt(prompt)

        # Save the generated image
        safe_filename = self._sanitize_filename(location.name)
        image_path = self.locations_dir / f"{safe_filename}.png"

        # Generate the image using our utility function
        success = generate_image_with_gemini(prompt, image_path)

        # Always set the image path, even if generation failed (placeholder will be created)
        location.image_path = str(image_path)
        self._save_assets()

        return str(image_path)

    def validate_location_asset(self, image_path: str) -> bool:
        """
        Validate that a location image doesn't contain characters.
        This is a basic check - in production you might want to use AI vision analysis.
        """
        # For now, we'll rely on the prompt validation
        # In the future, you could add AI vision analysis here to detect if characters are present
        return True

    def analyze_narrative_structure(self, chapter: str) -> Dict[str, str]:
        """
        Analyze the chapter's narrative structure to determine optimal scene and panel distribution.
        """
        if client is None:
            return {
                "total_scenes": 3,
                "scene_types": ["establishing", "action", "resolution"],
                "narrative_flow": ["setup", "conflict", "resolution"],
                "optimal_panels_per_scene": [2, 3, 2],
            }

        prompt = f"""
        Analyze this novel chapter's narrative structure to determine optimal comic adaptation.
        
        Chapter:
        {chapter}
        
        Analyze and provide:
        1. Total number of distinct scenes needed
        2. Type of each scene (establishing, action, dialogue, transition, climax)
        3. Narrative flow progression (setup, conflict, rising_action, climax, resolution, transition)
        4. Optimal number of panels for each scene (considering story complexity and visual impact)
        
        Return as JSON:
        {{
            "total_scenes": 3,
            "scene_types": ["establishing", "action", "resolution"],
            "narrative_flow": ["setup", "conflict", "resolution"],
            "optimal_panels_per_scene": [2, 3, 2],
            "scene_descriptions": ["Brief description of each scene"],
            "continuity_notes": ["Important continuity elements to maintain"]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Clean and parse JSON response
        text = clean_json_response(response.text)

        try:
            structure = json.loads(text)
            return structure
        except json.JSONDecodeError as e:
            print(f"Error parsing narrative structure: {e}")
            print(f"Raw response text: {text[:200]}...")
            # Fallback to default structure
            return {
                "total_scenes": 3,
                "scene_types": ["establishing", "action", "resolution"],
                "narrative_flow": ["setup", "conflict", "resolution"],
                "optimal_panels_per_scene": [2, 3, 2],
            }

    def split_scenes_with_continuity(self, chapter: str) -> List[Scene]:
        """
        Split a chapter into individual scenes using AI with continuity tracking.
        """
        if client is None:
            print(
                "Warning: Google Gemini API client not available. Using placeholder scenes."
            )
            # Create placeholder scenes for testing
            scenes = [
                Scene(
                    content="Luna and Orion begin their journey",
                    characters=["Luna", "Orion"],
                    location="Enchanted Forest",
                    scene_type="establishing",
                    narrative_flow="setup",
                    estimated_panels=2,
                    previous_scene=None,
                    next_scene="Scene 2",
                ),
                Scene(
                    content="They discover the Crystal Cave",
                    characters=["Luna", "Orion"],
                    location="Crystal Cave",
                    scene_type="action",
                    narrative_flow="conflict",
                    estimated_panels=3,
                    previous_scene="Scene 1",
                    next_scene="Scene 3",
                ),
            ]
            return scenes

        # First, analyze the narrative structure
        narrative_structure = self.analyze_narrative_structure(chapter)

        prompt = f"""
        Break this novel chapter into {narrative_structure['total_scenes']} distinct scenes with continuity tracking.
        
        Chapter:
        {chapter}
        
        Narrative Structure Analysis:
        - Scene Types: {narrative_structure['scene_types']}
        - Narrative Flow: {narrative_structure['narrative_flow']}
        - Optimal Panels: {narrative_structure['optimal_panels_per_scene']}
        
        For each scene, provide:
        - content: the scene text
        - characters: list of character names present
        - location: the location name
        - scene_type: one of the scene types from the analysis
        - narrative_flow: one of the flow elements from the analysis
        - estimated_panels: optimal panel count for this scene
        - previous_scene: reference to previous scene (null for first)
        - next_scene: reference to next scene (null for last)
        
        Ensure each scene flows naturally to the next and maintains location/character continuity.
        
        Return as JSON:
        {{
            "scenes": [
                {{
                    "content": "...",
                    "characters": ["char1", "char2"],
                    "location": "location_name",
                    "scene_type": "establishing",
                    "narrative_flow": "setup",
                    "estimated_panels": 2,
                    "previous_scene": null,
                    "next_scene": "Scene 2"
                }}
            ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Clean and parse JSON response
        text = clean_json_response(response.text)

        try:
            scenes_data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response text: {text[:200]}...")
            # Fallback to placeholder scenes
            return [
                Scene(
                    content="Scene parsing failed, using fallback",
                    characters=["Main Character"],
                    location="Story Location",
                    scene_type="establishing",
                    narrative_flow="setup",
                    estimated_panels=2,
                    previous_scene=None,
                    next_scene=None,
                )
            ]

        scenes = []
        for scene_data in scenes_data["scenes"]:
            scene = Scene(**scene_data)
            scenes.append(scene)

        # Update narrative flow tracking
        self.narrative_flow.scene_sequence = [scene.content for scene in scenes]
        if scenes:
            self.narrative_flow.current_scene = scenes[0].content

        return scenes

    def detect_panel_redundancy(self, new_panel: Panel) -> float:
        """
        Detect if a new panel is too similar to existing ones.
        Returns a similarity score (0.0 = completely different, 1.0 = identical).
        """
        if not self.generated_panels:
            return 0.0

        # Simple redundancy detection based on panel characteristics
        max_similarity = 0.0

        for existing_panel in self.generated_panels[-3:]:  # Check last 3 panels
            similarity = 0.0

            # Location similarity
            if new_panel.location == existing_panel.location:
                similarity += 0.3

            # Character overlap
            char_overlap = len(
                set(new_panel.characters) & set(existing_panel.characters)
            )
            total_chars = len(
                set(new_panel.characters) | set(existing_panel.characters)
            )
            if total_chars > 0:
                similarity += (char_overlap / total_chars) * 0.3

            # Panel type similarity
            if new_panel.panel_type == existing_panel.panel_type:
                similarity += 0.2

            # Camera angle similarity
            if new_panel.camera_angle == existing_panel.camera_angle:
                similarity += 0.2

            max_similarity = max(max_similarity, similarity)

        return max_similarity

    def direct_panels_with_continuity(
        self,
        scene_description: str,
        characters: List[str],
        location: str,
        scene_type: str,
        narrative_flow: str,
        target_panels: int,
    ) -> List[Panel]:
        """
        Direct and describe panels based on the scene with continuity and redundancy prevention.
        """
        if client is None:
            print(
                "Warning: Google Gemini API client not available. Using placeholder panels."
            )
            # Create placeholder panels for testing
            panels = [
                Panel(
                    description=f"Scene: {scene_description[:50]}...",
                    characters=characters,
                    location=location,
                    composition_prompt="Wide establishing shot",
                    panel_type="establishing",
                    camera_angle="wide",
                ),
                Panel(
                    description=f"Close-up of characters in {location}",
                    characters=characters,
                    location=location,
                    composition_prompt="Medium close-up shot",
                    panel_type="action",
                    camera_angle="medium",
                ),
            ]
            return panels

        prompt = f"""
        Create {target_panels} comic panels for this scene with visual variety and story progression.
        
        Scene: {scene_description}
        Characters: {', '.join(characters)}
        Location: {location}
        Scene Type: {scene_type}
        Narrative Flow: {narrative_flow}
        
        For each panel, provide:
        - description: what's happening in the panel (advance the story)
        - characters: which characters are present
        - location: the location (same as scene location)
        - composition_prompt: detailed prompt for image generation including camera angle, framing, etc.
        - panel_type: "establishing", "action", "reaction", "transition", or "climax"
        - camera_angle: "wide", "medium", "close", "bird_eye", or "worm_eye"
        
        Ensure each panel:
        1. Advances the story visually
        2. Has a different camera angle from other panels
        3. Shows different character interactions or actions
        4. Maintains visual continuity with the scene
        
        Return as JSON:
        {{
            "panels": [
                {{
                    "description": "...",
                    "characters": ["char1"],
                    "location": "{location}",
                    "composition_prompt": "...",
                    "panel_type": "establishing",
                    "camera_angle": "wide"
                }}
            ]
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )

        # Clean and parse JSON response
        text = clean_json_response(response.text)

        try:
            panels_data = json.loads(text)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response text: {text[:200]}...")
            # Fallback to placeholder panels
            return [
                Panel(
                    description=f"Panel parsing failed, using fallback",
                    characters=characters,
                    location=location,
                    composition_prompt="Fallback composition",
                    panel_type="establishing",
                    camera_angle="wide",
                )
            ]

        panels = []
        for panel_data in panels_data["panels"]:
            panel = Panel(**panel_data)

            # Check for redundancy
            redundancy_score = self.detect_panel_redundancy(panel)
            panel.redundancy_score = redundancy_score

            # If panel is too similar, regenerate or skip
            if redundancy_score > self.panel_similarity_threshold:
                print(
                    f"Panel too similar to existing ones (score: {redundancy_score:.2f}), regenerating..."
                )
                # Try to regenerate with different parameters
                panel.camera_angle = "close" if panel.camera_angle == "wide" else "wide"
                panel.panel_type = (
                    "action" if panel.panel_type == "establishing" else "establishing"
                )

            panels.append(panel)

        return panels

    def fetch_assets(self, panel: Panel) -> Dict[str, str]:
        """
        Identify and fetch assets based on panel description.
        Returns a dict mapping asset type to image path.
        """
        assets = {}

        # Fetch character images
        for char_name in panel.characters:
            if char_name in self.characters:
                char = self.characters[char_name]
                if not char.image_path or not validate_image_path(char.image_path):
                    print(f"Generating character image for {char_name}...")
                    self.generate_character_image(char)

                # Ensure we have a valid image path
                if char.image_path and validate_image_path(char.image_path):
                    assets[f"character_{char_name}"] = char.image_path
                    print(f"Added character asset: {char_name} -> {char.image_path}")
                else:
                    print(
                        f"Warning: Failed to generate valid image for character {char_name}"
                    )
                    # Create a fallback asset path
                    fallback_path = (
                        self.characters_dir
                        / f"{self._sanitize_filename(char_name)}_fallback.png"
                    )
                    if not fallback_path.exists():
                        # Create a simple placeholder
                        from PIL import Image, ImageDraw, ImageFont

                        img = Image.new("RGB", (256, 256), color="#e0e0e0")
                        draw = ImageDraw.Draw(img)
                        try:
                            font = ImageFont.truetype("arial.ttf", 16)
                        except:
                            font = ImageFont.load_default()
                        draw.text(
                            (10, 120),
                            f"Character: {char_name}",
                            fill="#333333",
                            font=font,
                        )
                        img.save(fallback_path)
                    assets[f"character_{char_name}"] = str(fallback_path)

                # Update character tracking
                char.last_seen_scene = self.narrative_flow.current_scene

        # Fetch location image
        if panel.location in self.locations:
            loc = self.locations[panel.location]
            if not loc.image_path or not validate_image_path(loc.image_path):
                print(f"Generating location image for {panel.location}...")
                self.generate_location_image(loc)

            # Ensure we have a valid image path
            if loc.image_path and validate_image_path(loc.image_path):
                # Validate that the location image doesn't contain characters
                if self.validate_location_asset(loc.image_path):
                    assets["location"] = loc.image_path
                    print(f"Added location asset: {panel.location} -> {loc.image_path}")
                else:
                    print(
                        f"Warning: Location image for {panel.location} may contain characters"
                    )
                    # Regenerate the location image
                    self.generate_location_image(loc)
                    if loc.image_path and validate_image_path(loc.image_path):
                        assets["location"] = loc.image_path
                    else:
                        print(
                            f"Failed to regenerate location image for {panel.location}"
                        )
            else:
                print(
                    f"Warning: Failed to generate valid image for location {panel.location}"
                )
                # Create a fallback asset path
                fallback_path = (
                    self.locations_dir
                    / f"{self._sanitize_filename(panel.location)}_fallback.png"
                )
                if not fallback_path.exists():
                    # Create a simple placeholder
                    from PIL import Image, ImageDraw, ImageFont

                    img = Image.new("RGB", (512, 256), color="#f0f0f0")
                    draw = ImageDraw.Draw(img)
                    try:
                        font = ImageFont.truetype("arial.ttf", 20)
                    except:
                        font = ImageFont.load_default()
                    draw.text(
                        (10, 120),
                        f"Location: {panel.location}",
                        fill="#666666",
                        font=font,
                    )
                    img.save(fallback_path)
                assets["location"] = str(fallback_path)

        return assets

    def generate_panel_image(self, panel: Panel, assets: Dict[str, str]) -> str:
        """
        Generate the panel image by composing the assets according to the panel description.
        """
        # Create a composition prompt that references the existing assets
        asset_descriptions = []
        for asset_type, asset_path in assets.items():
            if asset_type.startswith("character_"):
                char_name = asset_type.replace("character_", "")
                asset_descriptions.append(
                    f"Character {char_name} (use consistent appearance)"
                )
            elif asset_type == "location":
                asset_descriptions.append(
                    f"Location: {panel.location} (use consistent appearance)"
                )

        composition_prompt = f"""
        Create a manhwa-style comic panel with these specifications:
        
        Panel Description: {panel.description}
        Composition: {panel.composition_prompt}
        Panel Type: {panel.panel_type}
        Camera Angle: {panel.camera_angle}
        
        Characters: {', '.join(panel.characters)}
        Location: {panel.location}
        
        Style: Modern manhwa/webtoon style, clean lines, vibrant colors
        Panel Format: Comic panel with clear borders
        Quality: High resolution, detailed but not overly complex
        
        IMPORTANT: Compose this panel by combining the separate character and location assets.
        The location should serve as the background/environment, and characters should be 
        placed on top of it. Do not duplicate characters or add new ones - use only the 
        specified character assets.
        
        Ensure character consistency and proper composition.
        """

        # Save the generated panel
        panel_filename = f"panel_{len(list(self.panels_dir.glob('*.png')))}.png"
        panel_path = self.panels_dir / panel_filename

        # Generate the panel image using our utility function
        character_paths = [
            assets.get(f"character_{char}", "") for char in panel.characters
        ]
        location_path = assets.get("location", "")

        # Filter out empty paths
        character_paths = [path for path in character_paths if path and path.strip()]
        if not location_path or not location_path.strip():
            location_path = ""

        print(
            f"Panel composition - Characters: {len(character_paths)}, Location: {location_path}"
        )

        success = compose_panel_with_assets(
            composition_prompt, character_paths, location_path, panel_path
        )

        return str(panel_path)

    def process_chapter(self, chapter: str) -> List[str]:
        """
        Enhanced main pipeline: Convert a chapter string to a list of panel image paths.
        """
        print("1. Extracting entities...")
        characters, locations = self.extract_entities(chapter)

        print("2. Generating character images...")
        for character in characters:
            if not character.image_path or not validate_image_path(
                character.image_path
            ):
                self.generate_character_image(character)

        print("3. Generating location images (character-free backgrounds)...")
        for location in locations:
            if not location.image_path or not validate_image_path(location.image_path):
                self.generate_location_image(location)

        print("4. Analyzing narrative structure...")
        narrative_structure = self.analyze_narrative_structure(chapter)

        print("5. Splitting into scenes with continuity...")
        scenes = self.split_scenes_with_continuity(chapter)

        panel_paths = []
        total_panels_generated = 0

        for i, scene in enumerate(scenes):
            print(f"6. Processing scene {i+1}/{len(scenes)}...")
            print(
                f"   Scene type: {scene.scene_type}, Target panels: {scene.estimated_panels}"
            )

            # Update narrative flow
            self.narrative_flow.current_scene = scene.content

            # Direct panels for this scene with continuity
            panels = self.direct_panels_with_continuity(
                scene.content,
                scene.characters,
                scene.location,
                scene.scene_type,
                scene.narrative_flow,
                scene.estimated_panels,
            )

            for j, panel in enumerate(panels):
                print(f"   Generating panel {j+1}/{len(panels)}...")
                print(
                    f"   Panel type: {panel.panel_type}, Camera: {panel.camera_angle}"
                )

                # Fetch assets for this panel (characters and location as separate assets)
                assets = self.fetch_assets(panel)

                # Generate the panel image
                panel_path = self.generate_panel_image(panel, assets)
                panel_paths.append(panel_path)

                # Track generated panels for redundancy detection
                self.generated_panels.append(panel)
                total_panels_generated += 1

        print(f"\nTotal panels generated: {total_panels_generated}")
        print(f"Average panels per scene: {total_panels_generated / len(scenes):.1f}")

        return panel_paths

    def test_asset_generation(self):
        """Test method to verify asset generation works correctly"""
        print("Testing asset generation...")

        # Test character generation
        test_char = Character(
            name="Test Character",
            description="A test character for validation",
            visual_traits="Generic test appearance",
        )

        char_path = self.generate_character_image(test_char)
        print(f"Character image generated: {char_path}")
        print(f"Character image_path attribute: {test_char.image_path}")
        print(f"Image path valid: {validate_image_path(char_path)}")

        # Test location generation
        test_loc = Location(
            name="Test Location",
            description="A test location for validation",
            transition_type="interior",
        )

        loc_path = self.generate_location_image(test_loc)
        print(f"Location image generated: {loc_path}")
        print(f"Location image_path attribute: {test_loc.image_path}")
        print(f"Image path valid: {validate_image_path(loc_path)}")

        return True


def main():
    print("Enhanced Novel to Comic Generator")
    print("=================================")

    # Example usage
    comic_generator = EnhancedNovelToComic()

    # Test asset generation first
    print("Testing asset generation...")
    comic_generator.test_asset_generation()
    print()

    # Example chapter (you can replace this with actual chapter text)
    example_chapter = """
    Chapter 1: The Beginning
    
    Sarah stood at the edge of the ancient forest, her heart pounding with anticipation. 
    The towering trees seemed to whisper secrets of the past, their branches reaching 
    toward the cloudy sky like skeletal fingers.
    
    "Are you sure about this?" asked her best friend, Alex, who had followed her 
    despite his obvious nervousness. His brown eyes darted around the shadowy 
    undergrowth, searching for any sign of movement.
    
    "I have to find out what happened to my grandmother," Sarah replied, her 
    determination unwavering. She adjusted her backpack and took a deep breath. 
    "She disappeared somewhere in these woods thirty years ago, and I'm going 
    to find the truth."
    
    The wind picked up, rustling the leaves and carrying with it an eerie melody 
    that seemed to come from deep within the forest. Alex shivered and pulled 
    his jacket tighter around his shoulders.
    
    "That sound... it's like nothing I've ever heard before," he whispered.
    
    Sarah nodded, her eyes fixed on the path ahead. "That's exactly why we need 
    to investigate. Come on, let's go."
    
    Together, they stepped into the forest, the shadows swallowing them whole 
    as they ventured deeper into the unknown.
    """

    print("Processing chapter...")
    panel_paths = comic_generator.process_chapter(example_chapter)

    print(f"\nGenerated {len(panel_paths)} panels:")
    for i, path in enumerate(panel_paths):
        print(f"  Panel {i+1}: {path}")


if __name__ == "__main__":
    main()
