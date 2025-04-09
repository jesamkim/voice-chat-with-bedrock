import os
import json
import base64
import boto3
import botocore
import asyncio
import sounddevice

from amazon_transcribe.client import TranscribeStreamingClient
from amazon_transcribe.handlers import TranscriptResultStreamHandler
from amazon_transcribe.model import TranscriptEvent
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage


#사용자 음성 입력(한국어)
prompt = """Human:  
다음 <context>에 대해 다음 지시 사항을 따라 주세요.

1. 입력된 prompt를 반복해서 말하지 마세요.
2. 맞춤법이나 띄어쓰기가 잘못되어 있으면 수정하세요.
3. 질의에 대한 답변만 출력 해주세요.
4. 이해할 수 없는 질의라면 '말씀을 이해하기 어렵습니다.'라고만 대답해주세요.

 입력된 prompt에 대해서 답변만 하세요.

<context>
"""


class MyEventHandler(TranscriptResultStreamHandler):
    async def handle_transcript_event(self, transcript_event: TranscriptEvent):
        global prompt  # 전역 변수 사용 선언
        results = transcript_event.transcript.results
        for result in results:
            if not result.is_partial:  # 최종 결과만 처리
                for alt in result.alternatives:
                    print(alt.transcript)  # 화면에 텍스트 출력
                    prompt += alt.transcript + "\n"  # 변환된 텍스트를 prompt 변수에 추가


async def wait_for_enter():
    await asyncio.get_event_loop().run_in_executor(None, input)

async def mic_stream(stop_event):
    loop = asyncio.get_event_loop()
    input_queue = asyncio.Queue()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(input_queue.put_nowait, (bytes(indata), status))

    stream = sounddevice.RawInputStream(
        channels=1,
        samplerate=16000,
        callback=callback,
        blocksize=1024 * 2,
        dtype="int16",
    )
    with stream:
        while not stop_event.is_set():
            indata, status = await input_queue.get()
            yield indata, status

async def write_chunks(stream, stop_event):
    async for chunk, status in mic_stream(stop_event):
        await stream.input_stream.send_audio_event(audio_chunk=chunk)
    await stream.input_stream.end_stream()



def bedrock_inference():
    session = boto3.Session()
    bedrock_runtime = session.client(
        service_name="bedrock-runtime",
        region_name="us-west-2",
    )
    
    # prompt 후처리
    global prompt
    prompt = prompt + "</context> Assistant:"
    
    bedrock_model_id = "us.amazon.nova-micro-v1:0"
    payload = {
        "modelId": bedrock_model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "inferenceConfig": {
                "max_new_tokens": 1000
            },
            "messages": [{
                "role": "user", 
                "content": [{"text": prompt}]
                },
            ]
        }
    }
    body_bytes = json.dumps(payload['body']).encode('utf-8') #payload 인코딩
    response = bedrock_runtime.invoke_model(
        body = body_bytes,
        contentType = payload['contentType'],
        accept = payload['accept'],
        modelId = payload['modelId']
    )
    response_body = response['body'].read().decode('utf-8')
    # 문자열을 딕셔너리로 변환
    response_dict = json.loads(response_body)
    
    # 디버깅을 위해 전체 응답 구조 확인
    print("Bedrock 응답 구조:", json.dumps(response_dict, indent=2, ensure_ascii=False))
    
    print("\n\nBedrock:") 
    
    bedrock_response = ""
    
    # Nova 모델의 응답 형식 처리
    if "output" in response_dict and "message" in response_dict["output"] and "content" in response_dict["output"]["message"]:
        # Nova 모델 응답 형식
        content_list = response_dict["output"]["message"]["content"]
        for item in content_list:
            if "text" in item:
                text = item["text"]
                print(text)
                bedrock_response += text + " "
    elif "content" in response_dict:
        # Claude 스타일 응답
        for item in response_dict["content"]:
            if "text" in item:
                text = item["text"]
                print(text)
                bedrock_response += text + " "
    elif "completion" in response_dict:
        # 일부 모델의 응답 형식
        text = response_dict["completion"]
        print(text)
        bedrock_response = text
    elif "outputText" in response_dict:
        # 다른 가능한 응답 형식
        text = response_dict["outputText"]
        print(text)
        bedrock_response = text
    elif "output" in response_dict and "text" in response_dict["output"]:
        # 또 다른 가능한 응답 형식
        text = response_dict["output"]["text"]
        print(text)
        bedrock_response = text
    elif "generated_text" in response_dict:
        # 일부 모델의 응답 형식
        text = response_dict["generated_text"]
        print(text)
        bedrock_response = text
    else:
        # 알 수 없는 응답 형식인 경우
        print("알 수 없는 응답 형식, 응답 구조를 확인하세요.")
        bedrock_response = "응답 형식을 해석할 수 없습니다."
    
    # Polly로 음성 합성
    polly_client = boto3.client('polly')
    response = polly_client.synthesize_speech(
        Engine='neural',  # Neural 엔진 사용
        Text=bedrock_response,
        OutputFormat='mp3',
        VoiceId='Seoyeon'  # 한국어 음성 'Seoyeon' 사용
    )
    
    # 음성 데이터를 파일로 저장
    with open('bedrock_response.mp3', 'wb') as f:
        f.write(response['AudioStream'].read())

    # 음성 파일 재생 (macOS에서는 'afplay' 명령어 사용)
    os.system('afplay bedrock_response.mp3')
    
    # 음성 파일 삭제
    os.remove('bedrock_response.mp3')


async def basic_transcribe():
    global prompt  # 전역 변수 사용 선언
    client = TranscribeStreamingClient(region="ap-northeast-2")
    stream = await client.start_stream_transcription(
        language_code="ko-KR",
        media_sample_rate_hz=16000,
        media_encoding="pcm",
    )
    handler = MyEventHandler(stream.output_stream)

    stop_event = asyncio.Event()
    enter_task = asyncio.create_task(wait_for_enter())
    enter_task.add_done_callback(lambda _: stop_event.set())

    await asyncio.gather(
        write_chunks(stream, stop_event),
        handler.handle_events(),
    )
    print("<챗봇 응답까지 조금만 기다려주세요...> \n")
    
    
###########
print("\n 음성 채팅을 시작합니다. 한국어로 말해주세요. 입력을 마치려면 Enter키를 누르세요. \n")

print("YOU : ")
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()

bedrock_inference() # 프로그램 종료 시 챗봇 대답 출력
