import os
from flask import Flask, jsonify, render_template
import pandas as pd
import yfinance as yf

app = Flask(__name__)

# 주식 데이터 수집 및 분석
def fetch_stock_data(ticker):
    try:
        # Yahoo Finance에서 주식 데이터 다운로드
        data = yf.download(ticker, period='1y', interval='1d')

        # 데이터가 비어 있는 경우 처리
        if data.empty:
            return [{"Date": "No Data", "Open": 0, "High": 0, "Low": 0, "Close": 0, "Volume": 0}]

        # 인덱스를 열로 변환
        data = data.reset_index()

        # 열 이름을 단순화
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]

        # 날짜를 문자열로 변환
        data['Date'] = data['Date'].astype(str)

        # JSON 변환
        return data.to_dict(orient='records')
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return [{"Date": "Error", "Open": 0, "High": 0, "Low": 0, "Close": 0, "Volume": 0}]


@app.route('/api/data')
def get_data():
    # NQ=F는 나스닥 100 선물 데이터
    stock_data = fetch_stock_data('NQ=F')
    return jsonify(stock_data)


@app.route('/api/sentiment-data')
def get_sentiment_data():
    try:
        # 감정 분석 데이터 로드
        sentiment_data = pd.read_csv('daily_sentiment_ratios.csv')
        return jsonify(sentiment_data.to_dict(orient='records'))
    except FileNotFoundError:
        print("Sentiment data file not found.")
        return jsonify({"error": "Sentiment data file not found."}), 404
    except Exception as e:
        print(f"Error loading sentiment data: {e}")
        return jsonify({"error": "Error loading sentiment data."}), 500


@app.route('/')
def index():
    # 기본 HTML 페이지 렌더링
    return render_template('index.html')


if __name__ == '__main__':
    # Render 호스팅을 고려해 PORT 환경 변수 읽기, 기본값은 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
