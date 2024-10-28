import common
import a_similarity_code.mes as mes


async def similarity_code_finding_logic(request_similarity_code):

    #스레드 생성 및 메시지 제출
    thread, run = mes.create_thread_and_run(f"{request_similarity_code}")

    messages = await common.handle_run_response_for_code(run,thread)

    print(messages)

    #'similarity' 항목에서 'similarity_code'값을 모두 합침
    if 'similarity' in messages :
        combined_similarity_code = '|'.join(
            item['similarity_code'].replace(', ', '|') for item in messages['similarity'] if 'similarity_code' in item
        )
        messages['combined_similarity_code'] = combined_similarity_code
    
    return messages