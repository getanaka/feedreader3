# README

## 技術スタック

- Python3
- FastAPI
- SQLModel
    - SQLite
- APScheduler
    - フィードの定期取得ジョブを実行する
- sse-starlette

## API

- GET /feeds
    - 保存済みのフィードを取得する
- POST /feed-urls
    - RSS/AtomのフィードのURLを登録する
- DELETE /feed-urls
    - 登録済みのRSS/AtomのフィードのURLを削除する
- GET /feed/stream
    - SSEとしてサーバからリアルタイムに更新されたフィードの情報を取得する
