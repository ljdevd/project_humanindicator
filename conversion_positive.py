import pandas as pd
from collections import Counter
import re
from datetime import datetime, timedelta
import pytz

def calculate_daily_sentiment_ratios_exclude_sunday(input_csv_path, output_csv_path):
    """
    입력된 CSV 파일을 읽어 일요일을 제외한 일별로 긍정 비율을 계산하고,
    confidence 값이 0.7 이하인 경우 중립으로 처리한 상태에서
    해당 일자의 제목에서 불용어를 제외한 가장 많이 언급된 단어와
    감정이 가장 강한 제목을 추출한 후,
    'date', 'positive_ratio', 'top_word', 'strongest_title', 'top_word_with_top_word'를 포함하는 새로운 CSV 파일로 저장합니다.

    :param input_csv_path: 입력 CSV 파일 경로
    :param output_csv_path: 출력 CSV 파일 경로
    """
    # 불용어 리스트 정의
    stopwords = set([
        '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도',
        '를', '으로', '자', '에', '와', '한', '하다', '에서', '에서부터',
        '까지', '에게', '하고', '으로서', '동안', '및', '으로', '하고는',
        "ㅋㅋ", "ㅎㅎ", "ㅇㅇ", "ㄴㄴ", "ㄱㄱ", "ㅅㅂ", "ㅂㅂ", "ㄴㄴㄴ",
    "ㅃㅃ", "ㅋㄱ", "ㅇㅅㅇ", "ㄷㄷ", "ㅅㄱ", "ㅠㅠ", "ㅜㅜ",
    "ㅋㅋㅋㅋ", "ㅎㅎㅎ", "아님", "나만", "잘못", "진짜", "ㅈㄴ",
    "왜", "뭐", "그래서", "아니", "갑자기", "그럼", "오지네",
    "ㅂㄷㅂㄷ", "ㄱㅅ", "ㄴㄴㄴㄴ", "ㅋㅋㅋ", "그게뭐", "고소",
    "ㅅㅂㅅㅂ", "ㄷㄷㄷ", "ㅍㅎㅎ", "킹받네", "전혀", "어떻게",
    "진짜로", "그러니까", "그런가", "요즘", "그런데", "근데",
    "ㅉㅉ", "ㅠㅠㅠ", "ㅎㅇ", "ㅋㅇㅋ", "이게뭐야", "미쳤다",
    "ㅋㅋㅋㅋㅋ", "뭐야", "뭐라고", "이게뭐지", "나중에", "다들",
    "ㅋㅋㅋㅋㅋㅋ", "다시", "ㄱㄱㄱ", "ㅇㅋ", "ㅇㅇㅇ", "야",
    "개쩔어", "ㅋㄱㄱ", "흠", "그럴수있지", "답답하다", "열받네",
    "끄덕", "아냐", "아님", "부럽다", "장난하냐", "개꿀", "헐",
    "ㄷㄷㄷㄷ", "한번", "헐ㅋ", "ㅏㅏㅏ", "이런", "ㅋㅑ", "느려",
    "재밌다", "열받아", "대박", "엄청", "죽는다", "대체", "엥",
    "ㅈㅣㄴ짜", "결국", "그럴리", "내 말이", "그래도", "가자",
    "그렇지", "이따", "좀", "아니야", "ㅇㅇㅇㅇㅇ", "흠흠",
    "진짜네", "별로", "아웃", "맞긴한데", "깜놀", "헐ㅋㅋㅋ",
    "미치겠다", "와우", "마무리", "맞네", "뭐가", "하기", "유일하게",
    "됐다", "뭐함", "도대체", "나갔다", "죽겠다", "나쁜놈", "확실히",
    "다시 봐도", "왠지", "쓰레기", "실화냐", "개빡침", "잡았다",
    "ㅇㅇㄱㄱ", "뭐야ㅋㅋ", "가만히", "미친놈", "그만하자",
    "미쳤다", "그게 다야", "이게 뭐지", "그렇다면", "진심",
    "말되나", "이거 실화냐", "나가자", "괜찮은데", "불안", "하지마",
    "맞는 말", "아니겠지", "이게 바로", "또 뭐야", "맞아",
    "신기하다", "뭐하는거지", "대박이다", "찐따", "동의해",
    "맞다", "계속하자", "조용히 해", "그래요", "그걸로 끝",
    "그냥 그렇다고", "왜", "근데", "아", "와", "지금", "다", "이거", "좀", "다시",
    "그냥", "더", "또", "내", "나", "내일", "아니", "그", "이",
    "뭐", "다들", "거", "안", "아직", "아직도", "ㄷㄷ", "ㄷ",
    "ㄷㄷㄷ", "ㄷㄷㄷㄷ", "ㅇㅇ", "어", "ㅅㅂ", "ㅅㅅ", "ㅅㅅㅅ",
    "그리", "저", "뭐야", "나도", "어케", "하나", "일단", "있다",
    "는", "하", "하고", "어어", "하따", "없는", "어지", "야",
    "가", "등", "오늘", "아", "와", "다", "걍", "또", "이제", "그냥", "더", "ㄹㅇ", "그",
    "이", "내", "거", "하", "안", "아직", "일단", "하나",
    "는", "하고", "어어", "ㅅㅅ", "어", "무슨", "그냥 그렇다고",
    "ㅅㅂ", "ㅂㅂ", "ㄴㄴ", "ㅃㅃ", "ㅋㄱ", "ㅇㅅㅇ", "ㄷㄷ",
    "ㅅㄱ", "ㅠㅠ", "ㅜㅜ", "ㅋㅋ", "ㅎㅎ", "ㅎㅎㅎ", "ㅈㄴ", "ㅉㅉ",
    "ㅠㅠㅠ", "ㅎㅇ", "ㅋㅇㅋ", "이새끼", "ㅈㅣㄴ짜", "ㄷㄷㄷ",
    "ㅍㅎㅎ", "ㅋㅋㅋㅋㅋㅋㅋ","ㅅㅅㅅㅅ","ㅅㅅㅅ","ㅅㅅ","아가리","기상","젤",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "20", "30", 
    "50", "100", "어제", "내가", "난", "너무", "오늘은", "오늘의","오늘도", "사람", 
    "있냐", "아까", "보고", "많이", "잘", "때", "없네", 
    "할", "관련", "얘", "있으면", "때문에", "자", "이미", "같음", "있나","시발",
    "씨발","존나","개같이","새끼","ㅆㅂ","씹","ㅋ","딱","함","솔직히","님들","글","드디어"
        # 필요 시 추가 가능
    ])

    # CSV 파일 읽기
    try:
        df = pd.read_csv(input_csv_path)
    except FileNotFoundError:
        print(f"입력 파일 '{input_csv_path}'을(를) 찾을 수 없습니다.")
        return
    except pd.errors.EmptyDataError:
        print(f"입력 파일 '{input_csv_path}'이(가) 비어 있습니다.")
        return
    except pd.errors.ParserError:
        print(f"입력 파일 '{input_csv_path}'을(를) 읽는 중 오류가 발생했습니다.")
        return

    # 'date_time' 컬럼을 datetime 형식으로 변환
    try:
        df['date_time'] = pd.to_datetime(df['date_time'])
    except Exception as e:
        print(f"'date_time' 컬럼을 datetime 형식으로 변환하는 중 오류가 발생했습니다: {e}")
        return

    # 한국 시간(KST)을 미국 동부 시간(EST)으로 변환
    kst = pytz.timezone('Asia/Seoul')
    est = pytz.timezone('US/Eastern')
    
    def convert_to_est(row):
        try:
            local_time = kst.localize(row)
            est_time = local_time.astimezone(est)
            return est_time
        except Exception as e:
            print(f"시간 변환 오류: {e}")
            return row

    df['est_time'] = df['date_time'].apply(convert_to_est)
    df['est_date'] = df['est_time'].dt.date  # 미국 기준 날짜 추출

    # `confidence`가 0.7 이하인 경우 중립 처리
    df.loc[df['confidence'] <= 0.75, 'sentiment'] = 0

    # 그룹화: 미국 기준 날짜별로 그룹화
    grouped = df.groupby('est_date')

    # 결과를 저장할 리스트 초기화
    results = []

    for date, group in grouped:
        # 일요일 제외
        if date.weekday() == 6:  # 0: 월요일, ..., 6: 일요일
            continue

        # 긍정 비율 계산 (기존 로직)
        total_weight = group['confidence'].sum()
        positive_weight = group[group['sentiment'] == 1]['confidence'].sum()
        positive_ratio = (positive_weight / total_weight) * 100 if total_weight > 0 else 0
        positive_ratio = round(positive_ratio, 2)

        # 제목에서 가장 많이 언급된 단어 추출 (기존 로직)
        titles = ' '.join(group['title'].astype(str))
        titles_clean = re.sub(r'[^가-힣\s]', '', titles)
        words = titles_clean.split()
        filtered_words = [word for word in words if word not in stopwords and len(word) > 1]
        word_counts = Counter(filtered_words)

        if word_counts:
            top_word, _ = word_counts.most_common(1)[0]
        else:
            top_word = ''

        # top_word를 포함하는 제목 중 감정이 가장 강한 제목 추출
        if top_word:
            titles_with_top_word = group[group['title'].str.contains(top_word, case=False, na=False)]
            if not titles_with_top_word.empty:
                strongest_title_row = titles_with_top_word.loc[titles_with_top_word['confidence'].idxmax()]
                strongest_title_with_top_word = strongest_title_row['title']
            else:
                strongest_title_with_top_word = ''
        else:
            strongest_title_with_top_word = ''

        results.append({
            'date': date.strftime('%Y-%m-%d'),
            'positive_ratio': positive_ratio,
            'top_word': top_word,
            'strongest_title_with_top_word': strongest_title_with_top_word
        })

    # 결과를 DataFrame으로 변환
    result_df = pd.DataFrame(results)

    # 날짜 기준으로 정렬
    result_df = result_df.sort_values(by='date')

    # 결과를 새로운 CSV 파일로 저장
    try:
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"결과가 '{output_csv_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"결과를 '{output_csv_path}' 파일로 저장하는 중 오류가 발생했습니다: {e}")


    # 결과를 DataFrame으로 변환
    result_df = pd.DataFrame(results)

    # 날짜 기준으로 정렬
    result_df = result_df.sort_values(by='date')

    # 결과를 새로운 CSV 파일로 저장
    try:
        result_df.to_csv(output_csv_path, index=False, encoding='utf-8-sig')
        print(f"결과가 '{output_csv_path}' 파일로 저장되었습니다.")
    except Exception as e:
        print(f"결과를 '{output_csv_path}' 파일로 저장하는 중 오류가 발생했습니다: {e}")

# 사용 예제
if __name__ == "__main__":
    input_csv = 'input_data.csv'                  # 입력 CSV 파일 경로
    output_csv = 'daily_sentiment_ratios.csv'     # 출력 CSV 파일 경로

    calculate_daily_sentiment_ratios_exclude_sunday(input_csv, output_csv)
