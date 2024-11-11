import os

img_path = "image/1700280327108.jpg"
if os.path.exists(img_path):
    print(f"The image exists at: {img_path}")
else:
    print(f"The image does not exist at: {img_path}")