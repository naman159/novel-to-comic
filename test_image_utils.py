#!/usr/bin/env python3
"""
Test script for the updated image_utils functions.
This script tests the new asset handling capabilities.
"""

import os
from pathlib import Path
from image_utils import (
    compose_panel_with_assets,
    generate_image_with_gemini,
    get_image_mime_type,
    validate_image_path,
)


def test_mime_type_detection():
    """Test MIME type detection for different image formats."""
    print("Testing MIME type detection...")

    # Test with example images from the example_comic directory
    example_dir = Path("example_comic")

    if example_dir.exists():
        # Test character images
        char_dir = example_dir / "characters"
        if char_dir.exists():
            for char_file in list(char_dir.glob("*.png"))[
                :2
            ]:  # Test first 2 character files
                mime_type = get_image_mime_type(str(char_file))
                print(f"  {char_file.name}: {mime_type}")

        # Test location images
        loc_dir = example_dir / "locations"
        if loc_dir.exists():
            for loc_file in list(loc_dir.glob("*.png"))[
                :2
            ]:  # Test first 2 location files
                mime_type = get_image_mime_type(str(loc_file))
                print(f"  {loc_file.name}: {mime_type}")
    else:
        print("  Example comic directory not found, skipping MIME type tests")


def test_image_validation():
    """Test image path validation."""
    print("\nTesting image validation...")

    # Test with example images
    example_dir = Path("example_comic")

    if example_dir.exists():
        char_dir = example_dir / "characters"
        if char_dir.exists():
            for char_file in list(char_dir.glob("*.png"))[:2]:
                is_valid = validate_image_path(str(char_file))
                print(f"  {char_file.name}: {'Valid' if is_valid else 'Invalid'}")
    else:
        print("  Example comic directory not found, skipping validation tests")


def test_asset_composition():
    """Test the asset composition function."""
    print("\nTesting asset composition...")

    # Test with example assets
    example_dir = Path("example_comic")

    if example_dir.exists():
        char_dir = example_dir / "characters"
        loc_dir = example_dir / "locations"

        if char_dir.exists() and loc_dir.exists():
            # Get some example character and location files
            char_files = list(char_dir.glob("*.png"))[:2]  # First 2 character files
            loc_file = (
                list(loc_dir.glob("*.png"))[0] if list(loc_dir.glob("*.png")) else None
            )

            if char_files and loc_file:
                print(f"  Using characters: {[f.name for f in char_files]}")
                print(f"  Using location: {loc_file.name}")

                # Test the composition function
                output_path = Path("test_composed_panel.png")
                panel_prompt = "Create a manhwa panel showing these characters in this location, with dramatic lighting and dynamic composition."

                print("  Composing panel...")
                success = compose_panel_with_assets(
                    panel_prompt=panel_prompt,
                    character_paths=[str(f) for f in char_files],
                    location_path=str(loc_file),
                    output_path=output_path,
                )

                if success:
                    print(f"  Successfully created composed panel: {output_path}")
                else:
                    print("  Failed to create composed panel")
            else:
                print("  Not enough example assets found for composition test")
        else:
            print("  Character or location directories not found")
    else:
        print("  Example comic directory not found, skipping composition test")


def main():
    """Run all tests."""
    print("Testing updated image_utils functions...")
    print("=" * 50)

    test_mime_type_detection()
    test_image_validation()
    test_asset_composition()

    print("\n" + "=" * 50)
    print("Tests completed!")


if __name__ == "__main__":
    main()
