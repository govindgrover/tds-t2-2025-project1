import base64
from PIL import Image
from io import BytesIO

# ############## [ END IMPORTS ] ##############


def is_valid_base64_image(encoded: str) -> bool:
	"""
	Checks whether a given string is a valid base64-encoded image.

	Attempts to decode the string using base64. If decoding fails,
	the function returns False, indicating the input is not valid base64.

	Parameters:
		encoded (str): The base64-encoded string to validate.

	Returns:
		bool: True if the input is valid base64; False otherwise.
	"""
	try:
		base64.b64decode(encoded)
		return True
	except Exception:
		return False


def decode_base64_image(encoded: str) -> Image.Image:
	"""
	Decodes a base64-encoded string into a PIL Image object.

	This function assumes that the input string is a valid base64 representation
	of an image. The binary image data is first decoded, then converted into
	an image using the PIL library.

	Parameters:
		encoded (str): Base64-encoded image string.

	Returns:
		Image.Image: A PIL Image object created from the decoded data.
	"""
	image_data = base64.b64decode(encoded)
	return Image.open(BytesIO(image_data))
