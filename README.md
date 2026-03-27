# 白粉ねこ Bot 🐱

白粉ねこのX (Twitter) 自動投稿Bot。Claude APIでキャラクターに忠実なツイートを生成し、1日10〜20件の自然なタイミングで投稿する。

## 機能

- **自動ツイート**: 1日10〜20件、彼女の生活リズムに合わせた時間帯で投稿
  - root@proxmox での作業報告
  - 研究の進捗 (esportsネットワーク遅延)
  - 日常生活・ゲーム・技術発見・猫・研究室ネタ
  - 深夜のゆるいツイート
- **いいね**: 関連キーワードのツイートを自動でいいね (1日5〜15件)
- **フォロー**: リプライしてくれた人を自動フォロバ (1日0〜3件)

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. API キーの設定

```bash
cp .env.example .env
```

`.env` を編集して以下のキーを設定:

- **X (Twitter) API**: [X Developer Portal](https://developer.twitter.com/) でアプリを作成し、API Key/Secret と Access Token/Secret を取得
- **Anthropic API**: [Anthropic Console](https://console.anthropic.com/) で API キーを取得

### 3. ツイート生成テスト (Xに投稿しない)

```bash
python test_generate.py
```

### 4. Bot起動

```bash
python main.py
```

## ファイル構成

```
白粉ねこ/
├── character_profile.md   # キャラクター設定書
├── config.py              # 設定 (投稿数・時間帯・キーワード)
├── main.py                # エントリーポイント
├── test_generate.py       # ツイート生成テスト
├── bot/
│   ├── generator.py       # Claude APIでツイート生成
│   ├── twitter_client.py  # X API v2 ラッパー
│   ├── scheduler.py       # スケジューラ (APScheduler)
│   ├── actions.py         # いいね・フォローロジック
│   ├── prompts.py         # プロンプトテンプレート
│   └── database.py        # SQLite データ管理
└── data/
    └── topics.json        # トピックシード
```

## 運用

- `main.py` は長時間動作するプロセス。`tmux`, `screen`, `systemd` 等で常駐させる
- ログは `bot.log` と stdout に出力
- `data/tweet_history.db` に投稿履歴・いいね・フォロー履歴を記録
