import os
import openai
from init import api_key
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

openai.api_key(os.getenv('OPENAI_API_KEY'))

def generate_similar_barnd_names(brand_name):
    prompt = f'''
    유사한 상표검색을 위해 검색어를 1가지 이상 만들어야합니다.
    다음 상표 이름과 유사한 검색어를 아래 json형식에 맞추어 리스트로 생성해주세요. 
    한글과 영어 또는 다른 나라 발음을 고려하여 만들되, 새로은 언어를 만들지는 마세요. 

    예시 : 
    - '홈즈 하우스' -> '홈즈', '하우스', 'homes house', 'homes' 등 
    - 'MindShare' -> 'mind', 'share', '마인드', '마인드쉐어' 등
    - '토미카' -> 'tomica' 등

    주의 : 응답에는 반드시 처음 요청한 상표이름도 함께 포함되어야합니다.
    
    응답 형식 :
    {{
        'search_words': [
        
        ]
    }}
    '''
    
    response = openai.chat.completions.create(
        model='gpt-4o-mini',
        prompt=prompt,
        n=1, # 한번에 하나의 응답 생성
        stop=None, #명시적인 멈춤 신호가 없으면 자동 멈춤.
        temperature = 0 # 창의성 없음, 예측가능한 결과.
    )

    # API로 부터 받은 응답.
    result = response.choices[0].text.strip()
    
    now= datetime.now().isoformat(0)
    
    return result
