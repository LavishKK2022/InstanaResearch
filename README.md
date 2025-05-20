# AIOPTIM

Artificial intelligence optimiser (AIOPTIM) is a backend performance optimisation tool. This tool uses static analysis, dynamic analysis, and deep learning to identify endpoints experiencing performance degradation. Subsequently, this tool uses generative artificial intelligence to offer resolutions for the identified endpoints. These changes are pushed back to the repository in a separate branch. 

This tool relies on several components, such as IBM's Instana application monitoring tool, an Ollama server and a web server. Below is a guide describing how to run this tool in a macOS 15+ environment. While this tool has been tested on Windows 10+, it is currently unstable.

This tool supports optimising

* Java frameworks such as Spring Boot
* Python frameworks such as Flask and Fast API

This folder contains:

* The tool's source code
* The deep learning model's training code

## Hardware 

* MacOS (Apple Silicon)
* AWS EC2 (t2.medium, 30GB, Amazon Linux 2)
* Cloud GPU (DigitalOcean, Paperspace and Vast.ai)

## Software

* Python 3
* IBM Instana 
* GitHub

## Preliminary Setup

### GitHub

* Fork this [repository](https://github.com/LavishKK2022/priv-robot-shop
).
* Create a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token), granting read and write access to the forked repository.

### AWS EC2

* Create an AL2 EC2 t2.medium instance with 30GB storage space
* SSH into the EC2 instance
* Install and start the [Docker Engine](https://docs.docker.com/engine/install/)
* Pull the forked repository
* Change directories into the repository and run 

```bash
docker-compose up -d
```

* Start the load generation service in the background:

```bash
./load-gen/load-gen.sh
```

* Retrieve the docker agent command from the 'Deploy Agent' part of the Instana dashboard.
* Inside the EC2 instance, run the docker command to start the Instana agent.

### IBM Instana

* Create an [application perspective](https://www.ibm.com/docs/en/instana-observability/current?topic=applications-application-perspectives), ensuring the filter is the host/IP of the running EC2 instance.
* If the application perspective does not update after a few minutes, it may be necessary to kill the process running on port 42699 of the EC2 instance. 
* Create a [personal API token.](https://www.ibm.com/docs/en/instana-observability/current?topic=apis-instana-rest-api#creating-personal-api-tokens)

### Ollama Server

* Create an [Ollama server](https://ollama.com/download/linux) on a cloud GPU platform.
* Ensure that Ollama is [listening on 0.0.0.0](https://www.restack.io/p/ollama-knowledge-ollama-host-0-0-0-0-cat-ai), as opposed to the loopback address 127.0.0.1
* Ensure that port 11434 on the server is exposed. 
* Pull a model into the Ollama server (preferably [qwen2.5-coder:32b](https://ollama.com/library/qwen2.5-coder
))
* Ensure that a [local curl request](https://github.com/ollama/ollama/blob/main/docs/api.md) can be made to the GPU server.

## Using the Tool

In the project's folder, there is a file ending with the 'whl' extension.

Within the same folder:

* Create and source a Python3 environment.
* Run the command below to install the tool. 

```bash
pip install aioptim-1.0.0-py3-none-any.whl
```

Upon installation of the tool, the following commands become available:

```bash
aioptim --help
aioptim start --help
aiotpim setup --help
```

### Setup

To set up the tool, run the following command:

```bash
aioptim setup
```

### Start

Before starting the tool, on a new terminal window, the following command can be run to start a localhost visualisation dashboard on port 4200:

```bash
prefect server start
```

To start the tool, run this command with parameters for the :

* Threshold: upper bound of acceptable endpoint latency (milliseconds)
* Delay: how often to run the process (minutes)

```bash
aioptim start <threshold> <delay>`
```

This begins the process of locating and resolving slow endpoints. After some time the repository will update with new branches indicating the changes made by the generative models.

## Testing

Within the folder, there is a subdirectory titled 'ToolSource'. This file contains the source code for the tool. The following instruction can be run within the repository to run unit tests:

```bash
pytest
```