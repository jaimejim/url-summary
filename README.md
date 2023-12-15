# URL Summarizer

This script takes a list of URLs from a text file, scrapes the content of each website, and uses the OpenAI GPT-4 API to generate a summary of each website. The summaries are saved in a Markdown file.

If you find this useful consider buying me a beer 🍺 or something.

## Prerequisites

You can install the necessary Python packages with pip:

```bash
pip install requirements.txt
```

You also need to set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY=your-api-key
```

Replace your-api-key with your actual OpenAI API key.

## Usage

Activate the environment (I use fish shell)

```bash
source env/bin/activate.fish
```

To run the script, pass the input file (a text file with one URL per line) and the output file (the Markdown file to write the summaries to) as arguments:

```bash
python summarizer.py urls.txt output.md
```

This will create a Markdown file named output.md with the summaries of the websites listed in `urls.txt`.