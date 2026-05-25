# resolve-srt-to-textplus

DaVinci Resolveの現在のタイムラインに、SRT字幕ファイルからText+クリップを生成するスクリプトです。

DaVinci Resolve無料版でも使いやすいように、外部ターミナルではなく、Resolve内の `Workspace > Scripts` メニューから実行する想定で作っています。

## 動作確認環境

- Windows
- DaVinci Resolve 20 無料版
- PythonスクリプトをResolve内のScriptsメニューから実行

## できること

- SRTファイルを読み込む
- SRTの開始時間・終了時間に合わせてText+を配置する
- 日本語字幕用に `Yu Gothic` などの日本語フォントを指定する
- タイムライン開始タイムコードが `01:00:00:00` の場合にも対応する

## インストール

`ImportSRT_TextPlus.py` を以下のフォルダにコピーしてください。

Windows:

```text
%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\

例:
C:\Users\ユーザー名\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\
Edit フォルダがない場合は作成してください。

## 使い方

1.DaVinci Resolveでプロジェクトを開く
2.空のタイムラインを作る
3.Workspace > Scripts > Edit > ImportSRT_TextPlus を実行する
4.SRTファイルを選ぶ
5.Text+字幕が生成される
6.そのあと背景動画・画像・音声を追加する
7.必要に応じてトラック順を入れ替える

## おすすめ運用

ResolveのスクリプトAPIでは、Text+を挿入するトラックを完全には制御できない場合があります。
そのため、以下の順番がおすすめです。

1. 空のタイムラインで先にSRTからText+字幕を作る
2. そのあと背景素材を追加する
3. 背景を下、字幕を上になるようにトラック順を調整する

## 注意点

- DaVinci Resolve 20無料版 / Windowsで動作確認しています。
- macOSや他バージョンでは未検証です。
- 日本語が四角で表示される場合は、Text+のフォントを Yu Gothic や Meiryo に変更してください。
- 既存素材があるタイムラインで実行すると、Text+が意図しないトラックに入る場合があります。

## ライセンス

MIT License
