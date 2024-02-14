import os
import argparse
import openai
# Assuming this function is implemented to evaluate Azure architecture locally
from src.utils.chat_utils import azure_local_architecture_to_be_evaluated

openai.api_key = os.getenv("OPENAI_API_KEY")

# Set environment variables for Azure local development
# For Azurite
os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
# For Azure Functions local development, no specific environment variable is needed, but you should have Azure Functions Core Tools installed.

def main(text):
    main_prompt = text
    first_iteration = 0

    while first_iteration < 11:
        try:
            first_iteration += 1
            # Here, you would interact with Azurite or Azure Functions locally as needed
            # For example, uploading a file to Azurite Blob Storage or invoking a local Azure Function
            # Then, evaluate the architecture using the provided function
            code_response_body = azure_local_architecture_to_be_evaluated(main_prompt=main_prompt, text_prompt=text, iteration=first_iteration)
            print("Operation completed without errors.")
            break  # If no exception is caught, exit the loop

        except Exception as error:
            print("Caught an error:", error)
            text = error

    print(f"Final code: {code_response_body}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Describe the Azure architecture that you want to deploy locally:")
    parser.add_argument("text", type=str, help="Text to pass to the script")
    args = parser.parse_args()
    
    main(args.text)
