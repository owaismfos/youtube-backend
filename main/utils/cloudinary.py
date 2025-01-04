import cloudinary.uploader
import cloudinary.api
import cloudinary
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("API_KEY"),
    api_secret=os.getenv("API_SECRET"),
    secure=True,
)

def uploadOnCloudinry(file, folder_name):
    try:
        result = cloudinary.uploader.upload(
            file,
            folder = folder_name,
            resource_type = "auto"
        )
        return result, 'success'
    except Exception as e:
        print(str(e))
        return None, str(e)


def deleteFromCloudinry(public_id):
    try:
        result = cloudinary.api.delete_resources(
            public_id,
            resource_type="image",
            type="upload"
        )
        return result, 'success'
    except Exception as e:
        return None, str(e)
