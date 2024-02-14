import os
import argparse
import openai
from src.utils.chat_utils import aws_architecture_to_be_evaluated  # Assuming this is a provided function
from src.utils.general_utils import collect_cloudwatch_logs  # Assuming this is a provided function
from azure.monitor.query import LogsQueryClient
from azure.identity import DefaultAzureCredential

# Set OpenAI API key and Azure credentials
openai.api_key = os.getenv('OPENAI_API_KEY')
azure_credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential=azure_credential)

# Environment Variables for AWS
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_DEFAULT_REGION')
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')

# Environment Variable for Azure Log Analytics Workspace ID
azure_workspace_id = os.getenv('AZURE_LOG_ANALYTICS_WORKSPACE_ID')

def collect_azure_monitor_logs(query, timespan="P1D"):
    """
    Collect logs from Azure Monitor for the specified duration.

    :param query: Kusto Query Language (KQL) query string.
    :param timespan: The timespan over which to query. Defaults to "P1D" (one day).
    :return: Logs result.
    """
    try:
        response = logs_client.query_workspace(workspace_id=azure_workspace_id, query=query, timespan=timespan)
        return response.tables[0].rows
    except Exception as e:
        print(f"Failed to collect Azure Monitor logs: {e}")
        return []
def azure_architecture_to_be_evaluated(main_prompt, text_prompt, azure_monitor_logs, iteration):
    """
    Evaluates Azure architecture by sending prompts to GPT along with Azure Monitor logs.

    :param main_prompt: The main prompt describing the task or the question for GPT.
    :param text_prompt: Additional context or questions provided to GPT.
    :param azure_monitor_logs: Logs collected from Azure Monitor that might include metrics or messages.
    :param iteration: The iteration number if the function is being called multiple times.
    :return: GPT's response text evaluating or describing the Azure architecture.
    """

    # Combine the main prompt, text prompt, and formatted Azure logs into a single string.
    formatted_logs = format_azure_monitor_logs_for_gpt(azure_monitor_logs)
    combined_prompt = f"{main_prompt}\nLogs:\n{formatted_logs}\n{text_prompt}"

    # Here you would call OpenAI's GPT model using the combined prompt.
    # For example:
    try:
        response = openai.Completion.create(
            prompt=combined_prompt,
            model="text-davinci-003",  # Replace with the appropriate model
            max_tokens=150  # Adjust as needed
        )
        return response.choices[0].text.strip()
    except Exception as error:
        print(f"Error in GPT response: {error}")
        return "GPT evaluation failed."

def main(text, cloud_provider):
    main_prompt = text
    first_iteration = 0

    while first_iteration < 11:
        try:
            first_iteration += 1
            if cloud_provider == 'aws':
                cloud_logs = collect_cloudwatch_logs()
                code_response_body = aws_architecture_to_be_evaluated(
                    main_prompt=main_prompt, text_prompt=text, cloud_watch_logs=cloud_logs, iteration=first_iteration
                )
            elif cloud_provider == 'azure':
                # Example Azure Monitor KQL query
                azure_query = "AzureActivity | summarize count() by bin(timestamp, 1h), ResourceGroup | order by timestamp desc"
                cloud_logs = collect_azure_monitor_logs(azure_query)
                code_response_body = azure_architecture_to_be_evaluated(
                    main_prompt=main_prompt, text_prompt=text, azure_monitor_logs=cloud_logs, iteration=first_iteration
                )
            else:
                raise ValueError("Invalid cloud provider specified. Choose 'aws' or 'azure'.")
            
            print("Operation completed without errors.")
            break  # If no exception is caught, exit the loop

        except Exception as error:
            print("Caught an error:", error)
            text = error

    print(f"Final code: {code_response_body}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Describe the cloud architecture that you want to deploy:")
    parser.add_argument("text", type=str, help="Text to pass to the script")
    parser.add_argument("--cloud_provider", type=str, choices=['aws', 'azure'], required=True,
                        help="The cloud provider for which to evaluate the architecture.")
    args = parser.parse_args()
    
    main(args.text, args.cloud_provider)

