import os
import openai
from datetime import datetime
import time
from dotenv import load_dotenv
import json
load_dotenv()

openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_similar_barnd_names(brand_name, asign_product_description):
    prompt = f"""
상표명 '{brand_name}'과(와) 관련된 외관, 발음, 관념적 유사성을 기반으로 검색어를 생성하세요. 다음 조건과 지정상품 '{asign_product_description}'를 고려하세요:

0. **언어 조건**:
    - '{brand_name}'이 한글일 경우, 음 그대로 영어로 변환 / 뜻 그대로 영어로 변환하여 검색어를 생성하세요.
    - '{brand_name}'이 영어일 경우,  발음 그대로 한글로 변환 / 뜻 그대로 한글로 변환하여 검색어를 생성하세요.


1. **지정상품과 관련된 주요부 판별 및 일반 명사 제거**:
    - 지정상품 '{asign_product_description}'과 밀접하게 연관된 일반 명사나 산업 관련 단어를 제외하고 상표명의 고유한 부분을 추출하여 검색어를 생성하세요.
    - 여러 단어들의 합인 경우, 주요부만 떼어내서 검색어를 생성
    - 예시 :
        1. CALIFIA FARMS: “FARMS”는 농업과 관련된 일반 명사이므로, 고유한 부분은 CALIFIA입니다.
	    2. HAPPITRAVEL: “TRAVEL”은 여행 산업과 관련된 일반 명사이므로, 고유한 부분은 HAPPI입니다.
	    4. ZAMST HYBRID KNIT TECHNOLOGY: “TECHNOLOGY,” “HYBRID,” “KNIT”는 모두 일반 명사이므로, 고유한 부분은 ZAMST입니다.
	    5. Apple: “Apple”은 과일과 관련된 일반 명사이지만, “핸드폰”과 같은 지정상품에 적용될 때는 고유한 부분이 됩니다.

2. **단어 줄이기**:
    - 마지막 음절을 제외한 축약형 검색어를 생성하세요.
    - 예: '나이키' → '나이'

3. **발음 변형 생성**:
    - 발음이 유사한 음절을 변경하거나 추가, 삭제하여 발음 변형을 생성하세요.
    - 예: 'adidas' → 'adida'

4. **지정상품과 관련된 일반적 단어 제거**:
    - 'on', 'in', 'Co', 'Corp', 'Ltd' 등과 같은 일반적 단어나 '{asign_product_description}'와 관련된 단어는 검색어에서 제외하세요.
    
5. **유사성 예시 활용**:
    - 아래와 같은 유사성 예시를 참고하여 발음, 외관, 관념적 유사성을 고려한 검색어를 생성하세요.
    - 호칭이 유사한 표장 예시 
        INTERCEPTOR ≒ 인터셉트 / REVILLON ≒ REVLON / LYSOTAN ≒ 로소탄(LOSOTAN) / 
        千年 ≒ 天然 / TVC ≒ TBC / 마르샤 ≒ 마르셀 / EVOL ≒ EPOL / TOBY ≒ TOPY /
        DANYL ≒ DAONIL / Leeman ≒ Riman / PAPASHELIN ≒ PAPAPHYLLIN /
        CHROMATRON ≒ CHROMATONE / SAFUNEN ≒ SAFUNENSO / ADEFLON ≒ ADOPRON
            
    - 호칭이 유사하지 아니한 표장 예시 
        Solar ≠ polar / TBC ≠ CBC / 삼정 ≠ 미쯔이, MITSUI, みつい / 송하 ≠ 마쓰시다

6. **JSON 형식으로 출력**:
    - 중복 없이 생성된 모든 검색어를 `words` 리스트에 포함하세요. 첫 번째 검색어는 항상 '{brand_name}'이어야 합니다.

7. ** 일반명사를 제외한 단어 분리 **
    - 예시 : '상상베리 미술 ' -> '상상', '베리', '상상베리' 등
    - 예시 : '시민언론시선' -> '시민', '언론', '시선', '시민언론', '언론시선'


출력 예시:
{{
  "description_word": "'추측되는 일반명사' or '일반명사 없음'",
  "words": [
    "{brand_name}",
    "번역된_단어",
    "영어_단어_1",
    "한글_단어_1",
    "영어_단어_2",
    "한글_단어_2",
    ...
  ]
}}

**중요 사항**:
- 유사 단어를 최대 20개까지 만들어주세요 
- 특정 인명이나 건물명은 포함하지 마세요.
- 한 글자 단어는 생성하지 마세요. 모든 단어는 최소 두 글자 이상이어야 합니다.
- 지정상품 '{asign_product_description}'과 관련된 일반 명사를 제외하는 것에 집중하세요.
"""
    start_time = time.time()
    response = openai.chat.completions.create(
        model='gpt-4o',
        messages=[
            {
                "role":"system", 
                "content":"""
                당신은 제시된 상표명을 기반으로, 외관, 발음, 관념 측면에서 유사한 상표명을 검색하기 전에 
                유사 상표명을 발췌하는 전문가 입니다. 
                또한 중복단어는 절대 답하지 않도록 합니다.
                
                """
                },
            {'role': 'user', 'content': prompt}
        ],
        n=1, # 한번에 하나의 응답 생성
        # stop=None, #명시적인 멈춤 신호가 없으면 자동 멈춤.
        temperature = 0.56, # 약간의 창의성 추가.
        top_p= 0.9 # 확률 합 90%를 만족하는 후보 중 선택
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
        return result

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError 발생: {e}")
        print(f"OpenAI API 응답 내용: {result_str}")
        raise  # JSON 파싱 오류 발생 시 예외 다시 던짐




####################################################################################################


# # 상표명을 입력받아 유사한 이름 생성
# brand_name = '시민언론시선'
# try:
#     similar_words = generate_similar_barnd_names(brand_name)
#     print(similar_words)  # 결과 출력
# except ValueError as ve:
#     print(f"에러: {ve}")
# except Exception as e:
#     print(f"예기치 않은 에러 발생: {e}")


####################################################################################################


"""
    '{brand_name}'과 관련된 외관, 발음, 관념적으로 유사한 검색어를 생성하세요. 아래 조건을 고려하세요:

0. **언어 조건**:
    - '{brand_name}'이 한글이면 영어 번역을 생성하지 마세요.
    - '{brand_name}'이 영어이거나 영어 발음 기반의 한국어일 경우, 모든 단어에 대해 영어와 한국어 번역을 생성하세요.
    - '{brand_name}'이 영어이거나 영어 발음 기반일 경우, 유사한 단어들도 영어와 한국어로 함께 생성하세요. 이 조건은 '{brand_name}'에서 파생되거나 유사한 모든 단어에 적용됩니다.

1. **기본 단어 및 번역본 추가**:
    - '{brand_name}'과 그 번역본을 첫 번째로 추가하세요.
    - 예: 'onboarders' -> 'onboarders', '온보더스'

2. **단어 분리**:
    - '{brand_name}'을 구성하는 단어를 분리하되, 두 글자 이상의 단어만 생성하세요.
    - 예: '유상우정신건강의학원' -> '유상우', '정신건강의학원'
    - 어떤 경우에도 한 글자 단어는 생성하지 마세요.

3. **전치사 및 불필요한 단어**:
    - 전치사 및 불필요한 단어(예: 'on', 'in', 'a', '언', '온', '인')를 식별하여 생성된 검색어에서 **제외**하세요.
    - 예: 'onboarding' -> 'boarding' (전치사 'on' 제외)

4. **철자 오류와 발음 유사성 반영**:
    - 철자 오류(누락, 추가, 순서 변경)를 반영하고, 발음이 유사한 단어를 포함하세요.
    - 예: 'onboarders' -> 'onboader', '온보딩'

5. **한 글자 단어 제외**:
    - 한 글자 단어는 생성하지 마세요. 모든 단어는 두 글자 이상이어야 합니다.

6. **관념 및 음운 변형 반영**:
    - 개념적으로 유사한 단어와 언어 간 발음 변형을 반영하세요.
    - 예: 'onboarders' -> '온보드', 'onboard'

7. **JSON 형식 출력**:
    - 중복 없이 생성된 모든 검색어를 `words` 리스트에 포함하세요. 첫 번째 검색어는 반드시 '{brand_name}'과 그 번역본이어야 합니다.

출력 예시:
{{
  "words": [
    "{brand_name}",
    "번역된_단어",
    "분리된_단어들",
    "유사_단어_목록"
  ]
}}

**중요 사항**:
- 특정 인명이나 건물명은 포함하지 마세요.
- 한 글자 단어는 생성하지 마세요. 모든 단어는 최소 두 글자 이상이어야 합니다.
- 전치사 및 불필요한 단어(예: 'on', 'in', 'a', '언', '온', '인')는 최종 검색어에서 제외하세요.



---






    Generate search terms related to the brand name '{brand_name}' based on visual, phonetic, and conceptual similarities. Please consider the following conditions:

0. **Language Conditions**:
    - If '{brand_name}' is in Korean, do not generate any English translations.
    - If '{brand_name}' is in English or based on English phonetics in Korean as a Korean writing, **generate translations for all terms in both English and Korean**.
    - When '{brand_name}' is in English or based on English phonetics, similar terms should also be generated in both English and Korean. This applies to all terms derived from or similar to '{brand_name}'.

1. **Add the original term and its translation**:
    - Add '{brand_name}' and its translation as the first entries.
    - Example 1 (English): 'mindshare' -> 'mindshare', '마인드쉐어'
    - Example 2 (Korean with English phonetics): '마인드쉐어' -> '마인드쉐어', 'mindshare''

2. **Split the components**:
    - Split the components of '{brand_name}' into separate terms, but only generate terms that are **at least two characters** long.
    - Example: '유상우정신건강의학원' -> '유상우', '정신건강의학원'
    - Avoid creating single-character terms under any circumstances.

3. **Prepositions and Unnecessary Words, if it's base on English phonetics or English**:
    - Identify prepositions and unnecessary words (e.g., 'on', 'in', 'a', '언', '온', '인') and **exclude them** from the generated search terms.
    - Example: 'onboarding' -> 'boarding' (exclude 'on')

4. **Include spelling variations and phonetic similarities**:
    - Include terms with spelling errors (missing, added, or rearranged letters) and phonetic similarities.
    - Example: 'onboarders' -> 'onboader', '온보딩'

5. **Exclude single-character terms**:
    - Do not generate single-character terms. All generated terms must be at least two characters or more.

6. **Reflect theotrical and phonetic transformations**:
    - Reflect theotrical similarities and phonetic transformations across languages.
    - Example: 'onboarders' -> '온보드', 'onboard'

7. **Output in JSON format**:
    - Include all generated search terms in a `words` list without duplicates. The first search term should always be '{brand_name}' and its translation.

"""