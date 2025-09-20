import pyperclip
from google import genai
from pydantic import BaseModel
from plyer import notification
import platform
import subprocess
import argparse
from pathlib import Path


class Magic_text(BaseModel):
    output: str


client = genai.Client()


def load_style_guide(path: str) -> str:
    """Load style guide from a text file, fallback to default if not found."""
    style_path = Path(path)
    if style_path.exists():
        return style_path.read_text(encoding="utf-8").strip()
    return "## No style guide provided."


def build_improved_prompt(task: str, text: str, style_guide: str) -> str:
    """Wraps user task and input text into a structured prompt with style guide."""
    return f"""<system_prompt>
You are a specialized AI assistant for precise, automated text processing. 
Your output must be clean and adhere strictly to the user's instruction, as it will be used directly by a script.

## Rules:
1. **Execute the instruction:** Apply the user's instruction to the input text exactly as stated.
2. **No chatter:** Do not add any conversational text, preamble, or explanations.
3. **Strict formatting:** The output format must match what is requested in the instruction.

{style_guide}
</system_prompt>

<instruction>
{task}
</instruction>

<text>
{text}
</text>

<output>
""".strip()


def process_text(text: str, system_prompt: str, style_guide: str) -> str:
    """Send clipboard text to LLM and return processed output."""
    prompt = build_improved_prompt(system_prompt, text, style_guide)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": list[Magic_text],
        }
    )
    print(response.parsed[0].output)
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


def main(system_prompt: str, style_file: str):
    text = pyperclip.paste().strip()
    if not text:
        print("⚠️ Clipboard is empty. Copy text first.")
        return

    style_guide = load_style_guide(style_file)

    print("Original:", text)
    try:
        new_text = process_text(text, system_prompt, style_guide)
    except Exception as e:
        print("❌ Error calling LLM:", e)
        return

    print("Processed:", new_text)
    pyperclip.copy(new_text)
    notify_user()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Magic Text Processor")
    parser.add_argument(
        "--task",
        type=str,
        required=True,
        help="Instruction for processing text (e.g. 'Summarize in 3 bullet points.')"
    )
    parser.add_argument(
        "--style",
        type=str,
        default="style_guide.txt",
        help="Path to style guide text file (default: style_guide.txt)"
    )
    args = parser.parse_args()

    main(args.task, args.style)
