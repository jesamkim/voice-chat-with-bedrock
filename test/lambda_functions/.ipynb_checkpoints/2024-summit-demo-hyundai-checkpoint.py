def lambda_handler(event, context):
   
    # tool_input 값을 event에서 가져오거나 기본값을 설정합니다.
    tool_input = event.get('tool_input', None)
    
    # hyundai 함수 호출
    description = hyundai(tool_input)
    
    return {
        'statusCode': 200,
        'body': description
    }

def hyundai(tool_input=None):
    description = """
    현대자동차는 국내 최초로 독자 모델 포니를 개발하며 대한민국 자동차 산업의 선구자 역할을 해 왔습니다. 세계 200여 개국에 자동차를 수출하고 글로벌 생산기지를 건설해 세계적인 자동차 메이커로 자리매김했습니다. 세계 최초 양산형 수소차를 출시하고 프리미엄 브랜드 제네시스를 론칭해 시장을 확대하는 한편, 선도적 자율주행과 커넥티비티 기술을 바탕으로 미래 모빌리티 산업을 견인하고 있습니다. 현대자동차는 '인류애를 향한 진보'를 목표로 기술의 진화를 실현하며 인류를 위한 더 나은 방향을 모색하고 있습니다.
    - 창립 : 1967년
    - 사업분야 : 완성차 생산/판매
    - 생산제품 : 승용차, RV, 상용차, 친환경차
    """
    return description