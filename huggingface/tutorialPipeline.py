# https://youtu.be/QEaBAZQCtwE?si=54VBPnm8k1Ho37Sv

from transformers import pipeline

classifier = pipeline("sentiment-analysis")

res = classifier ("I've been waiting so long to get this result")

print(res)

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

res=classifier("I 've been waiting for a HuggingFac course my whole life")

print(res)

sequence="Using a transformer network is simple"
res= tokenizer(sequence)
print(res)
tokens= tokenizer.tokenize(sequence)
print(tokens)
ids=tokenizer.convert_tokens_to_ids(tokens)
print(ids)
decoded_string=tokenizer.decode(ids)
print(decoded_string)