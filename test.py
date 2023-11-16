import json
import urllib

import requests

tennisCourtList = {
            "중앙공원1": "OP48220697364086712,0",
            "중앙공원2": "OP48220697364086712,1",
            "중앙공원3": "OP48220697364086712,2",
            "중앙공원4": "OP48220697364086712,3",
            "중앙공원5": "OP48220697364086712,4",
            "중앙공원6": "OP48220697364086712,5",
            "중앙공원7": "OP48220697364086712,6",
            "중앙공원8": "OP48220697364086712,7",
            "중앙공원9": "OP48220697364086712,8",
            "중앙공원10": "OP48220697364086712,9",
            "수질복원센터A 테니스장1": "OP17028520651712824,0",
            "수질복원센터A 테니스장2": "OP21695037103696738,0",
            "수질복원센터A 테니스장3": "OP21166946437826537,0",
            "수질복원센터A 테니스장4": "OP21695037103696738,1",
            "수질복원센터A 테니스장5": "OP21703893297820968,0",
            "수질복원센터A 테니스장6": "OP21695037103696738,2",
            "수질복원센터A 테니스장7": "OP17028232109098739,0",
            "수질복원센터A 테니스장8": "OP21695037103696738,3",
            "수질복원센터A 테니스장9": "OP17028232109098739,1",
            "금남 생활체육공원1": "OP17271926690114529,0",
            "금남 생활체육공원2": "OP17271926690114529,1",
            "금남 생활체육공원3": "OP17271926690114529,2",
            "다정동 저류지 체육시설1 ": "OP17273881146249546,0",
            "다정동 저류지 체육시설2 ": "OP17273881146249546,1",
            "다정동 저류지 체육시설3 ": "OP17273881146249546,2",
            "소정 테니스장 A": "OP46996723757808552,0",
            "소정 테니스장 B": "OP46996723757808552,1",
            "소정 테니스장 C": "OP46996723757808552,2",
            "수질복원센터B 1": "OP17028743154983862,0",
            "수질복원센터B 2": "OP21696357966701005,0",
            "수질복원센터B 3": "OP17028743154983862,1",
            "전의생활체육공원1": "OP15716320733942054,0",
            "전의생활체육공원2": "OP15716320733942054,1",
            "전의생활체육공원3": "OP15716320733942054,2",
            "전의공공하수처리시설1": "OP10900259200163999,0",
            "조치원 체육공원1": "OP16682360410452683,0",
            "조치원 체육공원2": "OP16682360410452683,1",
            "조치원 체육공원3": "OP16682360410452683,2",
            "조치원 체육공원4": "OP16682360410452683,3",
            "조치원 체육공원5": "OP16682360410452683,4"
        }

def fcltList(oprtnPlanNo,sYear,sMonth,sDay):
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Host": "onestop.sejong.go.kr",
        "Origin": "https://onestop.sejong.go.kr",
        "Referer": "https://onestop.sejong.go.kr/Usr/resve/instDetail.do"
    }
    params = {
        "oprtnPlanNo": oprtnPlanNo,
        "sYear": sYear,
        "sMonth": sMonth,
        "sDay": sDay,
        "fcltNo": ""
    }

    params = urllib.parse.urlencode(params)

    url = "https://onestop.sejong.go.kr/Usr/resve/rest/timeCheck.do"
    res = requests.post(url=url, params=params)
    data = json.loads(res.text)

    # 응답 내용 확인
    # print("reserve 응답 상태 코드:", res.status_code)
    # print(f"응답 텍스트({name}):", res.text)

    reserveList = data

    # print("reserveList : ",reserveList)

    #############################################################
    # 예약자 명단 종료
    #############################################################

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Host": "onestop.sejong.go.kr",
        "Origin": "https://onestop.sejong.go.kr",
        "Referer": "https://onestop.sejong.go.kr/Usr/resve/instDetail.do"
    }
    params = {
        "oprtnPlanNo": oprtnPlanNo,
        "sYear": sYear,
        "sMonth": sMonth,
        "sDay": sDay,
        "fcltNo" : ""
    }

    params = urllib.parse.urlencode(params)

    url = "https://onestop.sejong.go.kr/Usr/resve/rest/fcltList.do"
    res = requests.post(url=url, params=params)
    # print(f"params : {params}")
    # print(f'url : {url}')
    # print(res)
    # 요청 보내기

    # 응답 내용 확인
    # print("fclt 응답 상태 코드:", res.status_code)
    # print(f"응답 텍스트({name}):", res.text)
    # JSON 데이터 파싱
    data = json.loads(res.text)
    # 새로운 딕셔너리 생성
    fcltList = data['fcltList']
    timeList = data['timeList']

    tennisCountCheckList = {}
    for data in fcltList:
        for time in timeList:
            fcltNo = data['fcltNo']
            fcltNm = data['fcltNm']
            oprtnPlanUseTimeNo = time['oprtnPlanUseTimeNo']
            tennisCountCheckList[f"{fcltNo}-{oprtnPlanUseTimeNo}"] = {
                'fcltNm' : fcltNm,
                'fcltNo': fcltNo,
                'oprtnPlanUseTimeNo' : time['oprtnPlanUseTimeNo'],
                "oprtnPlanNo" : time['oprtnPlanNo'],
                'strUseBeginHm' : time['strUseBeginHm'],
                'strUseEndHm' : time['strUseEndHm'],
                'useBeginHm' : time['useBeginHm'],
                'useEndHm': time['useEndHm']
            }
    print('tennisCountCheckList1 : ',len(tennisCountCheckList))


    # print(f"기예약 갯수 : {len(reserveList['checkList'])}")

    # tennisCountCheckList reserveYn : Y 으로 초기화
    for key in tennisCountCheckList:
        tennisCountCheckList[key]['reserveYn'] = 'Y'

    for reservation in reserveList['checkList']:
        # fcltNo와 oprtnPlanUseTimeNo를 결합하여 키 생성
        key = f"{reservation['fcltNo']}-{reservation['oprtnPlanUseTimeNo']}"
        print(key)

        # tennisCountCheckList1 해당 키가 존재하는지 확인
        if key in tennisCountCheckList:
            # 존재하면 reserveYn: 'N' 추가
            tennisCountCheckList[key]['reserveYn'] = 'N'

fcltList('OP21695037103696738','2023','11','20')