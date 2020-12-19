# 入退室管理システム v1.1

## 簡単な説明

* 起動させるのは `main.py` と `run.py `
* データベースは共有しているが，それぞれシステム的には独立したものになっている
* データベースはhistoryテーブル（いままでの入退室全記録）とroomテーブル（現在室者一覧）の2つで管理

### `main.py`

* カードリーダー読み取り（京大の学生証 / 交通系ICカード）
* slackに投稿（slackbotのtoken取得が必要）
* カードの情報によるデータベースの更新（データベースの作成を先に行わないと`run.py`の立ち上げの時にエラーが出ます）
* タッチ音
* 関連：`slack_post.py`,`reader.py`,`create_table.py`,`db.py`
### `run.py`

* 管理webアプリの立ち上げ
* powered by fastapi
* `localhost:8000/revise` からデータベースの修正ができる．できる修正は以下の通り：
    * historyのレコード削除
    * roomのレコード削除
    * historyの先頭にレコードの追加
    * roomにレコードの追加（option：同時にhistoryの先頭にレコードの追加）
* `localhost:8000/soundsetting` から入退室音の追加ができる．
* 関連：`controllers.py`,`db.py`,`models.py`

## そのほか

* 遊び心要素
    * 京大の学生証だけではなくsuicaの残高読み取りができるようになっている（ただしモバイルは非対応）