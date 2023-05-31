# encoding=utf-8
import json
import ddddocr
import requests
from base64 import b64decode
from flask import Flask, request, render_template

ocr = ddddocr.DdddOcr()

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def web():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        data = {}
        cookies = {}
        try:
            if 'imgdata' in request.json:
                imgdata = request.json['imgdata']
                if imgdata.startswith('data'):
                    imgdata = imgdata.split(',', 1)[1]
                imgdata = b64decode(imgdata)
            if 'header' in request.json:
                header = request.json['header']
            else:
                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'
                }
            if 'url' in request.json:
                url = request.json['url']
                r = requests.get(url, headers=header, timeout=30)
                for key, value in r.cookies.items():
                    cookies.update({key: value})
                imgdata = r.content
            if 'comp' in request.json:
                comp = request.json['comp']
                if comp not in ['digit', 'alpha', 'alnum']:
                    comp = 'alnum'
            else:
                comp = 'alnum'
            retry = 1
            while retry < 5:
                result = ocr.classification(imgdata)
                if comp == 'digit':
                    if result.isdigit():
                        break
                elif comp == 'alpha':
                    if result.isalpha():
                        break
                elif comp == 'alnum':
                    if result.isalnum():
                        break
                else:
                    break
                retry += 1
            data.update({'code': 1})
            data.update({'result': result})
            data.update({'cookies': cookies})
            data.update({'msg': 'success'})
        except:
            data.update({'code': 0})
            data.update({'msg': 'failure'})
        data_str = json.dumps(data)
        return data_str

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=9898)