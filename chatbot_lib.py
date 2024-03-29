import os
import boto3
from io import BytesIO
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.chat_models import BedrockChat
from langchain.chains import ConversationChain

# 시스템 프롬프트 설정
SYSTEM_PROMPT = "You're a cool assistant, love to response in Korean."

def get_llm():

    model_kwargs = { #Anthropic Cloude 3 Sonnet 파라미터
        "max_tokens": 1024, 
        "temperature": 0, 
        "top_p": 0.5, 
        "top_k": 0,
        "stop_sequences": ["\n\nHuman:"],
        "system": SYSTEM_PROMPT
    }

    llm = BedrockChat(
        credentials_profile_name=os.environ.get("BWB_PROFILE_NAME"), #AWS 자격 증명에 사용할 프로필 이름을 설정합니다(기본값이 아닌 경우)
        region_name=os.environ.get("BWB_REGION_NAME"), #리전 이름을 설정합니다(기본값이 아닌 경우)
        endpoint_url=os.environ.get("BWB_ENDPOINT_URL"), #endpoint URL을 설정합니다 (필요한 경우)
        model_id="anthropic.claude-3-haiku-20240307-v1:0", #파운데이션 모델 선택
        model_kwargs=model_kwargs) #모델 속성 설정

    return llm


def get_memory():

    llm = get_llm()

    chat_memory = ConversationBufferWindowMemory(human_prefix='Human', ai_prefix='Assistant')
    conversation = ConversationChain(llm=llm, verbose=False, memory=chat_memory)

    return chat_memory


def get_chat_response(input_text, memory):

    llm = get_llm()

    conversation_with_summary = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    chat_response = conversation_with_summary.predict(input=input_text)
    return chat_response


def synthesize_speech(text, output_file):
    polly_client = boto3.Session().client('polly')
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat='mp3',
        VoiceId='Seoyeon'
    )
    if isinstance(output_file, BytesIO):
        output_file.write(response['AudioStream'].read())
    else:
        with open(output_file, 'wb') as f:
            f.write(response['AudioStream'].read())