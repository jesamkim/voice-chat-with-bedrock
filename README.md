# Voice Chat test with Amazon Transcribe and Amazon Bedrock (Claude v3 Sonnet)

### 실행 방법

#### 1. 패키지 설치
- Local에 aws 자격 증명 설정은 되어 있어야 합니다. (aws configure)
```
python3 -m pip install -r ./requirements.txt
```

- macos의 경우 brew로 추가 패키지 설치가 필요할 수 있습니다.
```
brew install portaudio
```

#### 2. 앱 실행
- 사전에 us-east-1에 Bedrock 모델 access 설정은 되어 있어야 합니다.
```
python3 app.py
```

#### 앱이 실행되면, 로컬 환경(랩탑)의 mic 로 음성(한국어)을 인식합니다.
![result1](./img/result1.png)