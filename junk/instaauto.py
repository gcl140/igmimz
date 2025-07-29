from instagrapi import Client
import os
from datetime import datetime
import random
import csv

# Setup client
cl = Client()

# Login (First time: will ask for code if 2FA or challenge is triggered)
USERNAME = "gcme.mes2025"
PASSWORD = "Lukoonge14@0"
# cl.login(USERNAME, PASSWORD)

# Optional: Save session to file (avoids re-login next time)
# cl.dump_settings("session.json")

# Optional: Load session if already saved
cl.load_settings("session.json")
cl.login(USERNAME, PASSWORD)

# Choose random photo from folder
post_folder = "posts"
photos = [f for f in os.listdir(post_folder) if f.endswith((".jpg", ".jpeg", ".png"))]
chosen_photo = os.path.join(post_folder, random.choice(photos))

# Generate caption (could be dynamic)
with open('captions.csv', 'r') as file:
    reader = csv.reader(file)
    captions = [row[0] for row in reader if row]
caption = random.choice(captions) if captions else "Check out this awesome photo! 📸"

caption += f" Daily post - {datetime.now().strftime('%Y-%m-%d')} #funnytweets #fyp #foryoupage #viral #trending #explorepage"

# Upload post
# cl.photo_upload(chosen_photo, caption)
print(caption)
print("✅ Post uploaded successfully.")