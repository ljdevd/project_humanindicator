from flask import Flask, jsonify, render_template, request
import pandas as pd
import yfinance as yf

app = Flask(__name__)

# 주식 데이터 수집 및 분석
def fetch_stock_data(ticker):
    try:
        data = yf.download(ticker, period='2y', interval='1d')

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
        print(f"Error fetching data for {ticker}: {e}")
        return []

@app.route('/api/data', methods=['GET'])
def get_data():
    # 요청에서 티커 값 가져오기
    ticker = request.args.get('ticker', 'NQ=F')  # 기본값: NQ=F
    stock_data = fetch_stock_data(ticker)
    if not stock_data:
        return jsonify({"error": f"Failed to fetch data for ticker: {ticker}"}), 500
    return jsonify(stock_data)

@app.route('/api/sentiment-data')
def get_sentiment_data():
    try:
        sentiment_data = pd.read_csv('daily_sentiment_ratios.csv')
        return jsonify(sentiment_data.to_dict(orient='records'))
    except Exception as e:
        print(f"Error fetching sentiment data: {e}")
        return jsonify({"error": "Failed to fetch sentiment data"}), 500

@app.route('/')
def index():
    return render_template('index.html')

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # PORT 환경 변수가 없으면 8080 포트를 사용
    app.run(debug=True, host='0.0.0.0', port=port)
