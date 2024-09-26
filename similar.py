import os
import openai
from init import api_key
from datetime import datetime
import time
from dotenv import load_dotenv
import json
load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_similar_barnd_names(brand_name):
    prompt = f"""
    '{brand_name}'이라는 상표명을 기반으로, 외관, 발음, 관념 측면에서 유사한 검색어를 생성해 주세요. 다음 조건들을 고려해서 검색어를 만들어 주세요.

1. **기본 단어와 번역본 추가**:
    - '{brand_name}'과 그 번역본을 첫 번째에 추가해 주세요.
    - 예: 'onboarders'와 '온보더스'.

2. **철자 오류와 발음 유사성 반영**:
    - 철자 오류(누락, 추가, 순서 변경)를 반영해 유사한 단어를 추가해 주세요. 발음이 비슷한 단어들도 포함해 주세요.
    - 예: 'onboarders' -> 'onboader', '온보딩'. 
    - 생성 불가한 검색어 : '유상우정신건강병원'-> '유상우정신과', '유상우정신병원' 등의 특정이름이나 명칭을 포함한 검색어는 생성 불가합니다.

3. **합성어 분리 및 불필요한 단어 제거**:
    - 현재 존재할것 같은 상표명으로 쓰일 단어들 위주로 생성하세요.
        - 예 : 'onboarders' -> 'board', 'boards' 
        - 예 :'on','온', 'in', '인', 'a', '어', 'an', '언' 등과 같은 전치사로 판단되는 것들은 검색어로 생성하지 않아야합니다.
    - 특정 명칭이나 이름은 분리한 뒤 한번만 검색어에 추가, 흔한 단어 위주로 만드세요.
        - 예: '유상우정신건강의학원' -> '유상우', '정신건강의학원', '정신건강의학과', '정신병원'

4. **한 글자 검색어 필터링**:
    - 의미 없는 한 글자는 제외해 주세요. 단, 약어의 일부이거나 의미가 있으면 허용.

5. **관념 유사성 반영**:
    - 개념이나 의미가 유사한 단어들을 포함해 주세요.

6. **음운론적 변형 생성**:
    - 영어단어로된 상표명이거나 영어발음으로된 상표명은 영어단어도 만들어주세요.
    - 다른 언어 간 발음 변환을 반영해 주세요. 발음 변환된 단어도 포함해 주세요.
        - 예: 'onboarders' -> '온보더스','onboarders', '온보드', 'onboard'.


7. **결과는 JSON 형식으로 출력**:
    - 생성된 검색어는 `words` 리스트에 중복 없이 포함해 주세요. 첫 번째 검색어는 반드시 검색한 단어와 번역본입니다.

예시:
{{
  "words": [
    // 유사 단어 리스트
  ]
}}

** Warning! **
- 등록하려는 {brand_name}의 유사한 상표명을 찾을때 쓰일 검색어 입니다. 상표명으로 있을법한 단어를 위주로 나열하세요
- 반드시!!! 중복 단어는 나열하지 마세요.
- 특정이름은 중복단어로 판단하여 제외합니다.

    """
    start_time = time.time()
    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {
                "role":"system", 
                "content":"""
                당신은 제시된 상표명을 기반으로, 외관, 발음, 관념 측면에서 유사한 상표명을 검색하기 전에 
                유사 상표명을 발췌하는 전문가 입니다. 
                또한 중복단어는 절대 답하지 않도록 합니다.
                4~20 개 의 단어들을 생성하세요
                """
                },
            {'role': 'user', 'content': prompt}
        ],
        n=1, # 한번에 하나의 응답 생성
        # stop=None, #명시적인 멈춤 신호가 없으면 자동 멈춤.
        temperature = 0, # 창의성 없음, 예측가능한 결과.
    )
    end_time = time.time()

    now= datetime.now().isoformat()
    use_token_dict = {
        "프롬프트 토큰 수": response.usage.prompt_tokens,
        "응답 토큰 수": response.usage.completion_tokens,
        "총 토큰 수": response.usage.total_tokens,
        "생성날짜": now,
        "소요시간": end_time - start_time
    }
    print(use_token_dict)
    
    # API로 부터 받은 응답.
    result_str = response.choices[0].message.content
    # 응답 문자열이 비어있지 않은지 확인
    if not result_str:
        raise ValueError("OpenAI API 응답이 비어 있습니다.")
    print(result_str)
    # JSON으로 변환 시도
    try:
        #json 문자열 정리
        result = result_str.strip('```json').strip('```') 
        result = json.loads(result)
        print(result)
        return result

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError 발생: {e}")
        print(f"OpenAI API 응답 내용: {result_str}")
        raise  # JSON 파싱 오류 발생 시 예외 다시 던짐



# # 상표명을 입력받아 유사한 이름 생성
# brand_name = '시민언론시선'
# try:
#     similar_words = generate_similar_barnd_names(brand_name)
#     print(similar_words)  # 결과 출력
# except ValueError as ve:
#     print(f"에러: {ve}")
# except Exception as e:
#     print(f"예기치 않은 에러 발생: {e}")