#!/usr/bin/env python3
"""
Panel Optimizer for Enhanced Novel to Comic Generator

This module provides intelligent panel generation, redundancy detection, and variety optimization
to ensure each panel contributes meaningfully to the story without repetition.
"""

import json
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from google import genai
from config import secrets, comic_config


@dataclass
class PanelVariety:
    """Tracks panel variety to ensure visual diversity"""

    used_camera_angles: Set[str]
    used_panel_types: Set[str]
    used_compositions: Set[str]
    location_repetition_count: Dict[str, int]
    character_focus_count: Dict[str, int]

    def __post_init__(self):
        if self.used_camera_angles is None:
            self.used_camera_angles = set()
        if self.used_panel_types is None:
            self.used_panel_types = set()
        if self.used_compositions is None:
            self.used_compositions = set()
        if self.location_repetition_count is None:
            self.location_repetition_count = {}
        if self.character_focus_count is None:
            self.character_focus_count = {}


@dataclass
class RedundancyScore:
    """Detailed redundancy analysis for a panel"""

    overall_score: float  # 0.0 = unique, 1.0 = completely redundant
    location_similarity: float
    character_similarity: float
    composition_similarity: float
    timing_similarity: float
    redundancy_factors: List[str]
    suggestions: List[str]


class PanelOptimizer:
    """Intelligent panel generation and optimization"""

    def __init__(self, client: genai.Client):
        self.client = client
        self.panel_variety = PanelVariety()
        self.generated_panels: List[Dict] = []
        self.similarity_threshold = secrets.PANEL_SIMILARITY_THRESHOLD

    def generate_optimized_panels(
        self,
        scene_content: str,
        characters: List[str],
        location: str,
        scene_type: str,
        target_panel_count: int,
        previous_panels: List[Dict] = None,
    ) -> List[Dict]:
        """
        Generate optimized panels with variety and redundancy prevention.
        """
        if not self.client:
            return self._get_fallback_panels(
                scene_content, characters, location, target_panel_count
            )

        # Analyze scene for optimal panel distribution
        scene_analysis = self._analyze_scene_for_panels(
            scene_content, characters, location, scene_type
        )

        # Generate initial panel concepts
        panel_concepts = self._generate_panel_concepts(
            scene_analysis, target_panel_count
        )

        # Optimize each panel for variety and impact
        optimized_panels = []

        for i, concept in enumerate(panel_concepts):
            print(f"Optimizing panel {i+1}/{len(panel_concepts)}...")

            # Check for redundancy with previous panels
            redundancy_score = self._calculate_redundancy_score(
                concept, previous_panels or []
            )

            # If too redundant, regenerate with different approach
            if redundancy_score.overall_score > self.similarity_threshold:
                print(
                    f"Panel too similar (score: {redundancy_score.overall_score:.2f}), regenerating..."
                )
                concept = self._regenerate_panel_concept(
                    concept, scene_analysis, redundancy_score.suggestions
                )
                # Recalculate redundancy
                redundancy_score = self._calculate_redundancy_score(
                    concept, previous_panels or []
                )

            # Optimize panel composition
            optimized_panel = self._optimize_panel_composition(
                concept, scene_analysis, i, len(panel_concepts)
            )

            # Update variety tracking
            self._update_panel_variety(optimized_panel)

            optimized_panels.append(optimized_panel)

            # Add to generated panels for future reference
            self.generated_panels.append(optimized_panel)

        return optimized_panels

    def _analyze_scene_for_panels(
        self, scene_content: str, characters: List[str], location: str, scene_type: str
    ) -> Dict[str, any]:
        """Analyze scene to determine optimal panel breakdown."""

        prompt = f"""
        Analyze this scene to determine the optimal panel breakdown for comic adaptation.
        
        Scene Content: {scene_content}
        Characters: {', '.join(characters)}
        Location: {location}
        Scene Type: {scene_type}
        
        Analyze and provide:
        1. **Key Story Beats**: Important moments that need visual representation
        2. **Character Dynamics**: How characters interact and move through the scene
        3. **Location Elements**: Specific environmental details to show
        4. **Emotional Progression**: How the mood and tension change
        5. **Visual Pacing**: How to distribute visual information across panels
        
        Return as JSON:
        {{
            "key_story_beats": ["beat1", "beat2", "beat3"],
            "character_dynamics": [
                {{"characters": ["char1", "char2"], "interaction": "dialogue|action|reaction", "panel_focus": "description"}}
            ],
            "location_elements": ["element1", "element2"],
            "emotional_progression": ["emotion1", "emotion2", "emotion3"],
            "visual_pacing": "slow|medium|fast",
            "panel_distribution": "even|climax_focused|setup_heavy"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            return json.loads(text)

        except Exception as e:
            print(f"Error analyzing scene for panels: {e}")
            return self._get_fallback_scene_analysis()

    def _generate_panel_concepts(
        self, scene_analysis: Dict[str, any], target_count: int
    ) -> List[Dict]:
        """Generate initial panel concepts based on scene analysis."""

        prompt = f"""
        Generate {target_count} distinct comic panel concepts for this scene analysis.
        
        Scene Analysis:
        {json.dumps(scene_analysis, indent=2)}
        
        For each panel, provide:
        1. **Description**: What happens in this panel (advance the story)
        2. **Panel Type**: establishing, action, reaction, transition, climax, dialogue, emotion, detail
        3. **Camera Angle**: wide, medium, close, bird_eye, worm_eye, dutch_angle, over_shoulder
        4. **Focus**: What the reader should focus on
        5. **Composition**: How to frame and arrange elements
        6. **Emotional Impact**: What feeling this panel should convey
        
        Ensure each panel:
        - Advances the story meaningfully
        - Has a different visual approach from others
        - Contributes to the overall narrative flow
        - Maintains character and location consistency
        
        Return as JSON:
        {{
            "panels": [
                {{
                    "description": "Panel description",
                    "panel_type": "establishing",
                    "camera_angle": "wide",
                    "focus": "What to focus on",
                    "composition": "Composition details",
                    "emotional_impact": "Feeling to convey"
                }}
            ]
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            concepts = json.loads(text)
            return concepts["panels"]

        except Exception as e:
            print(f"Error generating panel concepts: {e}")
            return self._get_fallback_panel_concepts(target_count)

    def _calculate_redundancy_score(
        self, new_panel: Dict, previous_panels: List[Dict]
    ) -> RedundancyScore:
        """Calculate how redundant a new panel is compared to previous ones."""

        if not previous_panels:
            return RedundancyScore(
                overall_score=0.0,
                location_similarity=0.0,
                character_similarity=0.0,
                composition_similarity=0.0,
                timing_similarity=0.0,
                redundancy_factors=[],
                suggestions=[],
            )

        # Calculate similarity scores for different aspects
        location_similarity = self._calculate_location_similarity(
            new_panel, previous_panels
        )
        character_similarity = self._calculate_character_similarity(
            new_panel, previous_panels
        )
        composition_similarity = self._calculate_composition_similarity(
            new_panel, previous_panels
        )
        timing_similarity = self._calculate_timing_similarity(
            new_panel, previous_panels
        )

        # Weighted overall score
        weights = comic_config.redundancy_weights
        overall_score = (
            location_similarity * weights["location"]
            + character_similarity * weights["characters"]
            + composition_similarity * weights["panel_type"]
            + timing_similarity * 0.2  # Additional weight for timing
        )

        # Identify redundancy factors
        redundancy_factors = []
        if location_similarity > 0.7:
            redundancy_factors.append("Location too similar to previous panels")
        if character_similarity > 0.7:
            redundancy_factors.append("Character composition too similar")
        if composition_similarity > 0.7:
            redundancy_factors.append("Panel type and composition too similar")
        if timing_similarity > 0.7:
            redundancy_factors.append("Timing and pacing too similar")

        # Generate suggestions
        suggestions = self._generate_redundancy_suggestions(
            new_panel, redundancy_factors
        )

        return RedundancyScore(
            overall_score=overall_score,
            location_similarity=location_similarity,
            character_similarity=character_similarity,
            composition_similarity=composition_similarity,
            timing_similarity=timing_similarity,
            redundancy_factors=redundancy_factors,
            suggestions=suggestions,
        )

    def _calculate_location_similarity(
        self, new_panel: Dict, previous_panels: List[Dict]
    ) -> float:
        """Calculate location similarity with previous panels."""
        # This would be more sophisticated in a real implementation
        # For now, we'll use a simple approach
        return 0.0  # Placeholder

    def _calculate_character_similarity(
        self, new_panel: Dict, previous_panels: List[Dict]
    ) -> float:
        """Calculate character composition similarity with previous panels."""
        # This would analyze character positioning, interactions, etc.
        return 0.0  # Placeholder

    def _calculate_composition_similarity(
        self, new_panel: Dict, previous_panels: List[Dict]
    ) -> float:
        """Calculate composition and panel type similarity."""
        # This would analyze panel type, camera angle, composition style
        return 0.0  # Placeholder

    def _calculate_timing_similarity(
        self, new_panel: Dict, previous_panels: List[Dict]
    ) -> float:
        """Calculate timing and pacing similarity."""
        # This would analyze the story beat timing
        return 0.0  # Placeholder

    def _generate_redundancy_suggestions(
        self, panel: Dict, redundancy_factors: List[str]
    ) -> List[str]:
        """Generate suggestions to reduce redundancy."""
        suggestions = []

        for factor in redundancy_factors:
            if "Location" in factor:
                suggestions.append("Change camera angle to show different perspective")
                suggestions.append("Focus on different location elements")
            elif "Character" in factor:
                suggestions.append("Change character positioning or interaction")
                suggestions.append("Use different panel type (close-up vs wide shot)")
            elif "Composition" in factor:
                suggestions.append("Use different camera angle")
                suggestions.append("Change panel type (action vs reaction)")
            elif "Timing" in factor:
                suggestions.append("Adjust pacing or emotional intensity")
                suggestions.append("Change focus to different story element")

        return suggestions

    def _regenerate_panel_concept(
        self,
        original_concept: Dict,
        scene_analysis: Dict[str, any],
        suggestions: List[str],
    ) -> Dict:
        """Regenerate a panel concept to reduce redundancy."""

        prompt = f"""
        Regenerate this panel concept to reduce redundancy while maintaining story progression.
        
        Original Concept:
        {json.dumps(original_concept, indent=2)}
        
        Redundancy Issues:
        {', '.join(suggestions)}
        
        Scene Analysis:
        {json.dumps(scene_analysis, indent=2)}
        
        Generate a new panel concept that:
        1. Advances the story in a different way
        2. Uses different visual approach (camera angle, composition, focus)
        3. Maintains narrative coherence
        4. Avoids the redundancy issues mentioned
        
        Return as JSON:
        {{
            "description": "New panel description",
            "panel_type": "different panel type",
            "camera_angle": "different camera angle",
            "focus": "Different focus element",
            "composition": "Different composition approach",
            "emotional_impact": "Different emotional impact"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )

            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

            return json.loads(text)

        except Exception as e:
            print(f"Error regenerating panel concept: {e}")
            # Return modified original concept
            modified = original_concept.copy()
            modified["camera_angle"] = (
                "close" if modified["camera_angle"] == "wide" else "wide"
            )
            modified["panel_type"] = (
                "action" if modified["panel_type"] == "establishing" else "establishing"
            )
            return modified

    def _optimize_panel_composition(
        self,
        concept: Dict,
        scene_analysis: Dict[str, any],
        panel_index: int,
        total_panels: int,
    ) -> Dict:
        """Optimize panel composition for maximum impact and variety."""

        # Add composition prompt for image generation
        composition_prompt = self._generate_composition_prompt(concept, scene_analysis)

        # Add variety optimization
        optimized_concept = concept.copy()
        optimized_concept["composition_prompt"] = composition_prompt
        optimized_concept["panel_index"] = panel_index
        optimized_concept["total_panels"] = total_panels

        # Ensure variety in camera angles and panel types
        if panel_index > 0:
            optimized_concept = self._ensure_variety(optimized_concept, panel_index)

        return optimized_concept

    def _generate_composition_prompt(
        self, concept: Dict, scene_analysis: Dict[str, any]
    ) -> str:
        """Generate detailed composition prompt for image generation."""

        prompt = f"""
        Create a detailed composition prompt for this comic panel.
        
        Panel Concept:
        {json.dumps(concept, indent=2)}
        
        Scene Context:
        {json.dumps(scene_analysis, indent=2)}
        
        Generate a detailed composition prompt that includes:
        1. **Camera Position**: Exact camera placement and angle
        2. **Framing**: What's included and excluded from the frame
        3. **Character Positioning**: How characters are arranged
        4. **Lighting**: Light source, shadows, mood
        5. **Composition Rules**: Rule of thirds, leading lines, etc.
        6. **Visual Hierarchy**: What the eye should focus on first
        
        Return as a detailed composition prompt string.
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Error generating composition prompt: {e}")
            return f"Create a {concept['panel_type']} panel with {concept['camera_angle']} camera angle focusing on {concept['focus']}"

    def _ensure_variety(self, concept: Dict, panel_index: int) -> Dict:
        """Ensure variety between consecutive panels."""
        # This would implement more sophisticated variety checking
        # For now, we'll use the basic approach from the main module
        return concept

    def _update_panel_variety(self, panel: Dict):
        """Update variety tracking with new panel."""
        self.panel_variety.used_camera_angles.add(panel.get("camera_angle", ""))
        self.panel_variety.used_panel_types.add(panel.get("panel_type", ""))
        self.panel_variety.used_compositions.add(panel.get("composition", ""))

        # Update location repetition count
        location = panel.get("location", "unknown")
        self.panel_variety.location_repetition_count[location] = (
            self.panel_variety.location_repetition_count.get(location, 0) + 1
        )

    def _get_fallback_scene_analysis(self) -> Dict[str, any]:
        """Fallback scene analysis when AI fails."""
        return {
            "key_story_beats": ["main action", "character reaction", "resolution"],
            "character_dynamics": [
                {
                    "characters": ["main_character"],
                    "interaction": "action",
                    "panel_focus": "character action",
                }
            ],
            "location_elements": ["main setting"],
            "emotional_progression": ["neutral", "engaged", "resolved"],
            "visual_pacing": "medium",
            "panel_distribution": "even",
        }

    def _get_fallback_panel_concepts(self, target_count: int) -> List[Dict]:
        """Fallback panel concepts when AI fails."""
        concepts = []
        for i in range(target_count):
            concept = {
                "description": f"Panel {i+1} description",
                "panel_type": "establishing" if i == 0 else "action",
                "camera_angle": "wide" if i == 0 else "medium",
                "focus": f"Focus element {i+1}",
                "composition": f"Composition {i+1}",
                "emotional_impact": "neutral",
            }
            concepts.append(concept)
        return concepts
