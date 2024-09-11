import requests
import base64

def image_to_base64(url):
    # Fetch the image from the URL
    response = requests.get(url)
    
    # Ensure the request was successful
    if response.status_code == 200:
        # Encode the image content to base64
        encoded_image = base64.b64encode(response.content)
        
        # Convert to a readable base64 string
        base64_string = encoded_image.decode('utf-8')
        return base64_string
    else:
        return None

# Example usage:
# image_url = "http://plus.kipris.or.kr/kiprisplusws/fileToss.jsp?arg=ad7a17eeeef6e4ea4b5e22ef00dd3e29a5e93bcaa0e35e073b1e6c2fc0a2d532d65c7055be682c4bd2bf7857fba0e7ae4f5e673526ac2f62"
# base64_string = image_to_base64(image_url)

# if base64_string:
#     print("Base64 string:")
#     print(base64_string)
# else:
#     print("Failed to retrieve the image.")