## SK Financial Analyst

SK Financial Analyst is a Python-based financial health analysis tool that leverages Semantic Kernel, external APIs, and Large Language Models (LLMs) to analyze financial statements, news articles, and stock prices to generate a consolidated financial health report of public companies.

### Features

- **News Analysis**: Analyze sentiment in financial news articles related to a company's stock ticker.
- **Financial Statement Analysis**: Analyze balance sheet, income statement, and cash flow reports.
- **Consolidated Report**: Generate a structured consolidated report, following a pre-defined JSON schema, combining financial statement and news analyses.

### Modules

- `assistants/assistants.py`: Defines assistants such as NewsAnalyst, FinancialAnalyst, and StructuredReportGenerator that perform specific analysis tasks.
- `assistants/data_models.py`: Defines Pydantic data models used for structured data representation.
- `plugins/plugins.py`: Implements plugins for fetching data from external APIs, such as Bing News Search, Yahoo Finance, and SEC Edgar filings.
- `utils/config_reader.py`: Reads YAML configuration files.
- `utils/report_generator.py`: Converts JSON reports to markdown format.

### Architecture

Here is a diagram showing a high-level architecture:

![Architecture Diagram](./architecture.png)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/sk_financial_analyst.git
   cd sk_financial_analyst

2. Set up a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

### Configuration

#### config.yaml

Before running the code, create the `sk_financial_analyst/llm_application/config.yaml` file, using the provided `sk_financial_analyst/llm_application/config_sample.yaml` as example, and enter the needed values for your resource endpoints and deployment names.

You need only to enter the Azure OpenAI model deployment names in your Azure OpenAI service you want to use for each assistant, as well as your Azure Key Vault endpoint.

#### Azure Key Vault

You need to have access to an Azure Key Vault where you can write and read secrets. Follow [this instructions](https://learn.microsoft.com/en-us/azure/key-vault/general/quick-create-portal) if you need to create one.

You need to create two secrets:
- `AOAI-BASE-ENDPOINT`: this is the base endpoint of your Azure OpenAI deployment.
- `SEC-IDENTITY`: this is an identity in the form of `<your name> <your email address>` that is needed for the application to make requests to the SEC Edgar database to get financial statements.

Follow [this documentation](https://learn.microsoft.com/en-us/azure/key-vault/general/security-features#controlling-access-to-key-vault-data) to learn how to configure access for reading / writing secrets in Azure Key Vault.

#### Azure OpenAI

You need to have access to an Azure OpenAI service and have at least one model deployed. We suggest to use `gpt-4o`. Follow [this instructions](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/create-resource) if you need to create one.

#### Bing Search

You need to have access to a Bing Search service API. Follow [this instructions](https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/create-bing-search-service-resource) if you need to create one.

### Running the Code

The code uses an Azure Managed Identity Credential to get tokens to access the Azure OpenAI service and Azure Key Vault. It was tested running from `VSCode` authenticating to Azure.

When running the main Python script, you generate two consolidated financial health analysis for a public company: one as a structured JSON output, following a pre-defined schema, and a markdown version generated from it. To run the code, go to the `sk_financial_analyst` folder, and execute:

```bash
python llm_application/financial_health_analysis.py <STOCK_TICKER> <OUTPUT_FOLDER>
```

`<STOCK_TICKER>` and `<OUTPUT_FOLDER>` are set by default to `MSFT` and `./data/outputs`, respectively.

`sk_financial_analyst/data/outputs` is already populated with some example reports.


