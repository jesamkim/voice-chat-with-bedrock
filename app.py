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
모르는 내용은 모른다고 답해주세요. """


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



def bedrock_claude3():
    session = boto3.Session()
    bedrock_runtime = session.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )
    bedrock_model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    payload = {
        "modelId": bedrock_model_id,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user", 
                    "content": [{"type": "text", "text": prompt}]
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
    
    print("Bedrock:") 
    
    # "content" 항목에서 "text" 필드의 값을 추출하여 출력
    for item in response_dict["content"]:
        if "text" in item:
          print(item["text"])


async def basic_transcribe():
    global prompt  # 전역 변수 사용 선언
    client = TranscribeStreamingClient(region="us-east-1")
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
print("음성 채팅을 시작합니다. 한국어로 말해주세요. 입력을 마치려면 Enter키를 누르세요. \n")

print("YOU : ")
loop = asyncio.get_event_loop()
loop.run_until_complete(basic_transcribe())
loop.close()

bedrock_claude3() # 프로그램 종료 시 챗봇 대답 출력
