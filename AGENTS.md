# AGENTS

## エージェントサポートの方針

- 学習/ポートフォリオ向けのプロジェクトなので、基本的にはアドバイスに徹してください
- ファイル操作について
    - 読み取り
        - 許可します
        - こちらへの確認は不要です
        - 指示の実行でファイルへの読み込みが必要になったら許可を取らずに実行してください
    - 書き込み
        - こちらが明示的に指示しない限り許可しません
        - 作成および削除も含みます
- 出力は日本語で行ってください

## PostgreSQL

- PostgreSQL18からデータの保存先が`/var/lib/postgresql/18/docker`になった
- <https://hub.docker.com/_/postgres>

    > Important Change: the PGDATA environment variable of the image was changed to be version specific in PostgreSQL 18 and above. For 18 it is /var/lib/postgresql/18/docker. Later versions will replace 18 with their respective major version (e.g., /var/lib/postgresql/19/docker for PostgreSQL 19.x). The defined VOLUME was changed in 18 and above to /var/lib/postgresql. Mounts and volumes should be targeted at the updated location. This will allow users upgrading between PostgreSQL major releases to use the faster --link when running pg_upgrade and mounting /var/lib/postgresql.
