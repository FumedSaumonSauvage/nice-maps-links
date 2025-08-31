import os
import re
import requests
from urllib.parse import urlparse
from llama_cpp import Llama

# Simple class to infer a model

class Inferencer:

    def __init__(self, model_link: str, n_gpu_layers: int = 35):
        # Model link: may be a path
        # n_gpu_layers : max number of layers on gpu 
        self.model = None
        self.model_path = model_link

        # Check if model is url or local
        if urlparse(model_link).scheme in ['http', 'https']:
            print(f"Online model found, downloading.")
            
            filename = os.path.basename(urlparse(model_link).path) # Extraction of filename through URL
            self.model_path = os.path.join(os.getcwd(), filename)

            if not os.path.exists(self.model_path):
                try:
                    with requests.get(model_link, stream=True) as r:
                        r.raise_for_status()
                        with open(self.model_path, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)

                    print(f"Model downloaded to {self.model_path}")
                except Exception as e:
                    print(f"Error:{e}")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        try:
            print(f"Loading model {self.model_path} with {n_gpu_layers} max gpu layers.")

            self.model = Llama(
                model_path=self.model_path,
                n_gpu_layers=n_gpu_layers,
                n_ctx=4096,
                verbose=False
            )

            print("Model loaded.")
        except Exception as e:
            print(f"Error: {e}")

    def infer(self, prompt: str, max_tokens: int = 256) -> str:

        if not self.model:
            return "Model not loaded!"

        print("Performing inference")
        try:
            formatted_prompt = f"Q: {prompt} A:" # Llama cpp formatting
            
            output = self.model(
                formatted_prompt, 
                max_tokens=max_tokens, 
                stop=["Q:", "\n"], 
                echo=False
            )
            
            generated_text = output['choices'][0]['text']
            cleaned_text = re.sub(r'A:\s*', '', generated_text, 1).strip() # cleanup to rm prompt
            
            return cleaned_text
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":

    local_model_path = "assets/mistral-7b-v0.1.Q4_K_S.gguf"
    
    try:
        inferencer = Inferencer(model_link=local_model_path, n_gpu_layers=35)
        
        test_prompt = "Quelle est la couleur du ciel?"
        response = inferencer.infer(prompt=test_prompt)
        print("\nGenerated Response:")
        print(response)

    except Exception as e:
        print(f"Error: {e}")
