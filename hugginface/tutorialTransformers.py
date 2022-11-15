''' https:--huggingface.co/docs/datasets/use_dataset
#PREPROCESS
'''

from transformers import AutoTokenizer
from datasets import load_dataset
from pprint import pprint

# Tokenize text
###############
# the tokenizer corresponding to a pretrained BERT model. 
# Using the same tokenizer as the pretrained model is important because you want to make sure the text is split in the same way

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
dataset = load_dataset("rotten_tomatoes", split="train")

pprint(tokenizer(dataset[0]["text"]))
# The tokenizer returns a dictionary with three items:

# input_ids: the numbers representing the tokens in the text.
# token_type_ids: indicates which sequence a token belongs to if there is more than one sequence.
# attention_mask: indicates whether a token should be masked or not.

# autre methode plus rapide: declarer une methode tokenization et la fonction map
# pour ajouter le preprocess au dataset
def tokenization(example):
    return tokenizer(example["text"])


dataset = dataset.map(tokenization, batched=True)

pprint(dataset)

# format of your dataset to be compatible with your machine learning framework

# Pytorch / torch

dataset.set_format(type="torch", columns=["input_ids", "token_type_ids", "attention_mask", "labels"])
dataset.format['type']

#ou tensorflow
from transformers import DataCollatorWithPadding

data_collator = DataCollatorWithPadding(tokenizer=tokenizer, return_tensors="tf")
tf_dataset = dataset.to_tf_dataset(
    columns=["input_ids", "token_type_ids", "attention_mask"],
    label_cols=["labels"],
    batch_size=2,
    collate_fn=data_collator,
    shuffle=True
)

# preprocess Resample audio signals
from transformers import AutoFeatureExtractor
from datasets import load_dataset, Audio

feature_extractor = AutoFeatureExtractor.from_pretrained("facebook/wav2vec2-base-960h")
dataset = load_dataset("PolyAI/minds14", "en-US", split="train")