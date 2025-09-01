import base64
import io
import os
from pathlib import Path
from typing import Optional
from google import genai
from google.genai import types
from PIL import Image
from google.oauth2 import service_account
from config import Secrets
import mimetypes

secrets = Secrets()


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


client = init_vertexai_client()


def generate_image_with_gemini(prompt: str, output_path: Path) -> bool:
    """
    Generate an image using Gemini 2.5 Flash Image Preview and save it to the specified path.

    Args:
        prompt: The text prompt for image generation (can also be a list of contents)
        output_path: Path where the generated image should be saved

    Returns:
        bool: True if successful, False otherwise
    """
    # Check if client is available
    if client is None:
        print("Warning: Vertex AI client not available. Creating placeholder image.")
        create_placeholder_image(
            output_path, prompt if isinstance(prompt, str) else str(prompt)
        )
        return False

    try:
        # Configure response modalities to include both IMAGE and TEXT
        generate_content_config = types.GenerateContentConfig(
            response_modalities=[
                "IMAGE",
                "TEXT",
            ],
        )

        # Handle both string prompts and list contents
        contents = prompt if isinstance(prompt, list) else [prompt]

        # Use generate_content_stream for streaming response
        file_index = 0
        for chunk in client.models.generate_content_stream(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
            config=generate_content_config,
        ):
            # Check if chunk has valid candidates and content
            if (
                chunk.candidates is None
                or chunk.candidates[0].content is None
                or chunk.candidates[0].content.parts is None
            ):
                continue

            # Check if this chunk contains image data
            if (
                chunk.candidates[0].content.parts[0].inline_data
                and chunk.candidates[0].content.parts[0].inline_data.data
            ):
                inline_data = chunk.candidates[0].content.parts[0].inline_data
                data_buffer = inline_data.data

                # Get file extension from MIME type
                file_extension = mimetypes.guess_extension(inline_data.mime_type)
                if file_extension is None:
                    file_extension = ".png"  # Default to PNG if MIME type is unknown

                # Save the image data
                try:
                    # Convert to PIL Image and save
                    image = Image.open(io.BytesIO(data_buffer))
                    image.save(output_path)
                    print(f"Successfully saved image to {output_path}")
                    return True
                except Exception as e:
                    print(f"Error processing image data: {e}")
                    continue
            else:
                # Print text content if present
                if hasattr(chunk, "text") and chunk.text:
                    print(f"Text response: {chunk.text}")

        # If we get here, no image was found in the response
        print("No image data found in response. Creating placeholder.")
        create_placeholder_image(
            output_path, prompt if isinstance(prompt, str) else str(prompt)
        )
        return False

    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback

        traceback.print_exc()
        # Create a placeholder image
        create_placeholder_image(
            output_path, prompt if isinstance(prompt, str) else str(prompt)
        )
        return False


def create_placeholder_image(output_path: Path, prompt: str):
    """
    Create a placeholder image when actual generation fails.
    """
    # Create a simple placeholder image
    width, height = 512, 512
    image = Image.new("RGB", (width, height), color="#f0f0f0")

    # Add text to indicate this is a placeholder
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(image)

    # Try to use a default font, fallback to basic if not available
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()

    # Add placeholder text
    text = f"Placeholder for: {prompt[:50]}..."
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (width - text_width) // 2
    y = (height - text_height) // 2

    draw.text((x, y), text, fill="#666666", font=font)

    image.save(output_path)


def compose_panel_with_assets(
    panel_prompt: str,
    character_paths: list,
    location_path: Optional[str],
    output_path: Path,
) -> bool:
    """
    Compose a panel by combining character and location assets.
    This function loads the actual image assets and provides them to Gemini
    along with the text prompt for proper image generation.
    """
    try:
        # Check if client is available
        if client is None:
            print(
                "Warning: Vertex AI client not available. Creating placeholder image."
            )
            create_placeholder_image(output_path, panel_prompt)
            return False

        # Prepare contents list starting with the text prompt
        contents = [panel_prompt]

        # Load and add character images
        for char_path in character_paths:
            if validate_image_path(char_path):
                try:
                    with open(char_path, "rb") as img_file:
                        img_data = img_file.read()
                        # Add character image to contents
                        contents.append(
                            {
                                "inline_data": {
                                    "mime_type": get_image_mime_type(char_path),
                                    "data": img_data,
                                }
                            }
                        )
                        print(f"Added character image: {char_path}")
                except Exception as e:
                    print(f"Failed to load character image {char_path}: {e}")
            else:
                print(f"Invalid character image path: {char_path}")

        # Load and add location image if provided
        if location_path and validate_image_path(location_path):
            try:
                with open(location_path, "rb") as img_file:
                    img_data = img_file.read()
                    # Add location image to contents
                    contents.append(
                        {
                            "inline_data": {
                                "mime_type": get_image_mime_type(location_path),
                                "data": img_data,
                            }
                        }
                    )
                    print(f"Added location image: {location_path}")
            except Exception as e:
                print(f"Failed to load location image {location_path}: {e}")

        # Use the updated generate_image_with_gemini function with the combined contents
        return generate_image_with_gemini(contents, output_path)

    except Exception as e:
        print(f"Error composing panel: {e}")
        import traceback

        traceback.print_exc()
        create_placeholder_image(output_path, panel_prompt)
        return False


def get_image_mime_type(image_path: str) -> str:
    """
    Detect the MIME type of an image file.
    """
    try:
        with Image.open(image_path) as img:
            format_name = img.format.lower()
            if format_name == "jpeg":
                return "image/jpeg"
            elif format_name == "png":
                return "image/png"
            elif format_name == "gif":
                return "image/gif"
            elif format_name == "bmp":
                return "image/bmp"
            elif format_name == "webp":
                return "image/webp"
            else:
                # Default to PNG if format is unknown
                return "image/png"
    except Exception as e:
        print(f"Error detecting MIME type for {image_path}: {e}")
        # Default to PNG if detection fails
        return "image/png"


def validate_image_path(image_path: str) -> bool:
    """
    Check if an image file exists and is valid.
    """
    path = Path(image_path)
    if not path.exists():
        return False

    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except:
        return False
