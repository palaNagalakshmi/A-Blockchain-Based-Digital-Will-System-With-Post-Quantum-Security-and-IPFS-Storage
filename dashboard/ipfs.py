import requests
from django.conf import settings


def upload_will_pdf_to_ipfs(file_path):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"

    headers = {
        "pinata_api_key": settings.PINATA_API_KEY,
        "pinata_secret_api_key": settings.PINATA_SECRET_API_KEY,
    }

    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files, headers=headers)

    response.raise_for_status()

    return response.json()["IpfsHash"]