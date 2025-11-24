# README

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
    - SQLite
- APScheduler
    - フィードの定期取得ジョブを実行する
- sse-starlette

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

### /feeds

- GET /feeds
    - 保存済みのフィードを取得する
- GET /feeds/stream
    - SSEとしてサーバからリアルタイムに更新されたフィードの情報を取得する

## コマンド

### 起動

```bash
uv run fastapi dev feedreader3/main.py
```

### QA

- ruff check/ruff format/mypy/pytestを一括で実行する

```bash
make qa
```
