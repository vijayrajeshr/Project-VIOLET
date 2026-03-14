import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class VioletBrain:
    def __init__(self, model_id="unsloth/phi-4-mini"):
        print(f"VIOLET: Waking up brain {model_id}...")
        
        # 4-bit configuration (keeps it lightweight)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4"
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            quantization_config=bnb_config,
            device_map="auto" # Automatically uses GPU if you have one
        )
        print("VIOLET: Synapse ready.")

    def think(self, prompt):
        inputs = self.tokenizer(f"Vijay: {prompt}\nVIOLET:", return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=100)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True).split("VIOLET:")[-1].strip()

# Initialize
# violet = VioletBrain()
