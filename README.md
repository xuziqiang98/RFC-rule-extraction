# Project Name
RFC (Request for Comments) documents are a series of files that contain information related to Internet protocols, technical standards, operational specifications, etc. 
This project aims to extracting rules from RFCs and detecting inconsistency bugs of protocol implementations based on specific RFCs. 

## Environment
Git clone this repo and enter the directory.
Before run this project, you have to install **conda**, which is a cross-platform package manager.
Suppose that you have already installed **conda**，use the following commands to install the required environment:
`conda env create -f environment.yml`
Then activate environment:
`conda activate rfc2rule`
We use **qwen**, a LLM model supported from Alibaba, to extract rules from RFCs, so you have to apply an API KEY to run those code.
[API]:https://bailian.console.aliyun.com/?apiKey=1#/api-key
After that, configure API KEY to environment variables:
`echo "export DASHSCOPE_API_KEY='YOUR_DASHSCOPE_API_KEY'" >> ~/.bashrc`

## Usage
You can use "--help" to check what options are available:
`python run.py `
For example, use **qwen-max** model to extract rules from **RFC4271**, and save all logs simultaneously.
`python run.py --rfc 4271 --model qwen-max --verbose`