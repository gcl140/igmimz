from instagrapi import Client
from instagrapi.types import Usertag, Location
import os
from datetime import datetime
import random
import csv
import traceback
from PIL import Image
import shutil

def convert_to_jpeg(input_path, output_folder="/home/autoo/igmimz/converted"):
    """Convert image to JPEG format if it's not already"""
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        img = Image.open(input_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        base_name = os.path.splitext(os.path.basename(input_path))[0]
        output_path = os.path.join(output_folder, f"{base_name}.jpg")

        img.save(output_path, "JPEG", quality=95)
        return output_path
    except Exception as e:
        print(f"Error converting image: {e}")
        return None

def validate_media(file_path):
    """Validate media file size and integrity"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    if os.path.getsize(file_path) == 0:
        raise ValueError(f"File is empty: {file_path}")

    # For images
    if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            img = Image.open(file_path)
            img.verify()  # Validates file integrity
            img.close()

            # If not JPEG, convert it
            if not file_path.lower().endswith((".jpg", ".jpeg")):
                converted_path = convert_to_jpeg(file_path)
                if converted_path:
                    return converted_path
        except Exception as e:
            raise ValueError(f"Invalid image file: {file_path} - {str(e)}")

    # For videos (basic validation)
    elif file_path.lower().endswith((".mp4", ".mov")):
        if os.path.getsize(file_path) < 1024:  # At least 1KB
            raise ValueError(f"Video file too small: {file_path}")

    return file_path

def auto_post(username: str, password: str,
              session_file="/home/autoo/igmimz/session.json",
              post_folder="/home/autoo/igmimz/posts",
              caption_csv="/home/autoo/igmimz/captions.csv"):

    cl = Client()
    try:
        # Session handling with refresh if invalid
        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                if not cl.user_id:  # Check if session is still valid
                    raise Exception("Invalid session")
            except Exception as e:
                print("Session invalid, logging in fresh...")
                cl.login(username, password)
                cl.dump_settings(session_file)
        else:
            cl.login(username, password)
            cl.dump_settings(session_file)

        # Get media files
        photos = [f for f in os.listdir(post_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        videos = [f for f in os.listdir(post_folder) if f.lower().endswith((".mp4", ".mov"))]

        if not photos and not videos:
            raise FileNotFoundError("⚠️ No photos or videos found in the posts folder.")

        # Select one photo and one video if available
        chosen_photo = os.path.join(post_folder, random.choice(photos)) if photos else None
        chosen_video = os.path.join(post_folder, random.choice(videos)) if videos else None

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
        date_str = datetime.now().strftime('%Y-%m-%d')

        base_caption = random.choice(captions) if captions else "Check this out! 📸"
        full_caption = f"{base_caption}\n\nFollow for more!!!\n\nDaily post - {date_str} {' '.join(selected_tags)}"

        # Upload media if available
        if chosen_photo:
            try:
                validated_photo = validate_media(chosen_photo)
                cl.photo_upload(validated_photo, full_caption)
                print("✅ Photo uploaded successfully.")
                print(f"📝 Caption used:\n{full_caption}")
            except Exception as e:
                print(f"❌ Failed to upload photo: {str(e)}")
                traceback.print_exc()

        if chosen_video:
            try:
                validated_video = validate_media(chosen_video)
                # For reels, you might want to use cl.clip_upload() instead
                # cl.video_upload(validated_video, full_caption)
                cl.clip_upload(validated_video, full_caption)
                print("✅ Video uploaded successfully.")
                print(f"📝 Caption used:\n{full_caption}")
            except Exception as e:
                print(f"❌ Failed to upload video: {str(e)}")
                traceback.print_exc()

    except Exception as e:
        print("❌ An error occurred during auto posting:")
        traceback.print_exc()
        print(f"Error details: {str(e)}")

if __name__ == "__main__":
    auto_post("gcme.mes2025", "Lukoonge14@")
