import pandas as pd
from collections import Counter
import re

def calculate_daily_negative_ratios(input_csv_path, output_csv_path):
    """
    입력된 CSV 파일을 읽어 일별로 부정 비율을 계산하고,
    confidence 값이 0.7 이하인 경우 중립으로 처리한 상태에서
    해당 일자의 제목에서 불용어를 제외한 가장 많이 언급된 단어와
    감정이 가장 강한 제목을 추출하여 결과를 CSV로 저장합니다.

    :param input_csv_path: 입력 CSV 파일 경로
    :param output_csv_path: 출력 CSV 파일 경로
    """
    # 불용어 리스트 정의
    stopwords = set([
        '의', '가', '이', '은', '들', '는', '좀', '잘', '걍', '과', '도',
        '를', '으로', '자', '에', '와', '한', '하다', '에서', '에서부터',
        '까지', '에게', '하고', '으로서', '동안', '및', '으로', '하고는',
        "ㅋㅋ", "ㅎㅎ", "ㅇㅇ", "ㄴㄴ", "ㄱㄱ", "ㅅㅂ", "ㅂㅂ", "ㄴㄴㄴ",
        # 필요에 따라 추가 가능
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

    # 'date' 컬럼 추출 (날짜만)
    df['date'] = df['date_time'].dt.date

    # `confidence`가 0.7 이하인 경우 중립 처리
    df.loc[df['confidence'] <= 0.7, 'sentiment'] = 0

    # 그룹화: 날짜별로 그룹화
    grouped = df.groupby('date')

    # 결과를 저장할 리스트 초기화
    results = []

    for date, group in grouped:
        # 부정 비율 계산
        total_weight = group['confidence'].sum()
        negative_weight = group[group['sentiment'] == 0]['confidence'].sum()
        negative_ratio = (negative_weight / total_weight) * 100 if total_weight > 0 else 0
        negative_ratio = round(negative_ratio, 2)

        # 제목에서 가장 많이 언급된 단어 추출
        titles = ' '.join(group['title'].astype(str))
        titles_clean = re.sub(r'[^가-힣\s]', '', titles)
        words = titles_clean.split()

        # 불용어 제거 및 길이가 1 이상인 단어만 필터링
        filtered_words = [word for word in words if word not in stopwords and len(word) > 1]

        # 단어 빈도 계산
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
            'negative_ratio': negative_ratio,
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

# 사용 예제
if __name__ == "__main__":
    input_csv = 'input_data.csv'                  # 입력 CSV 파일 경로
    output_csv = 'daily_negative_ratios.csv'     # 출력 CSV 파일 경로

    calculate_daily_negative_ratios(input_csv, output_csv)
