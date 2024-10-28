import os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from init import client

# Assistant Name: 상표 TEXT 유사도 평가 Assistant
ASSISTANT_ID = 'asst_IbYT7EatQkmSnremkg5RuiC0'

async def submit_message(ASSISTANT_ID, thread, user_message):

    content = [{'type': 'text', 'text': user_message}]

    # 메시지 전송
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=content

    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=ASSISTANT_ID,
        instructions= """
            모든 텍스틀간의 검토가 끝난 후 
            반드시 문서를 참고하여 출처와 함께 종합의견을 내세요. 

            응답 형식 :     
            < 텍스트 유사도 의견서 >     
                - 검토의견: 
                    상표명 : (title)
                    상품류: (claasificationCode)
                    상표이미지: ![](drawing)
                    출원/등록일 : (applicationDate)
                    출원인/등록권자: (applicantName)
                    유사도 : (O - 유사, △ - 중간유사, X - 비유사 로 판단)
                    검토의견 : [어떤 부분이 비슷한지 아닌지 판단]
                
        """
    )
    print(f'assistant_id : {ASSISTANT_ID}')
    print(f'thread_id : {thread.id}')
    print(f'run_id : {run.id}')

    return run



# 새로운 스레드 생성 및 메시지 제출 함수
async def create_thread_and_run(user_input):
    # 사용자 입력을 받아 새로운 스래드를 생성하고, Assistant 에게 메시지를 제출
    thread= client.beta.threads.create()
    run = await submit_message(ASSISTANT_ID, thread, user_input)
    return thread, run



####################################################################################################

# def send_message_in_same_thread(thread, user_message):
#     # 메시지 전송
#     run = submit_message(ASSISTANT_ID, thread, user_message)
#     return run


# # 상표 이름
# brand_name = '시민언론시선' #<==입력을 받는다고 가정
# similarity_code = 'S0601' # 유사군 코드

# #비슷한 단어 찾기
# similar_words = generate_similar_barnd_names(brand_name)
# # 분류코드와 비슷한단어로 상표 검색
# result_data= updated_search_results_for_text(similar_words['words'], similarity_code)


# # 동시에 여러 요청을 처리하기 위해 스래드를 생성합니다.

# thread, run = create_thread_and_run(
#     f"""
#     제가 등록하고 싶은 상표명입니다.
#     \n상표명 : {brand_name}\n상품류/유사군:{similarity_code}
#     아래는 특허청에서 비슷한 상표를 검색한 데이터입니다. 업로드되어있는 문서를 기반으로 하여 10가지 상표명의 유사도를 명확하게 판단하고, 어떤 근거에 따라 유사성이 같은지 혹은 다른지를 소스를 주고 디테일하게 설명하세요.\n\n{result_data}""", 
#     )# json데이터를 보낼것.

# run = wait_on_run(run, thread)
# print_message(get_response(thread))



# 세 번째 스레드를 마친 후 감사 인사 전송
# thread, run = submit_message(thread, '고마워요')  # run3이 완료된 후 메시지 전송

# run = wait_on_run(run, thread)  # 완료될 때까지 대기
# print_message(get_response(thread))


