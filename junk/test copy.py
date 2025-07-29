api = 'sk-cd19cc45e8d3498eb530f4a9fbb38da7'
from datetime import datetime
import random
import lorem
from faker import Faker

faker = Faker()

def generate_funny_caption():
    intros = random.choice([
        "Woke up like this 😎",
        "Proof I was outside today 🌞",
        "When in doubt, post a pic 📸",
        "Caught in 4K 🫣",
        "Insert deep quote here 🧠",
        "Living my villain arc 😈",
    ])

    outro = random.choice([
        "DM me if this made your day 😂",
        "Don't judge, just vibe 🎵",
        "Like if you feel attacked 😅",
        "Caption game weak but photo strong 💪",
    ])

    nonsense = lorem.sentence()
    fake_quote = faker.sentence()

    # return f"{random.choice(intros)}\n\n{nonsense}\n{fake_quote}\n\n{outro}"
    return f"{intros}\n\n{fake_quote}\n\n{outro}"


caption = generate_funny_caption() + f"\n\n📅 {datetime.now().strftime('%Y-%m-%d')}"

print(caption)