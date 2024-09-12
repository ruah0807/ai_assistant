import os
import openai
from init import api_key
from datetime import datetime
import time
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_similar_barnd_names(brand_name):
    prompt = f"""
    '{brand_name}'이라는 상표명칭에 대해 외관, 호칭, 관념 측면에서 유사한 텍스트를 만들어줘.

    1. 검색한 단어와 그 번역본(한글 또는 영어)은 가장 첫 번째로 리스트에 추가해줘. 예를 들어 'mindshare'라는 단어를 검색하면, 'mindshare'와 그 번역본인 '마인드쉐어'를 첫 번째로 포함해줘.
    
    2. 상표명이 합성어인 경우, 합성어를 분리한 각 부분도 검색어로 반드시 포함해줘. 예를 들어 'mindshare'라면 'mind', 'share'를 포함한 검색어를 생성해줘. 또한, 합성어인 'mindshare'와 그 번역본도 결과에 포함해줘.
    
    3. 발음이 유사한 한글과 영어 상표를 포함한 검색어를 만들어줘. 예를 들어 'mindshare'는 '마인드쉐어', 'mindshare'와 같이 영문 및 한글 발음 변환을 포함해줘.

    4. 관념이 유사한 단어들을 추가해줘. 예를 들어 '킹'은 '왕', '퀸'은 '여왕'처럼 의미가 동일하거나 유사한 단어를 포함시켜줘.

    5. 모든 검색어는 중복되지 않도록 생성해줘. 같은 의미나 발음을 가진 단어들은 하나만 남기고 나머지는 제외해줘.

    6. 결과는 JSON 형식으로 출력해줘. 검색어는 words 리스트 안에 고유한 단어들만 포함시켜줘. 검색한 단어와 그 번역본은 가장 첫 번째로 추가해줘(중복 글자 불가):
    {{
    "words": [
        // 8가지를 넘지 않는다.
        // 그 외에 중복 없는 고유한 검색어들
        // 검색한 단어와 번역본이 첫 번째,
    ]
    }}
    """
    start_time = time.time()
    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role":"system", "content":"당신은 유사 검색어를 발췌하는 전문가 입니다."},
            {'role': 'user', 'content': prompt}
        ],
        n=1, # 한번에 하나의 응답 생성
        stop=None, #명시적인 멈춤 신호가 없으면 자동 멈춤.
        temperature = 0, # 창의성 없음, 예측가능한 결과.
    )
    end_time = time.time()

    # API로 부터 받은 응답.
    result = response.choices[0].message.content
    
    now= datetime.now().isoformat()
    use_token_dict = {
        "프롬프트 토큰 수": response.usage.prompt_tokens,
        "응답 토큰 수": response.usage.completion_tokens,
        "총 토큰 수": response.usage.total_tokens,
        "생성날짜": now,
        "소요시간": end_time - start_time
    }
    print(use_token_dict)

    return result


# 상표명을 입력받아 유사한 이름 생성
# brand_name = 'mindshare'
# similar_words = generate_similar_barnd_names(brand_name)

# # 결과출력
# print(similar_words)