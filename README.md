Line seq2seq chatbot
===

## Installation

```
pip install -r requirements.txt
```

Usage
---
### Step1 匯出聊天紀錄
Line應用程式中可以透過以下步驟匯出聊天紀錄：

1. 開啟Line應用程式，進入對話後，點擊選單按鈕 (三個橫線)。
2. 點擊「其他設定」。
3. 點擊「傳送聊天紀錄」。
4. 檔案會儲存在您的電腦或手機中，您可以在電腦中開啟或將檔案傳送到其他設備。

### Step2 前處理
1. `cd line_msg_preprocess`
2. 設定preprocess.yaml
*   範例 line.txt:
    ```
    [LINE] 與A的聊天記錄
    儲存日期：2023/1/17 17:28

    2022/9/2（週五）
    17:21	A	xxxxxxx
    17:21	MYNAME	xxxxxxx
    ```
    
*    preprocess.yaml:

        ```
         config:
              userName: "MYNAME" # Your name
              friendName: "A" # The name of your chat partner
              lineHistoryPath: "./line.txt" # Your .txt file 
            setting:
              userNameFlag: "M"
              friendNameFlag: "M"
              newFieldFlag: "E"
        ```

3. 執行binary file
    ```
    ./main
    ```
    > 如果有go環境可以先在主目錄下`go mod tidy`再回來執行`go run main`
4. 會產生xxx_ok.txt:
    ```
    E
    M QQQQQ
    M AAAAAAA
    E
    M QQQQQQQQQQQ
    M AAA
    ```

### Step3 訓練模型
1. `cd config`
2. 設定seq2seq.ini
    ```
    [strings]
    # Output of line_msg_preprocess
    resource_data = train_data/line_ok.txt

    # seq data for train
    seq_data = train_data/line_seq.data
    train_data=train_data

    e = E
    m = M

    weight_dir = weight
    [ints]
    # vocabulary size 
    # 	20,000 is a reasonable size
    enc_vocab_size = 20000
    dec_vocab_size = 20000
    embedding_dim=128
    # output sentence max length
    max_length=20
    # typical options : 128, 256, 512, 1024
    layer_size = 256
    batch_size = 1
    [floats]
    min_loss=0.7

    ```
    resource_data換成Step2產生的檔案路徑就好，其他參數依照訓練結果可以調整
3. Training
    ```
    python3 train.py
    ```
    > 模型部份詳細參考: https://github.com/zhaoyingjun/chatbot/tree/master/Chatbot_pytorch/Seq2seqchatbot

    train_data下會生成訓練真正要用的seq.data檔
    權重檔在weight/weight.pt
    
### Step4 啟動flask server
    
    python3 run.py
