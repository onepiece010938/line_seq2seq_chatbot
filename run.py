# coding=utf-8
import sys
import os
sys.path.append(os.path.dirname(os.getcwd()))
from flask import Flask,request,jsonify
import jieba
import inference


app = Flask(__name__) 

@app.route('/message', methods=['POST'])
def reply():
    req_msg = request.form['msg']
    # print("Input:   ",req_msg)
    req_msg=" ".join(jieba.cut(req_msg))
    # print("Input_cut:   ",req_msg)
    # print("Input_cut_type:   ",type(req_msg))

    try:
        res_msg = inference.predict(req_msg)
    except:
        res_msg = "我不知道你在說什麼"
    res_msg = res_msg.replace('_UNK', '^_^')
    res_msg=res_msg.strip()
    

    if res_msg == ' ':
      res_msg = '請輸入一段話'
    res_msg = res_msg.replace('start', '').replace('end', '')
    # print("Output:   ",res_msg)
    return jsonify( { 'text': res_msg } )

if (__name__ == "__main__"): 
    app.run(host = '0.0.0.0', port = 5056) 
