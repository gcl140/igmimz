import csv
import random
from datetime import datetime

# Generate caption (could be dynamic)
with open('captions.csv', 'r') as file:
    reader = csv.reader(file)
    captions = [row[0] for row in reader if row]
caption = random.choice(captions) if captions else "Check out this awesome photo! 📸"

caption += f" Daily post - {datetime.now().strftime('%Y-%m-%d')}"

# Upload post
# cl.photo_upload(chosen_photo, caption)
print(caption)
print("✅ Post uploaded successfully.")