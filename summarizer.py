import os
import sys
import requests
import argparse
from bs4 import BeautifulSoup
from openai import OpenAI, OpenAIError
import json
from datetime import datetime
from termcolor import colored
from itertools import cycle

MODEL_MAX_TOKENS = {
    "openai": 128000,
    "mistral": 8000,
    "mixtral": 8000,
    "phi": 2500
}

OpenAI.api_key = os.getenv("OPENAI_API_KEY")

def print_with_timestamp(message, color=None):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(colored(f'[{timestamp}] {message}', color))

def summarize_url_with_openai(url, color, model):
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
    
    max_tokens = MODEL_MAX_TOKENS[model]
    if len(text) <= max_tokens:
        chunks = [text]
    else:
        chunks = [text[i:i + max_tokens] for i in range(0, len(text), max_tokens)]

    client = OpenAI()
    summary = ""
    for chunk in chunks:
        print_with_timestamp(f"Sending chunk to OpenAI model for processing (chunk length: {len(chunk)} characters)...", color)
        print_with_timestamp(f"Text being sent for summarizing: {chunk[-100:]}", color)
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


def summarize_url_with_ollama(url, color, model):
    print_with_timestamp(f"Processing URL: {url} with {model} model", color)
    print_with_timestamp("Sending request to URL...", color)
    try:
        response = requests.get(url)
    except requests.exceptions.SSLError:
        print_with_timestamp("SSL Verification failed. Retrying without SSL Verification...", 'yellow')
        response = requests.get(url, verify=False)
    print_with_timestamp("Response received. Parsing HTML...", color)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()

    max_tokens = MODEL_MAX_TOKENS[model]
    if len(text) <= max_tokens:
        chunks = [text]
    else:
        chunks = [text[i:i + max_tokens] for i in range(0, len(text), max_tokens)]

    summary = ""
    for chunk in chunks:
        print_with_timestamp(f"Sending chunk to {model} model for processing (chunk length: {len(chunk)} characters)...", color)
        print_with_timestamp(f"Text being sent for summarizing: {chunk[-100:]}", color)
        try:
            prompt = f"Generate a markdown formatted summary of the main aspects of this website, with features and useful information. Include a title in '##' format and embed links where necessary. The output should be a maximum 2 paragraphs of text without subsections, but including embedded links where necessary: {chunk}"
            response = requests.post('http://localhost:11434/api/generate', data=json.dumps({
                "model": model,
                "prompt": prompt,
                "stream": False
            }), headers={'Content-Type': 'application/json'})
            response_json = response.json()
            if 'response' in response_json:
                summary += response_json['response'] + "\n\n"
        except Exception as e:
            print_with_timestamp(f"An error occurred: {str(e)}", 'red')

    # Summarize the final summary
    print_with_timestamp("Summarizing the final summary...", color)
    try:
        prompt = f"Generate a markdown formatted summary of the main aspects of this website, with features and useful information. Include a title in '##' format and embed links where necessary. The output should be a maximum 2 paragraphs of text without subsections, but including embedded links where necessary: {summary}"
        response = requests.post('http://localhost:11434/api/generate', data=json.dumps({
            "model": model,
            "prompt": prompt,
            "stream": False
        }), headers={'Content-Type': 'application/json'})
        response_json = response.json()
        if 'response' in response_json:
            summary = response_json['response']
    except Exception as e:
        print_with_timestamp(f"An error occurred while summarizing the final summary: {str(e)}", 'red')

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
            summary = summarize_url_with_openai(url, color, model)
        else:
            summary = summarize_url_with_ollama(url, color, model)
        with open(output_file, 'a') as f:
            f.write(f'\n{summary}- {url}\n')
        print_with_timestamp(f"Appended summary to {output_file}", 'green')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='The input file containing URLs')
    parser.add_argument('output_file', help='The output file to write summaries')
    parser.add_argument('-m', '--model', help='The model to use for summarization (openai or one ollama)', default='openai')
    args = parser.parse_args()
    main(args.input_file, args.output_file, args.model)
