import os
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch

MODEL_NAME = "meta-llama/Llama-2-13b-hf"

def load_model(model_name=MODEL_NAME):
    """
    Downloads and loads the model into memory
    """
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

    if not HUGGINGFACE_TOKEN:
        raise ValueError("HUGGINGFACE_TOKEN is not set. Please set it as an environment variable.")

    print(f"Loading model {model_name} into RAM...")

    tokenizer = AutoTokenizer.from_pretrained(model_name, token=HUGGINGFACE_TOKEN)
    tokenizer.pad_token = tokenizer.eos_token

    # Handle CPU vs GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Only use quantization if on GPU
    quantization_config = None
    if device == "cuda":
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16
        )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto" if device == "cuda" else None,
        quantization_config=quantization_config if device == "cuda" else None,
        token=HUGGINGFACE_TOKEN
    )

    model.to(device)  # Move model to CPU/GPU
    print(f"Model loaded into {device.upper()} successfully.")
    return tokenizer, model, device
