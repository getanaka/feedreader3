# README

シンプルなRSS/Atomフィードリーダー。
Pythonバックエンドとして、フィード取得先URLの登録API、登録された取得先からのフィードの定期取得ジョブ、取得したフィードの取得APIを実装している。

## 開発環境

- uv
- ruff
- mypy
- pytest
- pytest-cov
- coverage
- pre-commit

## 構成パッケージ

- Python3
- FastAPI
- SQLModel
    - PostgreSQL
- APScheduler
    - フィードの定期取得ジョブを実行する
- feedparser
    - RSS/Atomフィードを取得しパースする
- python-dotenv
    - `.env`ファイルを読み込む
- sse-starlette

## 機能

### フィードの定期取得

- 毎時0分から10分ごとに、登録されたフィード取得先にアクセスしフィードを取得、その各エントリーをDBへ登録する

### 保存済みフィードエントリーの取得

- 1つのフィードエントリーは、フィード内の1記事に相当する
- GET /feed-entriesで取得可能
    - start/endクエリパラメータで任意の時間範囲のフィードエントリーが取得できる

## 実装予定API

### /feed-sources

- POST /feed-sources
    - フィード取得先を登録する
- GET /feed-sources
    - 登録済みのフィード取得先を取得する
- GET /feed-sources/{feed_source_id}
    - 登録済みの指定のフィード取得先を取得する
- PATCH /feed-sources/{feed_source_id}
    - 登録済みの指定のフィード取得先を更新する
- DELETE /feed-sources/{feed_source_id}
    - 登録済みの指定のフィード取得先を削除する

### /feed-entries

- GET /feed-entries
    - 保存済みのフィードエントリーを取得する
- GET /feed-entries/stream
    - SSEとしてサーバからリアルタイムに更新されたフィードエントリーを取得する

## コマンド

### 起動

#### ホスト上で実行

```bash
uv run fastapi dev feedreader3/main.py
```

#### コンテナ上で実行

```bash
docker run --rm --env-file .env --volume .:/app --volume /app/.venv --publish 8000:8000 -it --name feedreader3-dev $(docker build -q .)
```

### QA

- ruff check/ruff format/mypy/pytestを一括で実行する
- テスト用のDBはdbコンテナにテスト開始時に作成、テスト終了時に削除しているので、テスト実施前に`docker compose up`でdbコンテナを立ち上げておく必要があるので注意

```bash
make qa
```

## 環境変数

FeedReader3の挙動を調整するための環境変数はOSの環境変数 > `.env`ファイル > デフォルト値の優先順位で読み込まれる。つまりOSの環境変数と`.env`ファイルで同じキーの値が提供された場合、FeedReader3はOSの環境変数の値を使い`.env`ファイルの値を無視する。

利用可能な環境変数については`.env.example`ファイルを参照すること。
