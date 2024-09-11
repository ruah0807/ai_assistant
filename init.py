import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get('OPENAI_API_KEY')
# Open ai API를 사용하기 위한 클라이언트 객체생성
client = OpenAI(api_key=api_key)

ass_id = os.environ.get('ASSISTANT_ID')