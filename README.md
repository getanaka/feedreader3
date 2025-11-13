# README

## 開発環境

- uv
- pytest

## 構成パッケージ

- Python3
- FastAPI
- SQLModel
    - SQLite
- APScheduler
    - フィードの定期取得ジョブを実行する
- sse-starlette

## 実装予定API

- GET /feeds
    - 保存済みのフィードを取得する
- POST /feed-urls
    - RSS/AtomのフィードのURLを登録する
- DELETE /feed-urls
    - 登録済みのRSS/AtomのフィードのURLを削除する
- GET /feed/stream
    - SSEとしてサーバからリアルタイムに更新されたフィードの情報を取得する

## コマンド

### 起動

```bash
uv run fastapi dev
```
