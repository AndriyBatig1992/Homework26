import cloudinary.uploader
import hashlib

from src.conf.config import settings

class CloudImage:
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True
    )

    @staticmethod
    def generate_name_avatar(email: str):
        """
        The generate_name_avatar function takes an email address as input and returns a unique avatar name.
        The function uses the first 12 characters of the SHA256 hash of the email address to generate a unique string,
        which is then prepended with &quot;Web16/&quot;. This ensures that all avatars are stored in one folder on S3.

        :param email: str: Specify the type of data that is expected to be passed into the function
        :return: A string
        """
        name = hashlib.sha256(email.encode('utf-8')).hexdigest()[:12]
        return f"Web16/{name}"

    @staticmethod
    def get_url_for_avatar(public_id, r):
        """
        The get_url_for_avatar function takes in a public_id and an r (which is the result of a cloudinary.api.resource call)
        and returns the URL for that avatar image, which will be used to display it on the page.

        :param public_id: Specify the image to be used
        :param r: Pass in the request object
        :return: A url for an image with a public_id
        """
        src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=r.get('version'))
        return src_url

    @staticmethod
    def upload(file, public_id: str):
        """
        The upload function takes a file and public_id as arguments.
            The function then uploads the file to cloudinary using the public_id provided.
            If no public_id is provided, one will be generated for you.

        :param file: Specify the file to be uploaded
        :param public_id: str: Set the public id of the image
        :return: A dictionary with the following keys:
        """
        r = cloudinary.uploader.upload(file, public_id=public_id, owerwrite=True)
        return r


