# EAPゲルを用いた制御コード

本リポジトリでは、2025年度　立命館大学 理工学部 ロボティクス学科 クラウドロボティクス研究室での「EAPゲルを用いた「Gel Brain」のインターフェイス構築」の卒業論文での用いた制御プログラム一式である．

## 概要
以下の2点の実験で用いた制御コード
  - 1つの刺激(Stimulation)電極と3つの計測(Sensing)電極の制御
  - EAPゲルをインターフェイスとしたPong Gameの制御・実行
    

## 使用言語・ライブラリ
* Python 3.x
* Pygame (ゲーム画面・シミュレーション用)
* Matplotlib / Pandas / Seaborn (データ解析・グラフ生成用)
* OpenCV (動画生成用)

## ファイル構成
1 Stimulation電極と3 Sensing電極を用いた実験で用いるコード
* `videotra.py`: 実験ログ（CSV）から `opencv-python` を用いてビデオ出力を生成するスクリプト
* `pong_game.py`: EAPゲルの入力を反映させ、`pygame` で動作するメインの制御・ゲームプログラム
* `data/`: 実験結果のCSVデータを格納するフォルダ

## ソフトウェア環境と実行方法

### 1. 必要なライブラリのインストール
本研究で開発した制御システムおよび解析プログラムを実行するには、以下のライブラリが必要です。ターミナル（またはコマンドプロンプト）で以下のコマンドを実行してインストールしてください。
pip install pygame pandas numpy matplotlib seaborn opencv-python adafruit-blinka adafruit-circuitpython-ina219 RPi.GPIO

2. 各ライブラリの用途
プログラムの実行目的に応じて、以下のライブラリが使用されます。

システム制御・計測（Raspberry Pi）
adafruit-circuitpython-ina219: INA219センサーによる電流・電圧計測

adafruit-blinka: Raspberry PiでのCircuitPython環境動作

RPi.GPIO: リレー回路および電極切り替えの制御

ゲームシミュレーション
pygame: Pongゲーム環境の構築・描画

データ解析・可視化
pandas / numpy: 実験データの処理・数値計算

matplotlib / seaborn: 解析結果のグラフ作成

動画生成
opencv-python: 実験ログからのビデオ出力

3. 注意事項（Raspberry Piを使用する場合）
I2C通信を利用するため、あらかじめOS側の設定でI2Cインターフェースを有効化しておく必要があります。

# I2Cの有効化確認
sudo raspi-config

# 接続確認（INA219のアドレス 0x40, 0x41, 0x44 などが表示されるか）
i2cdetect -y 1
