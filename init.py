import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
# Open ai API를 사용하기 위한 클라이언트 객체생성
client = OpenAI(api_key=api_key)

# 상표 식별력 판단 AI(GPT-4o)   : asst_mD9MAguey0mzXs0wKEJmG4lV
# 상표 식별력 판단 AI           : asst_GDlNLfM4j2LCpTYFgULSR1V6
ASSISTANT_ID = 'asst_mD9MAguey0mzXs0wKEJmG4lV'
