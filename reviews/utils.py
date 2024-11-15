# from transformers import AutoTokenizer, AutoModelForSequenceClassification
# import torch

# # 감정 분석에 적합한 모델을 사용
# tokenizer = AutoTokenizer.from_pretrained("jason9693/KoBERT-sentiment")
# model = AutoModelForSequenceClassification.from_pretrained("jason9693/KoBERT-sentiment")

# def analyze_sentiment(text, positive_threshold=0.5, negative_threshold=0.5):
#     inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
#     outputs = model(**inputs)
#     scores = outputs.logits.softmax(dim=1)
#     positive_score = scores[0][1].item()
#     negative_score = scores[0][0].item()

#     # 부정어가 있는 경우 부정적 감정 강화
#     if any(word in text for word in ["없다", "싫다", "나쁘다", "별로", "실망"]):
#         negative_score += 0.2

#     # 긍정/부정 판단
#     if positive_score > positive_threshold:
#         return "긍정적"
#     elif negative_score > negative_threshold:
#         return "부정적"
#     else:
#         return "중립적"
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# KcELECTRA 한국어 감정 분석 모델 로드
# tokenizer = AutoTokenizer.from_pretrained("beomi/KcELECTRA-base")
# model = AutoModelForSequenceClassification.from_pretrained("beomi/KcELECTRA-base")

# def analyze_sentiment(text, positive_threshold=0.5, negative_threshold=0.5):
#     inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
#     outputs = model(**inputs)
#     scores = outputs.logits.softmax(dim=1)
#     positive_score = scores[0][1].item()
#     negative_score = scores[0][0].item()

#     if positive_score > positive_threshold:
#         return "긍정적"
#     elif negative_score > negative_threshold:
#         return "부정적"
#     else:
#         return "중립적"
