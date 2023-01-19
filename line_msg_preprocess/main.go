package main

import (
	"bufio"
	"fmt"
	"io"
	"os"
	"regexp"
	"strings"

	"github.com/spf13/viper"
)

// config
var (
	UserName       string
	FriendName     string
	UserNameFlag   string
	FriendNameFlag string
	NewFieldFlag   string
	FilePath       string
	TargetPath     string
)

func initConfig() {
	viper.SetConfigFile("preprocess.yaml")
	viper.SetConfigType("yaml")
	err := viper.ReadInConfig()
	if err != nil {
		panic("Read Config Fail:" + err.Error())
	}
	FilePath = viper.GetString("config.lineHistoryPath")
	TargetPath = strings.TrimSuffix(FilePath, ".txt")
	TargetPath = TargetPath + "_ok.txt"
	UserName = viper.GetString("config.userName")
	FriendName = viper.GetString("config.friendName")
	UserNameFlag = viper.GetString("setting.userNameFlag")
	FriendNameFlag = viper.GetString("setting.friendNameFlag")
	NewFieldFlag = viper.GetString("setting.newFieldFlag")
}

func main() {
	initConfig()
	//打開對話紀錄
	srcFile, _ := os.Open(FilePath)
	defer srcFile.Close()

	//準備寫入的檔案
	goodFile, _ := os.OpenFile(TargetPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	defer goodFile.Close()

	//創建對原始文件的緩衝讀取器
	reader := bufio.NewReader(srcFile)

	// 含有特殊字跳過 通話 照片 影片 貼圖 禮物在信箱裡  未接來電 通話時間 檔案
	// var r_exclude = regexp.MustCompile(`通話時間|通話|照片|影片|貼圖|禮物在信箱裡|未接來電|檔案`)
	// 改成有[xxx]都跳過
	var r_exclude = regexp.MustCompile(`\[.*\]`)

	// 時間戳跳過
	var r_date = regexp.MustCompile(`\d{4}/(\d{1}|\d{2})/(\d{2}|\d{1})（週.）`)
	var r_username = regexp.MustCompile(`\d{2}:\d{2}.` + UserName + ".")
	var r_friendname = regexp.MustCompile(`\d{2}:\d{2}.` + FriendName + ".")
	// url跳過
	var r_url = regexp.MustCompile(`/((http|ftp|https)\:\/\/)?([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?/g`)
	var count = 0
	var previous_row_name = ""
	var flag_getFriend = false
	var flag_E = 0
	//循環讀取
	for {

		//一次讀一行
		lineBytes, _, err := reader.ReadLine()

		//讀到底之後退出
		if err == io.EOF {
			break
		}
		// 跳過前3行
		if count < 3 {
			count++
			continue
		}

		msg := string(lineBytes)
		// fmt.Println(msg)
		if r_url.MatchString(msg) {
			fmt.Println(msg)
		}
		// 空白行跳過or特殊字跳過or時間戳跳過or url跳過
		if msg == "" || r_exclude.MatchString(msg) || r_date.MatchString(msg) || r_url.MatchString(msg) {
			continue
		}

		// 從抓到的第一個friendname開始處理對話（才能做成QA形式）
		if !flag_getFriend {
			if r_friendname.MatchString(msg) {
				flag_getFriend = true
			} else {
				continue
			}

		}

		// 判斷當前行是username
		if r_username.MatchString(msg) {
			// 續寫
			if previous_row_name == UserName {
				// 清空時間名稱後寫入
				// fmt.Println(r_username.ReplaceAllString(msg, ","))
				goodFile.WriteString(r_username.ReplaceAllString(msg, ","))

				continue
			}
			// 第一行
			if previous_row_name == "" {

				if flag_E%2 == 0 {
					goodFile.WriteString(NewFieldFlag + "\n")
				}
				goodFile.WriteString(r_username.ReplaceAllString(msg, UserNameFlag+" "))

				// 跳到下一行前 設定userName為前一行的使用者
				previous_row_name = UserName
				flag_E++
				continue
			}
			// 有換人 要加M
			if previous_row_name == FriendName {
				if flag_E%2 == 0 {
					goodFile.WriteString("\n" + NewFieldFlag)
				}
				goodFile.WriteString("\n" + r_username.ReplaceAllString(msg, UserNameFlag+" "))

				// 跳到下一行前 設定userName為前一行的使用者
				previous_row_name = UserName
				flag_E++
				continue
			}

		}
		// 判斷當前行是friendname
		if r_friendname.MatchString(msg) {
			// 續寫
			if previous_row_name == FriendName {
				// 清空時間名稱後寫入
				// fmt.Println(r_friendname.ReplaceAllString(msg, ","))
				goodFile.WriteString(r_friendname.ReplaceAllString(msg, ","))
				continue
			}
			// 第一行
			if previous_row_name == "" {
				if flag_E%2 == 0 {
					goodFile.WriteString(NewFieldFlag + "\n")
				}
				goodFile.WriteString(r_friendname.ReplaceAllString(msg, FriendNameFlag+" "))

				// 跳到下一行前 設定friendName為前一行的使用者
				previous_row_name = FriendName
				flag_E++
				continue
			}
			// 有換人 要換行
			if previous_row_name == UserName {
				if flag_E%2 == 0 {
					goodFile.WriteString("\n" + NewFieldFlag)
				}
				goodFile.WriteString("\n" + r_friendname.ReplaceAllString(msg, FriendNameFlag+" "))

				// 跳到下一行前 設定friendName為前一行的使用者
				previous_row_name = FriendName
				flag_E++
				continue
			}

		}
		// 該行抓不到使用者，代表是上一個使用者的訊息
		goodFile.WriteString("," + msg)
		// fmt.Println(previous_row_name)

	}
	goodFile.WriteString("\n")
}
