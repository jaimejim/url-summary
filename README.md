# URL Summarizer

This script takes a list of URLs from a text file, scrapes the content of each website, and uses OpenAI's 'gpt-4-1106-preview' or a local model to generate a summary of each website. The summaries are saved in a Markdown file.

For local LLMs [Ollama](https://ollama.ai/library/phi) and the selected model must be installed and running. You can find models in the [Ollama Library](https://ollama.ai/library).

## Prerequisites

- Python env

You can install the necessary Python packages with pip:

```bash
pip install -r requirements.txt
```

You also need to set your `.env` OpenAI API key as an environment variable:

```sh
OPENAI_API_KEY=your-api-key-without-quotes
```

## Usage

Activate the environment (I use fish shell)

```sh
source env/bin/activate.fish
```

To run the script, pass the input file (a text file with one URL per line) and the output file (the Markdown file to write the summaries to) as arguments. You can also specify the model to use for summarization with the -m or --model option. The default model is 'openai'.

```sh
python summarizer.py urls.txt output.md -m model
```

Where:

- `input_file` is a text file containing one URL per line.
- `output_file` is the file where the summarized content will be written.
- `model` is the model to use for summarization. It can be either 'openai' or the name of a model running locally with an ollama api (e.g., 'phi', 'mixtral'...). If not provided, 'openai' is used by default.

This will create a Markdown file named output.md with the summaries of the websites listed in `urls.txt`.

## Notes on the Local Models

**phi-2** does not seem very well-suited for text summarization but rather simple, short chats. It tends to generate very inaccurate and often non-sensical summaries. It is particularly bad with non-english texts. I do not recommend it other than for testing purposes.

**mixtral** output is very good quality but impossibly slow on my 2,3 GHz Quad-Core Intel Core i7.
