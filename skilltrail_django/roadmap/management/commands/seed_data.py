from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from roadmap.models import Category, LearningGoal, LearningTask, Reflection, Roadmap


class Command(BaseCommand):
    help = "デモ用のサンプルデータを投入します（既存の学習データは削除されます）"

    def handle(self, *args, **options):
        today = timezone.localdate()

        def d(offset):
            return today + timedelta(days=offset)

        self.stdout.write("既存データを削除しています…")
        Reflection.objects.all().delete()
        LearningTask.objects.all().delete()
        Roadmap.objects.all().delete()
        LearningGoal.objects.all().delete()
        Category.objects.all().delete()

        categories = {
            name: Category.objects.create(name=name, description=desc)
            for name, desc in [
                ("Python", "Pythonの基礎・応用"),
                ("Django", "DjangoによるWebアプリ開発"),
                ("AWS", "AWSサービスの学習"),
                ("Frontend", "HTML、CSS、JavaScriptなど"),
            ]
        }

        g1 = LearningGoal.objects.create(
            category=categories["Django"],
            title="DjangoでWebアプリを作れるようになる",
            purpose="業務で使うDjangoの基礎から実践までを一通り身につける",
            start_date=d(-30),
            target_date=d(45),
            status=LearningGoal.STATUS_IN_PROGRESS,
            memo="まずはCRUD、次に認証、最後にデプロイまで",
        )
        g2 = LearningGoal.objects.create(
            category=categories["AWS"],
            title="AWS Lambdaの基礎を理解する",
            purpose="サーバーレス構成の基本を理解し、簡単なAPIを構築できるようにする",
            start_date=d(-5),
            target_date=d(30),
            status=LearningGoal.STATUS_NOT_STARTED,
        )
        g3 = LearningGoal.objects.create(
            category=categories["Frontend"],
            title="Reactでダッシュボードを構築する",
            purpose="実務レベルのReact設計パターンを習得する",
            start_date=d(-60),
            target_date=d(-2),
            status=LearningGoal.STATUS_COMPLETED,
            memo="hooksの設計に慣れた",
        )
        g4 = LearningGoal.objects.create(
            category=categories["Python"],
            title="Pythonの非同期処理を理解する",
            purpose="asyncioの動きを理解して非同期APIを書けるようにする",
            start_date=d(-10),
            target_date=d(20),
            status=LearningGoal.STATUS_SUSPENDED,
            memo="一旦AWS学習を優先するため中断",
        )

        r1 = Roadmap.objects.create(
            learning_goal=g1, title="Djangoの基本構成を理解する",
            description="プロジェクト構成、settings、アプリの作り方を理解する",
            sort_order=1, status=Roadmap.STATUS_COMPLETED,
        )
        r2 = Roadmap.objects.create(
            learning_goal=g1, title="ModelとDB連携を理解する",
            description="ORM、マイグレーション、クエリの書き方を学ぶ",
            sort_order=2, status=Roadmap.STATUS_IN_PROGRESS,
        )
        r3 = Roadmap.objects.create(
            learning_goal=g1, title="Templateで画面を作成する",
            description="テンプレート継承と静的ファイルの扱いを理解する",
            sort_order=3, status=Roadmap.STATUS_NOT_STARTED,
        )
        Roadmap.objects.create(
            learning_goal=g1, title="認証機能を実装する",
            description="ログイン・ログアウト・権限管理を実装する",
            sort_order=4, status=Roadmap.STATUS_NOT_STARTED,
        )
        r5 = Roadmap.objects.create(
            learning_goal=g2, title="Lambdaの基本概念を理解する",
            description="サーバーレスの考え方とLambdaの仕組みを理解する",
            sort_order=1, status=Roadmap.STATUS_NOT_STARTED,
        )
        r6 = Roadmap.objects.create(
            learning_goal=g3, title="コンポーネント設計を理解する",
            description="再利用可能なコンポーネントの設計方法を学ぶ",
            sort_order=1, status=Roadmap.STATUS_COMPLETED,
        )
        r7 = Roadmap.objects.create(
            learning_goal=g3, title="状態管理を理解する",
            description="useState/useReducerの使い分けを理解する",
            sort_order=2, status=Roadmap.STATUS_COMPLETED,
        )
        r8 = Roadmap.objects.create(
            learning_goal=g4, title="asyncio入門",
            description="コルーチンとイベントループの基礎を学ぶ",
            sort_order=1, status=Roadmap.STATUS_IN_PROGRESS,
        )

        tasks = [
            (r1, "Djangoプロジェクトを作成する", "https://docs.djangoproject.com/", "high", d(-25), "completed"),
            (r1, "アプリを作成しURLを設定する", "", "medium", d(-22), "completed"),
            (r2, "URLとViewの関係を確認する", "https://docs.djangoproject.com/en/5.0/topics/http/urls/", "medium", d(2), "in_progress"),
            (r2, "Modelを作成しmigrateする", "", "high", d(4), "not_started"),
            (r2, "QuerySetの基本操作を試す", "", "low", d(9), "not_started"),
            (r3, "テンプレート継承を試す", "", "medium", d(16), "not_started"),
            (r5, "Lambda関数を1つ作成してみる", "https://docs.aws.amazon.com/lambda/", "high", d(6), "not_started"),
            (r6, "共通ボタンコンポーネントを作る", "", "medium", d(-40), "completed"),
            (r7, "useReducerでフォーム状態を管理する", "", "medium", d(-10), "completed"),
            (r8, "async/awaitの基本構文を試す", "", "high", d(1), "in_progress"),
            (r8, "asyncioのタスクを並行実行してみる", "", "low", d(12), "not_started"),
        ]
        for roadmap, title, url, priority, due, status in tasks:
            LearningTask.objects.create(
                roadmap=roadmap, title=title, material_url=url,
                priority=priority, due_date=due, status=status,
            )

        reflections = [
            (g1, d(-2), 60,
             "DjangoのURLルーティングの仕組みを理解した。path converterの使い分けが分かった。",
             "名前空間付きURLの逆引きで少し詰まった", "include()を使った分割方法を試す"),
            (g1, d(-1), 90,
             "ModelとMigrationの流れを確認した。ForeignKeyのon_deleteの挙動を試した。",
             "マイグレーションの巻き戻しで少し混乱した", "QuerySetのfilter/excludeを練習する"),
            (g3, d(-45), 45,
             "propsのバケツリレーを解消するためContext APIを導入した", "", "Context分割の粒度を検討する"),
            (g4, d(-8), 30,
             "asyncio.gatherで複数タスクを並行実行できることを確認した",
             "例外処理の伝播がよく分からなかった", "try/exceptとgatherの組み合わせを調べる"),
        ]
        for goal, date, minutes, learned, problem, next_action in reflections:
            Reflection.objects.create(
                learning_goal=goal, study_date=date, study_time=minutes,
                learned=learned, problem=problem, next_action=next_action,
            )

        self.stdout.write(self.style.SUCCESS("サンプルデータを投入しました。"))
