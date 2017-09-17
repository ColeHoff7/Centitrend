import websocket
import threading
import time
import argparse
import json
import datetime
from datetime import date

gainMap = {}
gainArr = []

def on_message(ws, message):
    datum = json.loads(message)
    timeStamp = datum['DateStamp']
    # gainMap[timeStamp[:timeStamp.find('T')]] = (datum['Open'] - datum['Close']) / datum['Close'] * 100
    gainMap[timeStamp] = (datum['Open'] - datum['Close']) / datum['Close'] * 100

def on_error(ws, error):
    print(error)

def on_close(ws):
    for key in sorted(gainMap):
        gainArr.append(gainMap[key])
    

def on_open(ws):
    def run():
        ws.send("")
        time.sleep(1)
        ws.close()
    threading.Thread(target=run).start()

def main():
    parser = argparse.ArgumentParser(description='gettin some market data')
    parser.add_argument('--start_date', required=True, help="Enter a valid start date in YYYYMMDD format")
    parser.add_argument('--end_date', required=True, help="Enter a valid end date in YYYYMMDD format")
    parser.add_argument('--symbols', required=True, help="Enter a ticker symbol or list of tickers. E.g. NDAQ or NDAQ,AAPL,MSFT")

    args = parser.parse_args()

    websocket.enableTrace(True)

    symbols = args.symbols.split(',')

    for symbol in symbols:
        url = 'ws://35.161.245.102/stream?symbol={}&start={}&end={}'.format(symbol,args.start_date,args.end_date)
        ws = websocket.WebSocketApp(url,
                                    on_message = on_message,
                                    on_error = on_error,
                                    on_close = on_close)
        ws.on_open = on_open
        ws.run_forever()

    # print(gainMap)
    print(gainArr)

if __name__ == "__main__":
  main() 