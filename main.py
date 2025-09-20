import pyperclip
from google import genai
from pydantic import BaseModel
from plyer import notification
import platform
import subprocess
import argparse


class Magic_text(BaseModel):
    output: str


client = genai.Client()


def build_prompt(task: str, text: str) -> str:
    """Wraps user task and input text into a more robust and flexible prompt."""
    return f"""<system_prompt>
You are a specialized AI assistant for precise, automated text processing. Your output must be clean and adhere strictly to the user's instruction, as it will be used directly by a script.

## Rules:
1.  **Execute the instruction:** Apply the user's instruction to the input text exactly as stated.
2.  **No chatter:** Do not add any conversational text, preamble, or explanations.
3.  **Strict formatting:** The output format must match what is requested in the instruction.
</system_prompt>

<instruction>
{task}
</instruction>

<text>
{text}
</text>

<output>
"""


def process_text(text: str, system_prompt: str) -> str:
    """Send clipboard text to LLM and return processed output."""
    prompt = build_prompt(system_prompt, text)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
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


def main(system_prompt: str):
    text = pyperclip.paste().strip()
    if not text:
        print("⚠️ Clipboard is empty. Copy text first.")
        return

    print("Original:", text)
    try:
        new_text = process_text(text, system_prompt)
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
    args = parser.parse_args()

    main(args.task)
