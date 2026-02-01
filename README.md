[![ci](https://github.com/getanaka/feedreader3/actions/workflows/ci.yml/badge.svg)](https://github.com/getanaka/feedreader3/actions/workflows/ci.yml)

# README

## 概要

Pythonで実装されたシンプルなRSS/Atomフィードリーダー。

現時点では、フィードの登録管理API、フィードの定期収集ジョブ、収集したフィードの取得APIを、複数コンテナで構成されたPythonアプリケーションとして実装済み。

個人的な自動情報収集サービスとしての実用性と、学習・ポートフォリオとを兼ねたプロジェクトとして段階的に実装を進めている。

## 主な技術構成

- [Python](https://www.python.org/)
    - 開発言語
- [uv](https://docs.astral.sh/uv/)
    - プロジェクトマネージャ
    - コンテナでの実行も含めてすべてuv上で実行する形を取っている
- [FastAPI](https://fastapi.tiangolo.com/)
    - Webフレームワーク
- [APScheduler](https://pypi.org/project/APScheduler/)
    - フィードの定期取得ジョブの実行管理に使用
- [feedparser](https://pypi.org/project/feedparser/)
    - RSS/Atomフィードの取得およびパースに使用
- [SQLModel](https://sqlmodel.tiangolo.com/)
    - SQLデータベースを操作するライブラリ
- [watchfiles](https://pypi.org/project/watchfiles/)
    - workerコンテナでコードの変更を検出し再実行するために導入
- [PostgreSQL](https://www.postgresql.org/)
    - SQLデータベース

### 開発用

- [Ruff](https://docs.astral.sh/ruff/)
    - リンターおよびフォーマッター
- [mypy](https://mypy-lang.org/)
    - 静的型チェッカー
- [pytest](https://docs.pytest.org/en/stable/)
    - テストフレームワーク
- [Coverage.py](https://coverage.readthedocs.io/)
    - コードカバレッジ計測ツール
- [pytest-cov](https://pypi.org/project/pytest-cov/)
    - テストとCoverage.pyを連携させるpytestのプラグイン
- [pre-commit](https://pre-commit.com/)
    - コミット前に各種チェックを実行するために使用

## アーキテクチャ

### コンテナ構成

アプリケーション用とテスト用の2つのDocker Compose構成がある。

アプリケーション・テスト共にローカルでの直接実行は想定しない。これは環境の設定をDockerの機能に一任しているため。

#### アプリケーション用

docker-compose.ymlを参照。

- web
    - フィード取得先URLのCRUDと、そこから取得したフィードを参照するAPIを提供する
- worker
    - 定期的にデータベースに登録されたフィード取得先URLからフィードを収集し、データベースへ格納するジョブを実行する
- db
    - PostgreSQLデータベースコンテナ

webとworkerは直接やり取りすることはなく、dbを介して動く。

#### テスト用

docker-compose.test.ymlを参照。
pytestによるテスト実行はこのテスト用コンテナ上で行う。

- test
    - テスト実行環境
- db
    - アプリケーション用dbとほぼ同一のPostgreSQLデータベースコンテナ

### 環境変数

ホストの環境変数または.envファイルに書かれた環境変数を参照する。

ホスト上での直接の実行は想定しておらず、Dockerによるコンテナへの環境変数の注入を利用してセットアップしている。

## 開発環境構築

1. 以下をインストール
    - git
    - docker
        - 参考
            - <https://docs.docker.com/engine/install>
    - uv
        - 0.9.8で動作確認済み
        - 参考
            - <https://docs.astral.sh/uv/getting-started/installation/>
    - make

1. リポジトリをローカルへクローン
1. プロジェクトディレクトリに入り`uv sync`を実行
    - 各種パッケージがインストールされる
1. `.env.example`を参考に`.env`ファイルをプロジェクトディレクトリ直下に作成
1. `docker compose up`でアプリケーション用コンテナを実行
    - `http://127.0.0.1:8000/docs`にアクセスできれば成功
1. `make qa`でリンター、フォーマッタ、静的型解析、テストがまとめて実行可能
    - このときテストの実行前に自動的にテスト用コンテナが立ち上がる
    - テストまで問題なく実行できれば成功

### 注意

- WSL上の複数のディストリビューション + Docker Desktopを使う場合、同じDockerデーモンを共有するためdb-dataが別ディストリビューションにすでにある場合、そちらを参照するので注意
    - 既存のWSLディストリビューションA上にすでに環境構築済みでdb-dataがある状態で、新しいWSLディストリビューションBに環境を構築すると、`docker compose up`したときにBにはdb-dataが作られず、Aのdb-dataにボリュームがバインドされる
    - 複数のディストリビューション上で同時に実行する場合docker-compose.ymlに書かれているdb-dataの名前を修正するなどの対応が必要

## テストおよびCI

`make qa`で`ruff check`（リンター）/`ruff format`（フォーマッター）/`mypy`（静的型チェッカー）/`pytest`（テスト）を一括で実行可能。

またCIとしてpush時に`make qa`を実行するGitHub Actionsも設定している。

## 開発方針

- Astral製品群を中心にモダンなPython開発環境に一通り触れることを目標としている
- OpenAI Codexを利用しているが学習のためコードの直接生成は行わない
    - レビューや相談などに留める
- 段階的に進めていく
    - Webアプリケーションの開発経験が浅いので完成形までの見通しが立てにくい
    - 手戻りや最終的に不要となる機能の実装が発生するかもしれないがそこは許容する
- 実行はローカル、テスト、CIすべてコンテナ上で行うものとする
    - 環境変数などDockerの機能に任せてコードを単純化できたため
- テストを積極的に実装する
    - テストカバレッジは80%以上を指標とする
        - なお現時点でのテストカバレッジは83%
            - `make coverage`で計測可能

## 現状と今後

### DONE

- uvを中心としたモダンなPythonプロジェクト構成と開発環境
- 複数コンテナによるWebアプリケーション構成
- CI
- 最低限のAPI実装
    - フィード取得先URLのCRUD
    - フィード取得API
- フィードの定期取得

### TODO

- フィードをリアルタイムで取得するためのSSE(Server-Sent Events) API実装
    - [sse-starlette](https://github.com/sysid/sse-starlette)を導入予定
    - クライアントには現時点ではDiscordのBotを想定している
- [ty](https://docs.astral.sh/ty/)を導入しmypyを置換
    - uv/RuffとそろえてAstral製品に統一する
- 自動翻訳
    - 英語のフィードを日本語へ翻訳したものを取得できるようにする
- レコメンデーション
    - 大量のフィードの中からユーザーの関心に基づいておすすめのフィードを提案させる
