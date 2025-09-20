import pyperclip
from google import genai
from pydantic import BaseModel
from plyer import notification
import platform, subprocess


class Magic_text(BaseModel):
    output: str


client = genai.Client()

# 🔧 Change this to control how the model processes text
SYSTEM_PROMPT = "Rewrite the text to be clearer and more concise."


def process_text(text: str) -> str:
    """Send clipboard text to LLM and return processed output."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{SYSTEM_PROMPT}\n\nText:\n{text}",
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Magic_text],
        }
    )
    return response.parsed[0].output


def notify_user():
    """Show a notification and play a sound when done."""
    notification.notify(
        title="Clipboard Ready",
        message="Processed text copied to clipboard. Paste it where you want.",
        timeout=3
    )

    system = platform.system()
    try:
        if system == "Windows":
            import winsound
            winsound.MessageBeep()
        elif system == "Darwin":  # macOS
            subprocess.run(
                ["afplay", "/System/Library/Sounds/Glass.aiff"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        elif system == "Linux":
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as e:
        print(f"(No sound played: {e})")


def main():
    text = pyperclip.paste().strip()
    if not text:
        print("⚠️ Clipboard is empty. Copy text first.")
        return

    print("Original:", text)
    try:
        new_text = process_text(text)
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return

    print("Processed:", new_text)
    pyperclip.copy(new_text)
    notify_user()


if __name__ == "__main__":
    main()
