import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from openai import OpenAI, OpenAIError
import tiktoken
import json
from datetime import datetime
from termcolor import colored
from itertools import cycle

MAX_TOKENS = 128000  # The new maximum number of tokens for GPT-4 Turbo

# Initialize OpenAI
OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def print_with_timestamp(message, color=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(colored(f'[{timestamp}] {message}', color))

def summarize_url_with_openai(url, color):
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
        print_with_timestamp(f"Sending chunk to OpenAI model for processing (chunk length: {len(chunk)} characters)...", color)
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

def summarize_url_with_phi(url, color):
    print_with_timestamp(f"Processing URL: {url} with Phi model", color)
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

    summary = ""
    for chunk in chunks:
        print_with_timestamp(f"Sending chunk to Phi model for processing (chunk length: {len(chunk)} characters)...", color)
        try:
            prompt = f"Generate a markdown formatted summary of the main aspects of this website, with features and useful information. Include a title in '##' format and embed links where necessary. The output should be a maximum 2 paragraphs of text without subsections or bullets and including embedded links where necessary: {chunk}"
            response = requests.post('http://localhost:11434/api/generate', data=json.dumps({
                "model": "phi",
                "prompt": prompt,
                "stream": False
            }), headers={'Content-Type': 'application/json'})
            response_json = response.json()
            if 'response' in response_json:
                summary += response_json['response'] + "\n\n"
        except Exception as e:
            print_with_timestamp(f"An error occurred: {str(e)}", 'red')

    return summary

def main(input_file, output_file, model):
    print_with_timestamp(f"Reading URLs from input file: {input_file}", 'green')
    with open(input_file, 'r') as f:
        urls = [line.strip() for line in f if line.strip()]

    print_with_timestamp(f"Writing summaries to output file: {output_file}", 'green')
    colors = cycle(['blue', 'magenta', 'cyan', 'yellow', 'white'])
    for url in urls:
        color = next(colors)
        if model == 'openai':
            summary = summarize_url_with_openai(url, color)
        elif model == 'phi':
            summary = summarize_url_with_phi(url, color)
        else:
            print_with_timestamp(f"Unknown model: {model}", 'red')
            return
        with open(output_file, 'a') as f:
            f.write(f'\n{summary}- {url}\n')
        print_with_timestamp(f"Appended summary to {output_file}", 'green')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='The input file containing URLs')
    parser.add_argument('output_file', help='The output file to write summaries')
    parser.add_argument('-m', '--model', help='The model to use for summarization (openai or phi)', default='openai')
    args = parser.parse_args()
    main(args.input_file, args.output_file, args.model)