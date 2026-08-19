import os
import csv
import random
import sqlite3
import subprocess
import traceback
from datetime import datetime

import imageio_ffmpeg
from dotenv import load_dotenv
from instagrapi import Client
from PIL import Image

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

IG_USERNAME = os.getenv("IG_USERNAME")
IG_PASSWORD = os.getenv("IG_PASSWORD")
SESSION_FILE = os.getenv("SESSION_FILE", os.path.join(BASE_DIR, "session.json"))
POST_FOLDER = os.getenv("POST_FOLDER", os.path.join(BASE_DIR, "posts"))
PHOTOS_FOLDER = os.getenv("PHOTOS_FOLDER", os.path.join(POST_FOLDER, "photos"))
VIDEOS_FOLDER = os.getenv("VIDEOS_FOLDER", os.path.join(POST_FOLDER, "videos"))
CAPTION_CSV = os.getenv("CAPTION_CSV", os.path.join(BASE_DIR, "captions.csv"))
STATE_DB = os.getenv("STATE_DB", os.path.join(BASE_DIR, "state.db"))
CONVERTED_FOLDER = os.getenv("CONVERTED_FOLDER", os.path.join(BASE_DIR, "converted"))

TAGS = [
    "#funnytweets", "#funny", "#humor", "#memes", "#lol", "#haha", "#comedy", "#funnymemes",
    "#laugh", "#jokes", "#dankmemes", "#meme", "#lmao", "#funnyvideos", "#hilarious",
    "#memeoftheday", "#sarcasm", "#relatable", "#funnyshit", "#funnyposts", "#funnyaf",
    "#laughoutloud", "#instafunny", "#humour", "#funnypictures", "#rofl", "#silly",
    "#justforfun", "#funnymeme", "#epicfail", "#funnyquotes",
]


def init_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS used_media ("
        "filename TEXT PRIMARY KEY, used_at TEXT)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS used_captions ("
        "caption TEXT PRIMARY KEY, used_at TEXT)"
    )
    conn.commit()
    return conn


def mark_used(conn, table, key_col, value):
    conn.execute(
        f"INSERT OR REPLACE INTO {table} ({key_col}, used_at) VALUES (?, ?)",
        (value, datetime.now().isoformat()),
    )
    conn.commit()


def pick_unused(conn, table, key_col, pool, label):
    """Pick a random item from pool that hasn't been used before.
    If every item has already been used, the cycle resets so nothing runs dry.
    """
    if not pool:
        return None

    used = {row[0] for row in conn.execute(f"SELECT {key_col} FROM {table}")}
    available = [item for item in pool if item not in used]

    if not available:
        print(f"All {label} have been used at least once - resetting the cycle.")
        conn.execute(f"DELETE FROM {table} WHERE {key_col} IN "
                     f"({','.join('?' for _ in pool)})", pool)
        conn.commit()
        available = pool

    return random.choice(available)


def generate_thumbnail(video_path, thumbnail_path, at_seconds=0.5):
    """Grab a single frame from the video as a JPEG thumbnail via ffmpeg."""
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [ffmpeg_exe, "-y", "-ss", str(at_seconds), "-i", str(video_path),
         "-frames:v", "1", "-q:v", "3", str(thumbnail_path)],
        check=True, capture_output=True,
    )


def convert_to_jpeg(input_path, output_folder=CONVERTED_FOLDER):
    """Convert image to JPEG format if it's not already"""
    try:
        os.makedirs(output_folder, exist_ok=True)

        img = Image.open(input_path)
        if img.mode != "RGB":
            img = img.convert("RGB")

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

    if file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        try:
            img = Image.open(file_path)
            img.verify()
            img.close()

            if not file_path.lower().endswith((".jpg", ".jpeg")):
                converted_path = convert_to_jpeg(file_path)
                if converted_path:
                    return converted_path
        except Exception as e:
            raise ValueError(f"Invalid image file: {file_path} - {str(e)}")

    elif file_path.lower().endswith((".mp4", ".mov")):
        if os.path.getsize(file_path) < 1024:
            raise ValueError(f"Video file too small: {file_path}")

    return file_path


def load_captions(caption_csv):
    if not os.path.exists(caption_csv):
        return []
    with open(caption_csv, "r", newline="") as file:
        return [row[0] for row in csv.reader(file) if row]


def build_caption(base_caption):
    selected_tags = random.sample(TAGS, 6)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return f"{base_caption}\n\nFollow for more!!!\n\nDaily post - {date_str} {' '.join(selected_tags)}"


def auto_post(username, password, session_file=SESSION_FILE,
              photos_folder=PHOTOS_FOLDER, videos_folder=VIDEOS_FOLDER,
              caption_csv=CAPTION_CSV, state_db=STATE_DB):

    if not username or not password:
        raise ValueError("IG_USERNAME / IG_PASSWORD are not set (check your .env file).")

    conn = init_db(state_db)
    cl = Client()

    try:
        if os.path.exists(session_file):
            try:
                cl.load_settings(session_file)
                if not cl.user_id:
                    raise Exception("Invalid session")
            except Exception:
                print("Session invalid, logging in fresh...")
                cl.login(username, password)
                cl.dump_settings(session_file)
        else:
            cl.login(username, password)
            cl.dump_settings(session_file)

        os.makedirs(photos_folder, exist_ok=True)
        os.makedirs(videos_folder, exist_ok=True)
        photos = [f for f in os.listdir(photos_folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        videos = [f for f in os.listdir(videos_folder) if f.lower().endswith((".mp4", ".mov"))]

        if not photos and not videos:
            raise FileNotFoundError("No photos or videos found in posts/photos or posts/videos.")

        chosen_photo = pick_unused(conn, "used_media", "filename", photos, "photos")
        chosen_video = pick_unused(conn, "used_media", "filename", videos, "videos")

        captions = load_captions(caption_csv)
        chosen_caption = pick_unused(conn, "used_captions", "caption", captions, "captions")
        base_caption = chosen_caption or "Check this out!"
        full_caption = build_caption(base_caption)

        if chosen_photo:
            photo_path = os.path.join(photos_folder, chosen_photo)
            try:
                validated_photo = validate_media(photo_path)
                cl.photo_upload(validated_photo, full_caption)
                mark_used(conn, "used_media", "filename", chosen_photo)
                print("Photo uploaded successfully.")
                print(f"Caption used:\n{full_caption}")
            except Exception:
                print(f"Failed to upload photo: {chosen_photo}")
                traceback.print_exc()

        if chosen_video:
            video_path = os.path.join(videos_folder, chosen_video)
            try:
                validated_video = validate_media(video_path)
                # Generate the thumbnail into CONVERTED_FOLDER ourselves - if left to
                # clip_upload's default, it drops a .jpg next to the video inside
                # post_folder, which then gets mistaken for a photo on the next run.
                os.makedirs(CONVERTED_FOLDER, exist_ok=True)
                thumbnail_path = os.path.join(
                    CONVERTED_FOLDER, os.path.basename(chosen_video) + ".jpg"
                )
                generate_thumbnail(validated_video, thumbnail_path)
                cl.clip_upload(validated_video, full_caption, thumbnail=thumbnail_path)
                mark_used(conn, "used_media", "filename", chosen_video)
                print("Video uploaded successfully.")
                print(f"Caption used:\n{full_caption}")
            except Exception:
                print(f"Failed to upload video: {chosen_video}")
                traceback.print_exc()

        if chosen_caption and (chosen_photo or chosen_video):
            mark_used(conn, "used_captions", "caption", chosen_caption)

    except Exception as e:
        print("An error occurred during auto posting:")
        traceback.print_exc()
        print(f"Error details: {str(e)}")
    finally:
        conn.close()


if __name__ == "__main__":
    auto_post(IG_USERNAME, IG_PASSWORD)
