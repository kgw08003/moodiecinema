import os
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer
from konlpy.tag import Okt
from django.conf import settings

# 형태소 분석기
okt = Okt()

# 모델 클래스 정의
class BERTGRUSentiment(nn.Module):
    def __init__(self, bert, hidden_dim, output_dim, n_layers, bidirectional, dropout):
        super().__init__()
        self.bert = bert
        embedding_dim = bert.config.to_dict()['hidden_size']
        self.rnn = nn.GRU(embedding_dim, hidden_dim,
                          num_layers=n_layers,
                          bidirectional=bidirectional,
                          batch_first=True,
                          dropout=0 if n_layers < 2 else dropout)
        self.out = nn.Linear(hidden_dim * 2 if bidirectional else hidden_dim, output_dim)
        self.dropout = nn.Dropout(dropout)

    def forward(self, text):
        with torch.no_grad():
            embedded = self.bert(text)[0]
        _, hidden = self.rnn(embedded)
        if self.rnn.bidirectional:
            hidden = self.dropout(torch.cat((hidden[-2, :, :], hidden[-1, :, :]), dim=1))
        else:
            hidden = self.dropout(hidden[-1, :, :])
        output = self.out(hidden)
        return output

# 모델 파일 경로
MODEL_PATH = os.path.join(settings.BASE_DIR, "moodiecinema", "tut6-model.pt")

# 모델 로드 함수
def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    
    bert = BertModel.from_pretrained('bert-base-multilingual-cased')
    model = BERTGRUSentiment(bert, hidden_dim=256, output_dim=1, n_layers=2, bidirectional=True, dropout=0.25)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=torch.device('cpu')))
    model.eval()  # 평가 모드로 전환
    return model

# 모델 및 토크나이저 로드
model = load_model()
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

# 감정 예측 함수
def predict_sentiment(sentence):
    keywords = {
        "슬픔": ["슬프다", "우울하다", "눈물", "상심하다", "고통스럽다", "외롭다", "상처", "힘들다", "괴롭다", "실망하다", "절망하다", "허탈하다", "낙담하다", "비통하다"],
        "공포": ["두렵다", "무섭다", "위험하다", "불안하다", "공포", "긴장", "긴장하다", "겁나다", "공황", "혼란스럽다", "초조하다", "걱정하다", "충격적이다", "두려움"],
        "분노": ["화가 나다", "짜증나다", "분노하다", "폭발하다", "열받다", "답답하다", "분통하다", "폭력적이다", "약오르다", "성질", "분개하다", "격분하다", "불쾌하다"],
        "평온": ["편안하다", "차분하다", "안정적이다", "평화롭다", "고요하다", "여유롭다", "행복감", "잔잔하다", "안도하다", "느긋하다", "온화하다", "조화롭다", "무사하다"],
        "기쁨": ["기쁘다", "행복하다", "즐겁다", "감사하다", "사랑스럽다", "신난다", "만족하다", "흥분하다", "웃다", "재밌다", "환희", "희열", "고마움", "미소"],
    }

    # 형태소 분석으로 명사와 동사 추출
    tokens = [token for token in okt.morphs(sentence, stem=True) if len(token) > 1]
    print(f"형태소 분석 결과 tokens: {tokens}")
    
    # 모델 예측 값 계산
    model_tokens = tokenizer.tokenize(sentence)
    model_tokens = model_tokens[:tokenizer.model_max_length - 2]
    indexed = [tokenizer.cls_token_id] + tokenizer.convert_tokens_to_ids(model_tokens) + [tokenizer.sep_token_id]
    tensor = torch.LongTensor(indexed).unsqueeze(0)

    with torch.no_grad():
        prediction = torch.sigmoid(model(tensor)).item()
    print(f"모델의 기본 예측 값 (가중치 조정 전): {prediction}")

    # 가중치 조정
    weight_adjustment = 0
    for emotion, words in keywords.items():
        match_count = sum(tokens.count(word) for word in words)  # 토큰에서 키워드 단어 등장 횟수 합산
        print(f"{emotion} match_count: {match_count}")
        
        if match_count > 0:
            if emotion == "슬픔":
                weight_adjustment -= 0.65 * match_count
            elif emotion == "공포":
                weight_adjustment -= 0.55 * match_count
            elif emotion == "분노":
                weight_adjustment += 0.55 * match_count
            elif emotion == "평온":
                weight_adjustment -= 0.25 * match_count
            elif emotion == "기쁨":
                weight_adjustment += 0.4 * match_count

    # 가중치를 적용한 최종 예측 값 계산
    adjusted_prediction = prediction + weight_adjustment
    adjusted_prediction = max(0, min(adjusted_prediction, 1))
    print(f"조정된 예측 값: {adjusted_prediction}")

    # 감정 범위에 따라 최종 예측 감정 반환
    if adjusted_prediction <= 0.3:
        return "슬픔"
    elif 0.3 < adjusted_prediction <= 0.5:
        return "공포"
    elif 0.5 < adjusted_prediction <= 0.65:
        return "분노"
    elif 0.65 < adjusted_prediction <= 0.8:
        return "평온"
    else:
        return "기쁨"
