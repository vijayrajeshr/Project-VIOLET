import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

class VioletBrain:
    def __init__(self, model_id="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"):
        print(f"VIOLET: Waking up DeepSeek R1 brain {model_id}...")
        
        # 4-bit configuration (keeps it lightweight)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4"
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            quantization_config=bnb_config,
            device_map="auto", # Automatically uses GPU if you have one
            trust_remote_code=True
        )
        print("VIOLET: Synapse ready.")

    def think(self, prompt):
        messages = [
            {"role": "system", "content": "You are VIOLET, a highly capable AI assistant created by Vijay. Be concise and execute commands effectively."},
            {"role": "user", "content": prompt}
        ]
        
        input_ids = self.tokenizer.apply_chat_template(
            messages, 
            add_generation_prompt=True, 
            return_tensors="pt"
        ).to(self.model.device)
        
        outputs = self.model.generate(
            input_ids,
            max_new_tokens=150,
            temperature=0.6,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )
        
        response_tokens = outputs[0][input_ids.shape[-1]:]
        response = self.tokenizer.decode(response_tokens, skip_special_tokens=True)
        
        # DeepSeek R1 Distill models often output <think> tags. Let's clean it up slightly if needed, or just return.
        # Returning clean response.
        return response.strip()

# Initialize
# violet = VioletBrain()
