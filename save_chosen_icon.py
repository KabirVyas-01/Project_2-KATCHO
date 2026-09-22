"""
Apply the chosen Version 1 icon as the official KATCHO app icon in static/icons/.
"""

import os
from PIL import Image

src_img_path = r"C:\Users\91999\.gemini\antigravity\brain\475aed69-7f52-4dc2-9bb3-7cbcaae9f1a8\katcho_app_icon_1789126927039.jpg"
out_dir = r"d:\KABIR CS work\Project_2\static\icons"
os.makedirs(out_dir, exist_ok=True)

if os.path.exists(src_img_path):
    with Image.open(src_img_path) as img:
        # Save 512x512
        img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        img_512.save(os.path.join(out_dir, "icon-512.png"), "PNG")
        
        # Save 192x192
        img_192 = img.resize((192, 192), Image.Resampling.LANCZOS)
        img_192.save(os.path.join(out_dir, "icon-192.png"), "PNG")

        # Save high-res master
        img.save(os.path.join(out_dir, "katcho_icon_master.png"), "PNG")
        print("Successfully updated static/icons with Version 1 icon!")
else:
    print("Source image not found, check path.")
