# RFC Rule Extraction System

A structured framework for extracting protocol rules from RFC documents and detecting implementation inconsistencies using Large Language Models (LLMs).

## Features

- Automated RFC document processing and analysis
- Rule extraction using multiple LLM backends:
  - Qwen (Alibaba Cloud)
  - GroqCloud API 
  - Local Ollama deployments
- Implementation consistency verification
- Detailed logging and output generation
- Configurable processing pipelines

## Project Structure

```
.
├── RFC/                  # RFC document storage
├── data/                 # Processed data outputs
├── src/                  # Core source code
│   ├── configs/         # Prompt templates and LLM configurations
│   ├── model.py         # LLM interface implementations
│   └── extraction.py    # Rule extraction logic
├── tests/               # Unit and integration tests
├── environment.yml      # Conda environment specification
└── run.py               # Main execution script
```

## Environment Setup

1. Clone repository and install dependencies:

```bash
git https://github.com/xuziqiang98/RFC-rule-extraction.git
cd rfc-rule-extraction
conda env create -f environment.yml
conda activate rfc2rule
```

2. Configure LLM credentials:

```bash
# For Qwen (Alibaba Cloud)
echo "export DASHSCOPE_API_KEY='YOUR_API_KEY'" >> ~/.zshrc

# For GroqCloud
echo "export GROQ_API_KEY='YOUR_GROQ_KEY'" >> ~/.zshrc

# For Ollama local models
echo "export OLLAMA_HOST='http://localhost:11434'" >> ~/.zshrc
```

Reload shell configuration:
```bash
source ~/.zshrc
```

## Usage

Basic command structure:
```bash
python run.py --rfc <RFC_NUMBER> --model <MODEL_TYPE> [OPTIONS]
```

### Common Options

| Option         | Description                          | Default     |
|----------------|--------------------------------------|-------------|
| `--rfc`        | RFC document number to process      | Required    |
| `--model`      | LLM provider (qwen/groq/ollama)     | qwen-max    |
| `--verbose`    | Enable detailed logging             | False       |
| `--output`     | Output directory path               | ./data      |
| `--max-tokens` | Maximum tokens per request          | 4096        |

### Example Use Cases

1. Basic rule extraction from RFC4271:
```bash
python run.py --rfc 4271 --model qwen-max
```

2. Run with GroqCloud API and debug logging:
```bash
python run.py --rfc 4271 --model groq-llama3-70b --verbose
```

3. Process with local Ollama model:
```bash
python run.py --rfc 4271 --model ollama-llama3 --max-tokens 2048
```

## Development

Contribution guidelines:
- Report issues via GitHub Issues
- Create feature branches from `main`
- Submit PRs with test coverage
- Follow PEP8 coding standards

## License
Distributed under the MIT License. See `LICENSE` for details.
