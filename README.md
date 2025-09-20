# magic-clipboard
It takes text in the clipboard as text then process it and puts the output in the clipboard for the user to paster where they please

After cloning the project.
Run: `uv sync`

Copy text on to your clipboard. Run the script as follows: `uv run main.py --task "how you want the text to be processed" --style "path to your .txt style guide"` 

`--style` is optional. `/style_guide.txt` is the default style guide

The ideal use cases for this script is to setup shortcut keys that call your preferred commands. This is ideal if you often ask LLMs to transform text a specific way.

##Modes
You can switch between two modes `--mode writing` and `--mode coding`

`writing` is for transforming text like summarising text
`coding` is working with pyton code
