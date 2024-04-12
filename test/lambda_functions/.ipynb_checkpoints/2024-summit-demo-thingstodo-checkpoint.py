def lambda_handler(event, context):
   
    # tool_input 값을 event에서 가져오거나 기본값을 설정합니다.
    tool_input = event.get('tool_input', None)
    
    # thingstodo 함수 호출
    description = thingstodo(tool_input)
    
    return {
        'statusCode': 200,
        'body': description
    }

def thingstodo(tool_input=None):
    description = "[현재 위치 기반 즐길거리 정보는 다음과 같습니다. ~~~~~]"
    return description