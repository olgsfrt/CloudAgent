import os
import logging
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, MetricsQueryClient
from datetime import timedelta
import openai

# Configure OpenAI and logging
openai.api_key = os.getenv('OPENAI_API_KEY')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set up Azure credentials and clients
credential = DefaultAzureCredential()
logs_client = LogsQueryClient(credential)
metrics_client = MetricsQueryClient(credential)

# Azure Monitor resource details
resource_id = "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{vm_name}"

def collect_azure_monitor_logs(query, duration=timedelta(days=1)):
    """
    Collect logs from Azure Monitor for the specified duration.

    :param query: Kusto Query Language (KQL) query string.
    :param duration: Time duration to query logs, default is last 1 day.
    :return: Logs result.
    """
    try:
        response = logs_client.query_workspace(os.environ["AZURE_MONITOR_WORKSPACE_ID"], query, timespan=duration)
        return response.tables[0].rows
    except Exception as e:
        logging.error(f"Failed to collect Azure Monitor logs: {e}")
        return []

def collect_azure_monitor_metrics(metric_name, duration=timedelta(days=1)):
    """
    Collect specified metrics from Azure Monitor for the specified duration.

    :param metric_name: Name of the metric to collect.
    :param duration: Time duration to query metrics, default is last 1 day.
    :return: Metrics result.
    """
    try:
        response = metrics_client.query_resource(resource_id, metric_names=[metric_name], timespan=duration)
        return response.metrics[0].timeseries[0].data
    except Exception as e:
        logging.error(f"Failed to collect Azure Monitor metrics: {e}")
        return []

def analyze_logs_with_gpt(logs):
    """
    Analyze the given logs with GPT and return a summary.

    :param logs: List of log entries to summarize.
    :return: Summary of the logs.
    """
    try:
        log_summary_prompt = f"Summarize the following logs: {logs}"
        summary = openai.Completion.create(prompt=log_summary_prompt, model="text-davinci-003")
        return summary.choices[0].text
    except Exception as e:
        logging.error(f"Failed to analyze logs with GPT: {e}")
        return "Analysis failed."

def main():
    # Customized queries for monitoring a web app
    logs_query = "AppServiceHTTPLogs | where TimeGenerated > ago(24h) | where StatusCode >= 400 | project TimeGenerated, StatusCode, RequestURL, Details"
    metrics_query = "Percentage CPU | where TimeGenerated > ago(24h) | project TimeGenerated, Average"

    try:
        logs = collect_azure_monitor_logs(logs_query)
        if logs:
            summary = analyze_logs_with_gpt(logs)
            print(f"Log Summary: {summary}")
        else:
            print("No logs to analyze.")

        metrics = collect_azure_monitor_metrics("CpuPercentage")
        print("Metrics:", metrics)
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
