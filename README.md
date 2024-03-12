# Voice Chatbot test with Transcribe, Polly and Bedrock (Claude v3 Sonnet)

#### 테스트 환경
- MacBook M1 Pro (macOS Sonoma)


### Architecture 
![test-architecture](./img/test-architecture.png)

### 실행 방법

#### 1. 패키지 설치
- 로컬 기기(MacBook)에 미리 AWS CLI를 [설치](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) 하고 [구성](https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-quickstart.html) 해야 합니다. (aws configure)
```
python3 -m pip install -r ./requirements.txt
```
 
- macOS의 경우 Homebrew를 통한 추가 패키지 설치가 필요할 수 있습니다.
```
brew install portaudio
```

#### 2. 앱 실행
- us-east-1 리전에서 Bedrock 모델 접근 권한을 미리 구성해야 합니다. (claude v3 sonnet)
```
python3 app.py
```

![result1](./img/result1.png)

#### 애플리케이션이 실행되면 로컬 기기(Macbook)의 Mic로 한국어로 말하세요.
> Amazon Transcribe가 한국어 음성 입력을 받습니다. <br>
> Amazon Bedrock에서 생성된 응답은 Amazon Polly를 통해 한국어 음성으로 재생됩니다. 


<br>


### 참고 자료
[aws-samples/amazon-bedrock-voice-conversation](https://github.com/aws-samples/amazon-bedrock-voice-conversation)