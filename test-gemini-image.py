from config import Secrets
from google.genai import Client, types
import base64
from PIL import Image
from io import BytesIO
from google.oauth2 import service_account
import mimetypes

secrets = Secrets()

credentials = service_account.Credentials.from_service_account_file(
    secrets.GOOGLE_CLOUD_SA_PATH,
    scopes=[
        "https://www.googleapis.com/auth/generative-language",
        "https://www.googleapis.com/auth/cloud-platform",
    ],
)


prompt = "Create a picture of cyw on a beach"


def save_binary_file(file_name, data):
    f = open(file_name, "wb")
    f.write(data)
    f.close()
    print(f"File saved to to: {file_name}")


def generate():
    client = Client(
        vertexai=True,
        project=secrets.GOOGLE_CLOUD_PROJECT,
        location=secrets.GOOGLE_CLOUD_LOCATION,
        credentials=credentials,
    )

    image = Image.open("cyw.jpeg")

    model = "gemini-2.5-flash-image-preview"
    # contents = [
    #     types.Content(
    #         role="user",
    #         parts=[
    #             types.Part.from_text(text="""INSERT_INPUT_HERE"""),
    #         ],
    #     ),
    # ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=[
            "IMAGE",
            "TEXT",
        ],
    )

    file_index = 0
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=[prompt, image],
        config=generate_content_config,
    ):
        if (
            chunk.candidates is None
            or chunk.candidates[0].content is None
            or chunk.candidates[0].content.parts is None
        ):
            continue
        if (
            chunk.candidates[0].content.parts[0].inline_data
            and chunk.candidates[0].content.parts[0].inline_data.data
        ):
            file_name = f"ENTER_FILE_NAME_{file_index}"
            file_index += 1
            inline_data = chunk.candidates[0].content.parts[0].inline_data
            data_buffer = inline_data.data
            file_extension = mimetypes.guess_extension(inline_data.mime_type)
            save_binary_file(f"{file_name}{file_extension}", data_buffer)
        else:
            print(chunk.text)


if __name__ == "__main__":
    generate()
