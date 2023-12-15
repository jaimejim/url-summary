import os
import sys
import requests
from bs4 import BeautifulSoup
from openai import OpenAI, OpenAIError
import tiktoken
from datetime import datetime
from termcolor import colored
from itertools import cycle

MAX_TOKENS = 128000  # The new maximum number of tokens for GPT-4 Turbo

# Initialize OpenAI
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def print_with_timestamp(message, color=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(colored(f'[{timestamp}] {message}', color))

def summarize_url(url, color):
    print_with_timestamp(f"Processing URL: {url}", color)
    print_with_timestamp("Sending request to URL...", color)
    try:
        response = requests.get(url)
    except requests.exceptions.SSLError:
        print_with_timestamp("SSL Verification failed. Retrying without SSL Verification...", 'yellow')
        response = requests.get(url, verify=False)
    print_with_timestamp("Response received. Parsing HTML...", color)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    # Check if the text exceeds the token limit
    if len(text) <= MAX_TOKENS:
        # Process as one chunk
        chunks = [text]
    else:
        # Split the text into appropriately sized chunks
        chunks = [text[i:i + MAX_TOKENS] for i in range(0, len(text), MAX_TOKENS)]

    client = OpenAI()
    summary = ""
    for chunk in chunks:
        print_with_timestamp("Sending chunk to OpenAI for processing...", color)
        try:
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": f"Generate a markdown formatted summary of the main aspects of this website, with features and useful information. Include a title in '##' format and embed links where necessary. The output should be a maximum 2 paragraphs of text without subsections, but including embedded links where necessary: {chunk}"}
                ],
                temperature=1,
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            summary += response.choices[0].message.content + "\n\n"
        except OpenAIError as e:
            print_with_timestamp(f"An error occurred: {str(e)}", 'red')

    return summary

def main(input_file, output_file):
    print_with_timestamp(f"Reading URLs from input file: {input_file}", 'green')
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print_with_timestamp(f"Writing summaries to output file: {output_file}", 'green')
    colors = cycle(['blue', 'magenta', 'cyan', 'yellow', 'white'])
    for url in urls:
        color = next(colors)
        summary = summarize_url(url, color)
        with open(output_file, 'a') as f:
            f.write(f'\n{summary}- {url}\n')
        print_with_timestamp(f"Appended summary to {output_file}", 'green')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])