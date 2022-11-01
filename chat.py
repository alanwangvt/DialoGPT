import torch

from transformers import (
    MODEL_WITH_LM_HEAD_MAPPING,
    WEIGHTS_NAME,
    AdamW,
    AutoConfig,
    AutoModelWithLMHead,
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    get_linear_schedule_with_warmup,
)
class Chatbot:
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained('microsoft/DialoGPT-large')
        # model = AutoModelWithLMHead.from_pretrained('bit4444-medium-n3')
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-large")
        self.step = 0
        self.chat_history_ids = None

    def output():
        return "hahaha"
        
    def get_response(self, raw_text):  
        # Let's chat continuously
        # encode the new user input, add the eos_token and return a tensor in Pytorch
        new_user_input_ids = self.tokenizer.encode(raw_text + self.tokenizer.eos_token, return_tensors='pt')
        # print(new_user_input_ids)

        # append the new user input tokens to the chat history
        bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1) if self.step > 0 else new_user_input_ids

        # bot_input_ids = new_user_input_ids
        # print(bot_input_ids)
        # generated a response while limiting the total chat history to 1000 tokens, 
        self.chat_history_ids = self.model.generate(
            bot_input_ids, max_length=1000,
            pad_token_id=self.tokenizer.eos_token_id,
            top_p=0.92, top_k = 10
        )

        # self.chat_history_ids = self.model.generate(
        #     bot_input_ids, max_length=1000,
        #     pad_token_id=self.tokenizer.eos_token_id,  
        #     no_repeat_ngram_size=3,       
        #     do_sample=True, 
        #     top_k=50, 
        #     top_p=0.7,
        #     temperature = 0.3
        # )

        # pretty print last ouput tokens from bot
        out_text = self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        self.step += 1 
        return out_text

def getInstance():
    newChatbot = Chatbot()
    return newChatbot

def getInstanceResponse(chatbotinstance, raw_text):
    return chatbotinstance.get_response(raw_text)