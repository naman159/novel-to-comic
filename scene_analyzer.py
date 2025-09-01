#!/usr/bin/env python3
"""
Scene Analyzer for Enhanced Novel to Comic Generator

This module provides advanced scene analysis, continuity tracking, and panel optimization
to ensure smooth narrative flow and visual consistency.
"""

import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from google import genai
from config import secrets, comic_config


@dataclass
class SceneAnalysis:
    """Result of scene analysis with narrative insights"""

    scene_id: str
    content: str
    scene_type: str
    narrative_flow: str
    emotional_tone: str
    pacing: str  # slow, medium, fast
    key_moments: List[str]
    character_interactions: List[
        Tuple[str, str, str]
    ]  # (char1, char2, interaction_type)
    location_details: Dict[str, str]
    estimated_panels: int
    continuity_requirements: List[str]
    visual_complexity: str  # simple, moderate, complex


@dataclass
class ContinuityTracker:
    """Tracks narrative and visual continuity across scenes"""

    current_scene: Optional[str] = None
    previous_scene: Optional[str] = None
    location_transitions: List[Tuple[str, str, str]] = (
        None  # (from, to, transition_type)
    )
    character_positions: Dict[str, str] = None  # character -> location
    time_progression: str = "continuous"  # continuous, flashback, timeskip
    mood_transitions: List[Tuple[str, str]] = None  # (from_mood, to_mood)

    def __post_init__(self):
        if self.location_transitions is None:
            self.location_transitions = []
        if self.character_positions is None:
            self.character_positions = {}
        if self.mood_transitions is None:
            self.mood_transitions = []


class SceneAnalyzer:
    """Advanced scene analysis and continuity tracking"""

    def __init__(self, client: genai.Client):
        self.client = client
        self.continuity_tracker = ContinuityTracker()
        self.scene_history: List[SceneAnalysis] = []

    def analyze_chapter_structure(self, chapter: str) -> Dict[str, any]:
        """
        Analyze the overall chapter structure to determine optimal scene distribution.
        """
        if not self.client:
            return self._get_fallback_structure()

        prompt = f"""
        Perform a comprehensive analysis of this novel chapter to determine optimal comic adaptation.
        
        Chapter Text:
        {chapter}
        
        Analyze and provide:
        1. **Narrative Structure**: Identify the story arc, key turning points, and emotional beats
        2. **Scene Breakdown**: Determine optimal number and type of scenes needed
        3. **Panel Distribution**: Calculate optimal panels per scene based on content complexity
        4. **Continuity Elements**: Identify what must remain consistent between scenes
        5. **Visual Progression**: Plan the visual flow and pacing
        
        Consider:
        - Story complexity and emotional weight
        - Character development moments
        - Location changes and transitions
        - Pacing and reader engagement
        - Visual variety and impact
        
        Return as detailed JSON:
        {{
            "narrative_structure": {{
                "story_arc": "setup -> conflict -> resolution",
                "key_turning_points": ["point1", "point2"],
                "emotional_beats": ["beat1", "beat2"],
                "pacing_overview": "slow start, building tension, fast climax"
            }},
            "scene_planning": {{
                "total_scenes": 4,
                "scene_types": ["establishing", "action", "dialogue", "resolution"],
                "narrative_flow": ["setup", "conflict", "rising_action", "resolution"],
                "estimated_panels_per_scene": [2, 3, 2, 2],
                "scene_descriptions": ["Brief description of each scene"]
            }},
            "continuity_requirements": {{
                "character_consistency": ["char1 appearance", "char2 emotional state"],
                "location_consistency": ["building layout", "time of day"],
                "story_elements": ["ongoing plot threads", "character relationships"]
            }},
            "visual_planning": {{
                "style_consistency": "maintain manhwa style throughout",
                "camera_variety": "ensure different angles between consecutive panels",
                "emotional_visualization": "use color and composition to convey mood"
            }}
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            # Extract JSON from response
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            structure = json.loads(text)
            return structure

        except Exception as e:
            print(f"Error analyzing chapter structure: {e}")
            return self._get_fallback_structure()

    def analyze_individual_scene(
        self, scene_content: str, scene_context: Dict[str, any]
    ) -> SceneAnalysis:
        """
        Analyze an individual scene for optimal panel generation and continuity.
        """
        if not self.client:
            return self._get_fallback_scene_analysis(scene_content)

        prompt = f"""
        Analyze this individual scene for comic panel generation with continuity considerations.
        
        Scene Content:
        {scene_content}
        
        Scene Context:
        - Scene Type: {scene_context.get('scene_type', 'unknown')}
        - Narrative Flow: {scene_context.get('narrative_flow', 'unknown')}
        - Previous Scene: {scene_context.get('previous_scene', 'none')}
        - Next Scene: {scene_context.get('next_scene', 'none')}
        
        Analyze and provide:
        1. **Scene Characteristics**: Type, emotional tone, pacing, visual complexity
        2. **Key Moments**: Important story beats that need visual representation
        3. **Character Dynamics**: Who interacts with whom and how
        4. **Location Details**: Specific environmental elements to maintain consistency
        5. **Panel Requirements**: Optimal number and types of panels needed
        6. **Continuity Notes**: What must remain consistent with previous/next scenes
        
        Return as JSON:
        {{
            "scene_id": "scene_{len(self.scene_history) + 1}",
            "scene_type": "establishing|action|dialogue|transition|climax",
            "narrative_flow": "setup|conflict|rising_action|climax|resolution",
            "emotional_tone": "calm|tense|excited|melancholy|furious",
            "pacing": "slow|medium|fast",
            "key_moments": ["moment1", "moment2"],
            "character_interactions": [
                ["char1", "char2", "dialogue|action|reaction"]
            ],
            "location_details": {{
                "primary_location": "location_name",
                "specific_elements": ["element1", "element2"],
                "atmospheric_details": "lighting, weather, mood"
            }},
            "estimated_panels": 3,
            "continuity_requirements": ["req1", "req2"],
            "visual_complexity": "simple|moderate|complex"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            # Extract JSON from response
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            analysis_data = json.loads(text)
            scene_analysis = SceneAnalysis(**analysis_data)

            # Update continuity tracker
            self._update_continuity_tracker(scene_analysis)

            # Add to history
            self.scene_history.append(scene_analysis)

            return scene_analysis

        except Exception as e:
            print(f"Error analyzing individual scene: {e}")
            return self._get_fallback_scene_analysis(scene_content)

    def optimize_panel_count(self, scene_analysis: SceneAnalysis) -> int:
        """
        Determine optimal panel count based on scene analysis and continuity requirements.
        """
        base_panels = scene_analysis.estimated_panels

        # Adjust based on scene type
        scene_type_multiplier = {
            "establishing": 0.8,  # Fewer panels for setup
            "action": 1.2,  # More panels for action
            "dialogue": 0.9,  # Slightly fewer for dialogue
            "transition": 0.6,  # Minimal panels for transitions
            "climax": 1.4,  # More panels for climactic moments
        }

        multiplier = scene_type_multiplier.get(scene_analysis.scene_type, 1.0)
        adjusted_panels = int(base_panels * multiplier)

        # Ensure within bounds
        min_panels = comic_config.MIN_PANELS_PER_SCENE
        max_panels = comic_config.MAX_PANELS_PER_SCENE

        return max(min_panels, min(max_panels, adjusted_panels))

    def check_continuity_violations(self, new_scene: SceneAnalysis) -> List[str]:
        """
        Check for potential continuity violations with previous scenes.
        """
        violations = []

        if not self.scene_history:
            return violations

        previous_scene = self.scene_history[-1]

        # Check location consistency
        if new_scene.location_details.get(
            "primary_location"
        ) != previous_scene.location_details.get("primary_location"):
            # This might be intentional, but check if it's a logical transition
            if not self._is_logical_location_transition(
                previous_scene.location_details.get("primary_location"),
                new_scene.location_details.get("primary_location"),
            ):
                violations.append(
                    f"Unexpected location change from {previous_scene.location_details.get('primary_location')} to {new_scene.location_details.get('primary_location')}"
                )

        # Check character consistency
        for char in new_scene.character_interactions:
            if char[0] in previous_scene.character_interactions:
                # Character was in previous scene, check for logical progression
                pass  # Add more sophisticated character continuity checks here

        # Check time progression
        if new_scene.pacing == "fast" and previous_scene.pacing == "slow":
            # This might need a transition panel
            violations.append("Sudden pacing change might need transition panel")

        return violations

    def suggest_continuity_panels(self, scene_analysis: SceneAnalysis) -> List[str]:
        """
        Suggest additional panels needed for continuity.
        """
        suggestions = []

        # Check if we need a location transition panel
        if (
            self.continuity_tracker.previous_scene
            and self.continuity_tracker.previous_scene != scene_analysis.scene_id
        ):
            suggestions.append("Consider adding location transition panel")

        # Check if we need character re-establishment
        if scene_analysis.visual_complexity == "complex":
            suggestions.append("Consider adding character re-establishment panel")

        # Check if we need mood transition
        if (
            self.continuity_tracker.mood_transitions
            and len(self.continuity_tracker.mood_transitions) > 0
        ):
            last_mood = self.continuity_tracker.mood_transitions[-1][1]
            if last_mood != scene_analysis.emotional_tone:
                suggestions.append(
                    f"Consider mood transition panel from {last_mood} to {scene_analysis.emotional_tone}"
                )

        return suggestions

    def _update_continuity_tracker(self, scene_analysis: SceneAnalysis):
        """Update the continuity tracker with new scene information."""
        self.continuity_tracker.previous_scene = self.continuity_tracker.current_scene
        self.continuity_tracker.current_scene = scene_analysis.scene_id

        # Update location tracking
        if scene_analysis.location_details.get("primary_location"):
            current_location = scene_analysis.location_details["primary_location"]
            if (
                self.continuity_tracker.previous_scene
                and current_location
                != self.continuity_tracker.character_positions.get("location")
            ):
                self.continuity_tracker.location_transitions.append(
                    (
                        self.continuity_tracker.character_positions.get(
                            "location", "unknown"
                        ),
                        current_location,
                        "scene_change",
                    )
                )
            self.continuity_tracker.character_positions["location"] = current_location

        # Update mood tracking
        if (
            self.continuity_tracker.mood_transitions
            and len(self.continuity_tracker.mood_transitions) > 0
        ):
            last_mood = self.continuity_tracker.mood_transitions[-1][1]
            if last_mood != scene_analysis.emotional_tone:
                self.continuity_tracker.mood_transitions.append(
                    (last_mood, scene_analysis.emotional_tone)
                )
        else:
            self.continuity_tracker.mood_transitions.append(
                ("neutral", scene_analysis.emotional_tone)
            )

    def _is_logical_location_transition(
        self, from_location: str, to_location: str
    ) -> bool:
        """Check if a location transition is logically sound."""
        # This is a simplified check - in a real implementation, you'd have
        # a more sophisticated location relationship graph
        if not from_location or not to_location:
            return True

        # Some obvious logical violations
        impossible_transitions = [
            ("interior", "exterior"),  # Need a door/exit panel
            ("day", "night"),  # Need time transition
            ("city", "forest"),  # Need travel transition
        ]

        for impossible in impossible_transitions:
            if (
                from_location.lower() in impossible[0]
                and to_location.lower() in impossible[1]
            ):
                return False

        return True

    def _get_fallback_structure(self) -> Dict[str, any]:
        """Fallback structure when AI analysis fails."""
        return {
            "narrative_structure": {
                "story_arc": "setup -> conflict -> resolution",
                "key_turning_points": ["beginning", "middle", "end"],
                "emotional_beats": ["introduction", "tension", "resolution"],
                "pacing_overview": "steady progression",
            },
            "scene_planning": {
                "total_scenes": 3,
                "scene_types": ["establishing", "action", "resolution"],
                "narrative_flow": ["setup", "conflict", "resolution"],
                "estimated_panels_per_scene": [2, 3, 2],
                "scene_descriptions": ["Scene setup", "Main action", "Resolution"],
            },
            "continuity_requirements": {
                "character_consistency": ["maintain character appearances"],
                "location_consistency": ["maintain location details"],
                "story_elements": ["maintain plot continuity"],
            },
            "visual_planning": {
                "style_consistency": "maintain consistent art style",
                "camera_variety": "use different camera angles",
                "emotional_visualization": "convey mood through composition",
            },
        }

    def _get_fallback_scene_analysis(self, scene_content: str) -> SceneAnalysis:
        """Fallback scene analysis when AI analysis fails."""
        return SceneAnalysis(
            scene_id=f"scene_{len(self.scene_history) + 1}",
            content=scene_content,
            scene_type="establishing",
            narrative_flow="setup",
            emotional_tone="neutral",
            pacing="medium",
            key_moments=["main action"],
            character_interactions=[["character", "other", "interaction"]],
            location_details={
                "primary_location": "unknown",
                "specific_elements": [],
                "atmospheric_details": "neutral",
            },
            estimated_panels=2,
            continuity_requirements=["maintain consistency"],
            visual_complexity="simple",
        )
