# 초기 세팅
conda create -n assistant python=3.12

conda activate assistant


# 시작
cd py-code && cd hw

conda activate jupyter_test

# 웹 테스트 페이지 오픈
jupyter notebook

# 사용 pip module
pip install load_dotenv sqlalchemy mysql mysql-connector-python pytz
