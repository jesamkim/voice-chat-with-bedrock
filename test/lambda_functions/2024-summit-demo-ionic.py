def lambda_handler(event, context):
   
    # tool_input 값을 event에서 가져오거나 기본값을 설정합니다.
    tool_input = event.get('tool_input', None)
    
    # ionic 함수 호출
    description = ionic(tool_input)
    
    return {
        'statusCode': 200,
        'body': description
    }

def ionic(tool_input=None):
    description = """
    현대자동차의 아이오닉은 전기차만을 위해 만들어진 전용 EV 브랜드입니다. 아이오닉은 경제성과 스타일, 지속 가능성과 편리함을 혁신적으로 결합하여, 의식있는 소비자들이 책임감을 갖고 더 나은 미래를 위한 결정을 할 수 있는 기회를 제공하고자 합니다.
    """
    return description