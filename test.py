import logging

import g4f
from g4f.client import Client
import time

# Define the models you want to test



model = 'codellama_70b_instruct'
# List to store results
results = []

logging.info(f'''
    =========********=========
    Starting for {model}......
    =========********=========
    ''')

# Get a list of working providers
working_providers = [
    provider.__name__
    for provider in g4f.Provider.__providers__
    if provider.working
]

# Initialize the client
client = Client()

# Iterate through each model and provider and get the response

for provider in working_providers:
        start_time = time.time()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "hi, how are you"}],
                provider=provider,
            )
            end_time = time.time()
            elapsed_time = end_time - start_time
            response_content = response.choices[0].message.content
            results.append(f"Model: {model}\nProvider: {provider}\nResponse: {response_content}\nTime taken: {elapsed_time:.2f} seconds\n")
        except Exception as e:
            elapsed_time = time.time() - start_time
            results.append(f"Model: {model}\nProvider: {provider}\nError: {str(e)}\nTime taken: {elapsed_time:.2f} seconds\n")

# Save results to a text file
with open('model_responses.txt', 'a') as file:
    for result in results:
        file.write(result + "\n")

print("Results saved to model_responses.txt")
