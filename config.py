import os
from pathlib import Path
from typing import Optional


class Secrets:
    """Configuration class for API keys and settings."""

    def __init__(self):
        # Google Cloud settings
        self.GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        self.GOOGLE_CLOUD_SA_PATH = os.getenv("GOOGLE_CLOUD_SA_PATH")

        # Enhanced novel-to-comic settings
        self.PANEL_SIMILARITY_THRESHOLD = float(
            os.getenv("PANEL_SIMILARITY_THRESHOLD", "0.7")
        )
        self.MAX_PANELS_PER_SCENE = int(os.getenv("MAX_PANELS_PER_SCENE", "4"))
        self.MIN_PANELS_PER_SCENE = int(os.getenv("MIN_PANELS_PER_SCENE", "2"))
        self.ENABLE_REDUNDANCY_DETECTION = (
            os.getenv("ENABLE_REDUNDANCY_DETECTION", "true").lower() == "true"
        )
        self.ENABLE_CONTINUITY_TRACKING = (
            os.getenv("ENABLE_CONTINUITY_TRACKING", "true").lower() == "true"
        )

        # Image generation settings
        self.IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "high")  # high, medium, low
        self.IMAGE_STYLE = os.getenv(
            "IMAGE_STYLE", "manhwa"
        )  # manhwa, manga, western, realistic
        self.DEFAULT_CAMERA_ANGLES = os.getenv(
            "DEFAULT_CAMERA_ANGLES", "wide,medium,close"
        ).split(",")

        # Scene analysis settings
        self.SCENE_ANALYSIS_MODEL = os.getenv(
            "SCENE_ANALYSIS_MODEL", "gemini-2.5-flash"
        )
        self.ENTITY_EXTRACTION_MODEL = os.getenv(
            "ENTITY_EXTRACTION_MODEL", "gemini-2.5-flash"
        )
        self.IMAGE_GENERATION_MODEL = os.getenv(
            "IMAGE_GENERATION_MODEL", "gemini-2.5-flash-image-preview"
        )

        # Output settings
        self.DEFAULT_OUTPUT_DIR = os.getenv("DEFAULT_OUTPUT_DIR", "comic_output")
        self.PANEL_NAMING_CONVENTION = os.getenv(
            "PANEL_NAMING_CONVENTION", "sequential"
        )  # sequential, descriptive, timestamped
        self.ENABLE_METADATA_EXPORT = (
            os.getenv("ENABLE_METADATA_EXPORT", "true").lower() == "true"
        )


class ComicConfig:
    """Configuration for comic generation behavior."""

    def __init__(self):
        # Panel generation settings
        self.panel_types = [
            "establishing",
            "action",
            "reaction",
            "transition",
            "climax",
            "dialogue",
            "emotion",
            "detail",
            "wide_shot",
            "close_up",
        ]

        self.camera_angles = [
            "wide",
            "medium",
            "close",
            "bird_eye",
            "worm_eye",
            "dutch_angle",
            "over_shoulder",
            "point_of_view",
        ]

        self.scene_types = [
            "establishing",
            "action",
            "dialogue",
            "transition",
            "climax",
            "setup",
            "conflict",
            "resolution",
            "character_intro",
            "location_change",
        ]

        self.narrative_flows = [
            "setup",
            "conflict",
            "rising_action",
            "climax",
            "falling_action",
            "resolution",
            "transition",
            "character_development",
            "world_building",
        ]

        # Redundancy detection weights
        self.redundancy_weights = {
            "location": 0.3,
            "characters": 0.3,
            "panel_type": 0.2,
            "camera_angle": 0.2,
        }

        # Panel count optimization by scene type
        self.optimal_panels_by_scene_type = {
            "establishing": 2,
            "action": 3,
            "dialogue": 2,
            "transition": 1,
            "climax": 4,
            "setup": 2,
            "conflict": 3,
            "resolution": 2,
            "character_intro": 2,
            "location_change": 2,
        }

        # Continuity tracking settings
        self.continuity_check_distance = 3  # Check last N panels for continuity
        self.location_transition_threshold = 0.5  # When to show location change
        self.character_consistency_threshold = 0.8  # Character appearance consistency


# Global configuration instances
secrets = Secrets()
comic_config = ComicConfig()
