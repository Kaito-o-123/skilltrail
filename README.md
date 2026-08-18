# SkillTrail（学習ロードマップ・スキル成長管理アプリ）

設計書（機能設計書・画面設計書・DB設計書・詳細設計書）をもとに実装した Django 版です。
学習目標を「トレイル」、ロードマップの各ステップを「ウェイポイント」に見立てたデザインになっています。

## 構成

```
skilltrail_django/
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── docker/entrypoint.sh
├── .vscode/                  # VSCode向けの推奨設定・デバッグ構成
├── skilltrail/          # プロジェクト設定 (settings.py, urls.py, ...)
└── roadmap/              # アプリ本体
    ├── models.py          # categories / learning_goals / roadmaps / learning_tasks / reflections
    ├── forms.py           # 入力チェック付きの各種フォーム
    ├── views.py           # 一覧・詳細・登録・編集・削除・完了などの処理
    ├── urls.py
    ├── admin.py
    ├── templatetags/roadmap_extras.py   # ステータスバッジ・分表示などのテンプレートフィルタ
    ├── management/commands/seed_data.py # デモ用サンプルデータ投入コマンド
    ├── templates/roadmap/                # 各画面のテンプレート
    └── static/roadmap/style.css          # デザイン（トレイルマップ風）
```

管理画面は `http://127.0.0.1:8000/admin/` です（`createsuperuser` 実行後）。

## セットアップ（方法A：VSCode + venv）

1. VSCodeでこのフォルダ（`skilltrail_django/`）を開く
2. ターミナルで仮想環境を作成・有効化

   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```

3. 依存パッケージをインストール

   ```bash
   pip install -r requirements.txt
   ```

4. VSCode右下（または `Ctrl+Shift+P` → `Python: Select Interpreter`）で
   `venv/bin/python`（Windowsは `venv\Scripts\python.exe`）を選択
   ※ `.vscode/settings.json` に既定パスを設定済みなので、多くの場合は自動で認識されます

5. マイグレーションとサンプルデータ投入

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py seed_data        # 任意：デモ用データを投入
   python manage.py createsuperuser  # 任意：管理画面用
   ```

6. 起動
   - ターミナルから: `python manage.py runserver`
   - もしくは VSCode の「実行とデバッグ」パネルから **Django: runserver** を選んで `F5`
     （ブレークポイントを置いてデバッグ可能）

   `http://127.0.0.1:8000/` を開くとダッシュボードが表示されます。

## セットアップ（方法B：Docker）

Docker Desktop（または Docker Engine + Compose）がインストールされていれば、
Pythonやパッケージをローカルに入れずにそのまま動かせます。

```bash
docker compose up --build
```

- 初回起動時に自動で `migrate` が実行され、`SEED_DATA=true`（`docker-compose.yml` で設定済み）
  によりサンプルデータも投入されます。
- `http://127.0.0.1:8000/` を開くとダッシュボードが表示されます。
- コードはバインドマウントされているため、`roadmap/` や `skilltrail/` を編集すると
  `runserver` の自動リロードで即座に反映されます。

管理者ユーザーを作りたい場合は、コンテナ起動中に別ターミナルから:

```bash
docker compose exec web python manage.py createsuperuser
```

停止する場合:

```bash
docker compose down
```

サンプルデータの投入をスキップしたい場合は `docker-compose.yml` の
`SEED_DATA=true` を `SEED_DATA=false` に変更してください。

### Dockerファイル構成

```
Dockerfile          # Python 3.12-slim ベースのイメージ定義
docker-compose.yml   # ローカル開発用（ホットリロード対応）
docker/entrypoint.sh # 起動時に migrate（+任意でseed_data）を自動実行
.dockerignore
```


## 実装している機能（01_機能設計書 準拠）

- 学習目標管理（登録・一覧・詳細・編集・削除、ステータス管理）
- ロードマップ管理（ステップの登録・編集・削除、並び順の変更）
- 学習タスク管理（登録・編集・削除・完了、教材URL・優先度・期限）
- 進捗管理（学習目標ごとの進捗率 = 完了タスク数 / 全タスク数 × 100 を自動算出）
- 振り返り管理（学習日・学習時間・学んだこと・詰まったこと・次にやることを記録）
- 検索・絞り込み（キーワード、カテゴリ、ステータス、優先度、学習目標）
- ダッシュボード表示（学習中/完了済み目標数、未完了タスク数、今月の学習時間、期限が近いタスク、最近の振り返り）
- 共通のメッセージ表示（登録/更新/削除完了、入力エラー）

認証機能は設計書の方針どおり初期実装の対象外としていますが、`LearningGoal.user` は
`AUTH_USER_MODEL` への外部キーとして用意してあるため、ログイン機能を追加すれば
`request.user` に紐づけて学習目標を管理する形に自然に拡張できます。

## 補足

- DBは開発用に SQLite を使用しています（`skilltrail/settings.py` の `DATABASES` を変更すれば
  PostgreSQL / MySQL 等にも切り替え可能です）。
- カテゴリ削除時、紐づく学習目標がある場合は `on_delete=models.PROTECT` により削除できないようにしています
  （DB設計書「10. 削除時の考慮」に準拠）。
- 学習目標を削除すると、紐づくロードマップ・タスク・振り返りも CASCADE で削除されます。
