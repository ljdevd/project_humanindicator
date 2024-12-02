from flask import Flask, jsonify, render_template
import pandas as pd
import yfinance as yf

app = Flask(__name__)

# 주식 데이터 수집 및 분석
def fetch_stock_data(ticker):
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



@app.route('/api/data')
def get_data():
    stock_data = fetch_stock_data('NQ=F')  # 애플 주식 데이터
    return jsonify(stock_data)

@app.route('/api/sentiment-data')
def get_sentiment_data():
    sentiment_data = pd.read_csv('daily_sentiment_ratios.csv')
    return jsonify(sentiment_data.to_dict(orient='records'))
@app.route('/')
def index():
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
