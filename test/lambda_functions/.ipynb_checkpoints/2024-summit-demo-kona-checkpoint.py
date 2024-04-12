def lambda_handler(event, context):
   
    # tool_input 값을 event에서 가져오거나 기본값을 설정합니다.
    tool_input = event.get('tool_input', None)
    
    # kona 함수 호출
    description = kona(tool_input)
    
    return {
        'statusCode': 200,
        'body': description
    }

def kona(tool_input=None):
    description = "현대 코나(영어: Hyundai Kona)는 현대자동차의 소형 5도어 스포츠 유틸리티 자동차이다. i30의 전륜구동 플랫폼을 공용한다. 몇몇 국가마다 수출명이 다르며 포르투갈에서는 차명은 카우아이(Kauai), 중국에서의 차명은 엔시노(Encino , 昂希诺 )이다."
    
    return description