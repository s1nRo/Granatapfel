import requests

from mirror.config import settings

owner = "Flowseal"
repo = "zapret-discord-youtube"

r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/releases", headers={'Authorization': f"Bearer {settings.GITHUB_TOKEN}"})
print(r.json())