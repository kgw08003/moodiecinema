import os
import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer

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

# 모델 로드 및 감정 예측 함수
def load_model():
    bert = BertModel.from_pretrained('bert-base-multilingual-cased')
    model = BERTGRUSentiment(bert, hidden_dim=256, output_dim=1, n_layers=2, bidirectional=True, dropout=0.25)

    # 현재 파일의 위치를 기준으로 모델 파일 경로 설정
    model_path = os.path.join(os.path.dirname(__file__), 'tut6-model.pt')
    model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
    model.eval()
    return model

model = load_model()
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

def predict_sentiment(sentence):
    # 감정 키워드와 대응되는 가중치 조정 값
    keywords = {
        "슬픔": [
            "슬프다", "우울", "눈물", "상심", "고통", "외롭다", "아프다", "상처", "힘들다", "괴롭다", 
            "실망", "절망", "후회", "허탈", "낙담", "비통", "좌절", "상실", "비참", "씁쓸하다",
            "고독", "절망적", "고립", "우울감", "불행", "포기", "기진맥진", "무기력", "애석하다",
            "의지 상실", "절망에 빠지다", "의미 없음", "기진하다", "생기 없다", "상실감", "염세적", 
            "비관적", "고독감", "눈물 흘리다", "절망의 나락", "우울한 마음", "감정적 피로", "연민", 
            "마음이 무겁다", "소외감", "허무", "공허함", "외로이", "비애", "쓸쓸하다", "비극적", 
            "고뇌", "우울하다", "좌절감", "지쳐 있다", "괴로움", "속상하다", "마음이 아프다"
        ],
        "공포": [
            "두렵다", "무섭다", "위험", "불안", "공포", "긴장", "겁나다", "무서운", "공황", "혼란", 
            "불쾌감", "초조", "걱정", "소름", "긴장되다", "심장 떨리다", "충격적", "겁먹다", "비명",
            "불안감", "겁에 질리다", "조마조마", "두려움", "놀라다", "불길하다", "무서움", "피하다", 
            "위축", "불안정", "두려운 마음", "위협받다", "위협적", "무섭게 느껴지다", "식은땀", 
            "불신", "미칠 것 같은 공포", "기피", "부정적 기대", "몸서리", "심각한 걱정", "비관", 
            "소름 끼치다", "겁에 사로잡히다", "불편함", "어둠 속에서 떨다", "초조함", "불쾌하다", 
            "위험할 수 있다", "무방비 상태", "긴장 상태", "두려움에 떨다", "떨리는 마음", "도망가다"
        ],
        "분노": [
            "화가", "짜증", "분노", "폭발", "열받다", "답답", "분통", "폭력", "미치다", "짜증나다", 
            "약오르다", "성질", "짜증스러운", "분개", "분노하다", "격분", "열받아", "불쾌", "열정",
            "불쾌하다", "화를 내다", "분노의", "억울하다", "울분", "분노가 치밀다", "불만", "비난", 
            "욕설", "화가 치밀다", "불만스럽다", "거슬리다", "분노의 감정", "짜증 폭발", "불쾌함", 
            "화가 치솟다", "원한", "맹렬히 화나다", "증오", "격한 감정", "부글부글 끓다", "분함", 
            "열받는다", "복수하고 싶다", "이성을 잃다", "심하게 화나다", "불평", "불만족", "충돌", 
            "공격적", "짜증 섞인 말", "분노에 차오르다", "분기탱천", "소리 지르다", "화를 참지 못하다"
        ],
        "평온": [
            "편안", "차분", "안정", "평화", "평온", "조용", "고요", "여유", "느긋하다", "편하다", 
            "행복감", "평안", "잔잔", "안도", "차분한", "안정감", "평온한", "평화롭다", "안정적인", 
            "느긋", "평화로운", "한가하다", "포근하다", "부드럽다", "평정심", "온화하다", "조화", 
            "무사", "마음이 편하다", "따뜻하다", "안정된 마음", "안정된 상태", "진정되다", "휴식", 
            "차분하게", "느긋한 미소", "행복한 순간", "마음의 평화", "마음의 안정", "포근한 느낌", 
            "편안한 분위기", "편안함을 느끼다", "편안한 미소", "평화로움", "차분한 시간", "평온한 하루", 
            "온화한 마음", "평화로워지다", "진정한 행복", "심신의 평화", "조용히 흐르다", "마음의 여유"
        ],
        "기쁨": [
            "기쁘다", "행복", "즐겁다", "감사", "사랑", "신난다", "기분좋다", "만족", "즐거운", "흥분", 
            "행복하다", "기쁨", "웃음", "재밌다", "환희", "희열", "즐거움", "행복해", "감동", "사랑스럽다", 
            "만족하다", "행복한 순간", "재미있다", "충만하다", "유쾌하다", "감격", "행복감", "고마움", 
            "행복한 시간", "마음이 따뜻하다", "미소 짓다", "웃음을 주다", "즐거운 하루", "신나는 경험", 
            "행복의 웃음", "만족감", "기쁨을 느끼다", "기쁨의 순간", "사랑스러움", "웃음소리", "행복한 날", 
            "기분이 좋다", "즐거운 일상", "만족스러운 시간", "감사함을 느끼다", "행복한 미소", "신나는 일", 
            "재미있는 시간", "기쁨을 표현하다", "행복하게 웃다", "유쾌한 대화", "사랑의 느낌", "행복한 기억"
        ],
    }

    weight_adjustment = 0  # 기본 가중치 조정 값
    for emotion, words in keywords.items():
        if any(word in sentence for word in words):
            if emotion == "슬픔":
                weight_adjustment -= 0.1
            elif emotion == "공포":
                weight_adjustment -= 0.05
            elif emotion == "분노":
                weight_adjustment += 0.1
            elif emotion == "평온":
                weight_adjustment += 0.05
            elif emotion == "기쁨":
                weight_adjustment += 0.1

    # 텍스트를 토크나이징하고 모델로 예측 수행
    tokens = tokenizer.tokenize(sentence)
    tokens = tokens[:tokenizer.model_max_length - 2]
    indexed = [tokenizer.cls_token_id] + tokenizer.convert_tokens_to_ids(tokens) + [tokenizer.sep_token_id]
    tensor = torch.LongTensor(indexed).unsqueeze(0)
    
    with torch.no_grad():
        prediction = torch.sigmoid(model(tensor)).item()
    
    # 키워드 가중치를 예측 값에 반영
    adjusted_prediction = prediction + weight_adjustment
    adjusted_prediction = max(0, min(adjusted_prediction, 1))  # 예측 값은 0과 1 사이로 제한

    # 조정된 감정 범위
    if adjusted_prediction <= 0.2:
        return "슬픔"
    elif 0.2 < adjusted_prediction <= 0.35:
        return "공포"
    elif 0.35 < adjusted_prediction <= 0.65:
        return "분노"
    elif 0.65 < adjusted_prediction <= 0.8:
        return "평온"
    else:
        return "기쁨"
