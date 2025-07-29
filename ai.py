from instagrapi import Client
import os
from datetime import datetime
import random
import csv
import traceback

def auto_post(username: str, password: str, session_file="session.json", post_folder="/home/gcl/Desktop/GCL/Projects/Cannon/igmemes/posts", caption_csv="/home/gcl/Desktop/GCL/Projects/Cannon/igmemes/captions.csv"):
    cl = Client()
    try:
        # Load session if exists
        if os.path.exists(session_file):
            cl.load_settings(session_file)
            cl.login(username, password)
        else:
            cl.login(username, password)
            cl.dump_settings(session_file)

        # Get a random photo
        photos = [f for f in os.listdir(post_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if not photos:
            raise FileNotFoundError("⚠️ No photos found in the posts folder.")

        chosen_photo = os.path.join(post_folder, random.choice(photos))

        # Load captions
        captions = []
        if os.path.exists(caption_csv):
            with open(caption_csv, 'r') as file:
                reader = csv.reader(file)
                captions = [row[0] for row in reader if row]

        tags = [
            "#funnytweets", "#funny", "#humor", "#memes", "#lol", "#haha", "#comedy", "#funnymemes",
            "#laugh", "#jokes", "#dankmemes", "#meme", "#lmao", "#funnyvideos", "#hilarious",
            "#memeoftheday", "#sarcasm", "#relatable", "#funnyshit", "#funnyposts", "#funnyaf",
            "#laughoutloud", "#instafunny", "#humour", "#funnypictures", "#rofl", "#silly",
            "#justforfun", "#funnymeme", "#epicfail", "#funnyquotes",
        ]

        selected_tags = random.sample(tags, 6)

        base_caption = random.choice(captions) if captions else "Check out this awesome photo! 📸"
        # full_caption = f"{base_caption}\n\nDaily post - {datetime.now().strftime('%Y-%m-%d')} " + " ".join(tags)
        full_caption = f"{base_caption}\n\nDaily post - {datetime.now().strftime('%Y-%m-%d')} {' '.join(selected_tags)}"

        # Upload the post
        cl.photo_upload(chosen_photo, full_caption)
        print("✅ Post uploaded successfully.")
        print(f"📝 Caption used:\n{full_caption}")

    except Exception as e:
        print("❌ An error occurred during auto posting:")
        traceback.print_exc()
        print(f"Error details: {str(e)}")
        
if __name__ == "__main__":
    auto_post("gcme.mes2025", "Lukoonge14@0")
