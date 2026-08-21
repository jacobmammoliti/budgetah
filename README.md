# Budgetah

A personal budgeting application used for AI learning and demo purposes.

## Components

### Backend API

The backend API is the backbone of the application. It contains all the logic for a personal budgeting application and ships with a SQLlite database. It is written in Python and uses [FastAPI](https://github.com/fastapi/fastapi) amongst other Python libraries.

### MCP Server

The MCP server acts an intermediary between the backend API and the LLM. It provides an entrypoint with well-defined tools to help answer questions about the budget data. It is written in Python and uses [FastMCP](https://github.com/PrefectHQ/fastmcp).

### Llama.cpp

[Llama.cpp](https://github.com/ggml-org/llama.cpp) is an LLM inference tool and is used here to provide a UI so that users can interact with the budget data in natural language. It allows users to ask questions like:

- How much did I spend on groceries this month?
- Give me the top 3 categories of where my spending went in June.

This project uses Google's [Gemma 4 E4B](https://huggingface.co/google/gemma-4-E4B) LLM model.

## How to Run

The easiest way to run this is to build all the container images separetely with their respective Makefile and then run them via the Docker Compose file. The steps are provided below:

> *Note:* I run these workloads on an Intel-GPU backed server so that's why I build the the Intel specific Dockerfile.

> *Note:* The Makefiles use Podman to build the images. If you use Docker or build images in some other way, either build without the Makefile or modify appropriately. Same with `CONTAINER_REGISTRY`.

```bash
# Build backend image
cd backend && make build && cd ..

# Build MCP server image
cd mcp && make build && cd ..

# Get back to home directory
cd ~

# Build Llama.cpp
git clone https://github.com/ggml-org/llama.cpp.git && cd llama.cpp

# Build the Intel GPU-enabled container image
# GGML_SYCL_F16 uses 16-bit floats for calculations —
# faster and less VRAM, with negligible quality difference in practice.
podman build \
--tag llama-cpp-sycl:$(git rev-parse --short HEAD) \
--build-arg="GGML_SYCL_F16=ON" \
--target server \
--file .devops/intel.Dockerfile .

# Modify the docker-compose file as required and then stand up the application
podman compose up
```