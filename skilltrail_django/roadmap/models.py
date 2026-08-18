from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """categories: 学習カテゴリを管理する"""

    name = models.CharField("カテゴリ名", max_length=100, unique=True)
    description = models.TextField("説明", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "カテゴリ"
        verbose_name_plural = "カテゴリ"
        ordering = ["name"]

    def __str__(self):
        return self.name


class LearningGoal(models.Model):
    """learning_goals: 学習目標を管理する"""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_SUSPENDED = "suspended"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "未着手"),
        (STATUS_IN_PROGRESS, "学習中"),
        (STATUS_COMPLETED, "完了"),
        (STATUS_SUSPENDED, "中断"),
    ]

    # 認証機能は初期実装の対象外のため null / blank を許容する
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="ユーザー",
        on_delete=models.CASCADE,
        related_name="learning_goals",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        verbose_name="カテゴリ",
        on_delete=models.PROTECT,
        related_name="learning_goals",
    )
    title = models.CharField("タイトル", max_length=200)
    purpose = models.TextField("目的", blank=True)
    start_date = models.DateField("開始日", null=True, blank=True)
    target_date = models.DateField("目標期限", null=True, blank=True)
    status = models.CharField(
        "ステータス", max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    memo = models.TextField("メモ", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "学習目標"
        verbose_name_plural = "学習目標"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("roadmap:goal_detail", args=[self.pk])

    @property
    def tasks(self):
        """この学習目標に紐づく全タスク（ロードマップ経由）"""
        return LearningTask.objects.filter(roadmap__learning_goal=self)

    @property
    def total_task_count(self):
        return self.tasks.count()

    @property
    def completed_task_count(self):
        return self.tasks.filter(status=LearningTask.STATUS_COMPLETED).count()

    @property
    def progress_rate(self):
        """進捗率 = 完了タスク数 / 全タスク数 × 100（0件の場合は0%）"""
        total = self.total_task_count
        if total == 0:
            return 0
        return round(self.completed_task_count / total * 100)

    @property
    def total_study_minutes(self):
        return self.reflections.aggregate(total=models.Sum("study_time"))["total"] or 0


class Roadmap(models.Model):
    """roadmaps: 学習目標に紐づく学習ステップを管理する"""

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "未着手"),
        (STATUS_IN_PROGRESS, "進行中"),
        (STATUS_COMPLETED, "完了"),
    ]

    learning_goal = models.ForeignKey(
        LearningGoal, verbose_name="学習目標", on_delete=models.CASCADE, related_name="roadmaps"
    )
    title = models.CharField("ステップ名", max_length=200)
    description = models.TextField("説明", blank=True)
    sort_order = models.PositiveIntegerField("並び順", default=1)
    status = models.CharField(
        "ステータス", max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "ロードマップステップ"
        verbose_name_plural = "ロードマップステップ"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.learning_goal.title} - {self.title}"

    @property
    def task_count(self):
        return self.tasks.count()


class LearningTask(models.Model):
    """learning_tasks: ロードマップに紐づく学習タスクを管理する"""

    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    PRIORITY_CHOICES = [
        (PRIORITY_HIGH, "高"),
        (PRIORITY_MEDIUM, "中"),
        (PRIORITY_LOW, "低"),
    ]

    STATUS_NOT_STARTED = "not_started"
    STATUS_IN_PROGRESS = "in_progress"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_NOT_STARTED, "未着手"),
        (STATUS_IN_PROGRESS, "進行中"),
        (STATUS_COMPLETED, "完了"),
    ]

    roadmap = models.ForeignKey(
        Roadmap, verbose_name="ロードマップ", on_delete=models.CASCADE, related_name="tasks"
    )
    title = models.CharField("タスク名", max_length=200)
    material_url = models.URLField("教材URL", max_length=500, blank=True)
    priority = models.CharField(
        "優先度", max_length=10, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM
    )
    due_date = models.DateField("期限", null=True, blank=True)
    status = models.CharField(
        "ステータス", max_length=20, choices=STATUS_CHOICES, default=STATUS_NOT_STARTED
    )
    memo = models.TextField("メモ", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "学習タスク"
        verbose_name_plural = "学習タスク"
        ordering = ["due_date", "id"]

    def __str__(self):
        return self.title

    @property
    def learning_goal(self):
        return self.roadmap.learning_goal

    @property
    def is_overdue(self):
        if not self.due_date or self.status == self.STATUS_COMPLETED:
            return False
        return self.due_date < timezone.localdate()


class Reflection(models.Model):
    """reflections: 学習の振り返りを管理する"""

    learning_goal = models.ForeignKey(
        LearningGoal, verbose_name="学習目標", on_delete=models.CASCADE, related_name="reflections"
    )
    study_date = models.DateField("学習日")
    study_time = models.PositiveIntegerField("学習時間（分）", null=True, blank=True)
    learned = models.TextField("学んだこと")
    problem = models.TextField("詰まったこと", blank=True)
    next_action = models.TextField("次にやること", blank=True)
    created_at = models.DateTimeField("作成日時", auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    class Meta:
        verbose_name = "振り返り"
        verbose_name_plural = "振り返り"
        ordering = ["-study_date", "-id"]

    def __str__(self):
        return f"{self.learning_goal.title} ({self.study_date})"
