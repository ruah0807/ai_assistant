import common
import a_similarity_code.mes as mes

async def similarity_code_finding_logic(user_input: str):
    
    #스레드 생성 및 메시지 제출
    thread, run = mes.create_thread_and_run(f"{user_input}")

    messages = await common.handle_run_response(run,thread, expect_json=False)

    return messages