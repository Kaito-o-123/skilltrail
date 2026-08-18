from django import forms

from .models import LearningGoal, LearningTask, Reflection, Roadmap


class StyledFormMixin:
    """全フィールドのウィジェットに共通CSSクラス(input)を付与する。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " input").strip()


class RoadmapSelect(forms.Select):
    """ロードマップ選択肢に data-goal 属性を付与し、学習目標選択に応じて
    JS側で候補を絞り込めるようにするためのカスタムウィジェット。"""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        raw_value = value.value if hasattr(value, "value") else value
        if raw_value not in (None, ""):
            roadmap = Roadmap.objects.filter(pk=raw_value).select_related("learning_goal").first()
            if roadmap:
                option["attrs"]["data-goal"] = roadmap.learning_goal_id
        return option


class GoalForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = LearningGoal
        fields = ["title", "category", "purpose", "start_date", "target_date", "status", "memo"]
        labels = {
            "title": "タイトル",
            "category": "カテゴリ",
            "purpose": "目的",
            "start_date": "開始日",
            "target_date": "目標期限",
            "status": "ステータス",
            "memo": "メモ",
        }
        widgets = {
            "purpose": forms.Textarea(attrs={"rows": 3, "placeholder": "なぜ学習するのか"}),
            "memo": forms.Textarea(attrs={"rows": 3, "placeholder": "補足情報"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "title": forms.TextInput(attrs={"placeholder": "例）DjangoでWebアプリを作れるようになる"}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_date")
        target = cleaned.get("target_date")
        if start and target and target < start:
            self.add_error("target_date", "目標期限は開始日以降の日付にしてください。")
        return cleaned


class RoadmapForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Roadmap
        fields = ["title", "description", "sort_order", "status"]
        labels = {
            "title": "ステップ名",
            "description": "説明",
            "sort_order": "並び順",
            "status": "ステータス",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "title": forms.TextInput(attrs={"placeholder": "例）ModelとDB連携を理解する"}),
        }

    def clean_sort_order(self):
        value = self.cleaned_data["sort_order"]
        if value is None or value < 1:
            raise forms.ValidationError("並び順は1以上の数値で入力してください。")
        return value


class TaskForm(StyledFormMixin, forms.ModelForm):
    goal = forms.ModelChoiceField(
        label="学習目標",
        queryset=LearningGoal.objects.all().order_by("-created_at"),
        required=True,
    )

    class Meta:
        model = LearningTask
        fields = ["roadmap", "title", "material_url", "priority", "due_date", "status", "memo"]
        labels = {
            "roadmap": "ロードマップ",
            "title": "タスク名",
            "material_url": "教材URL",
            "priority": "優先度",
            "due_date": "期限",
            "status": "ステータス",
            "memo": "メモ",
        }
        widgets = {
            "memo": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "material_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "roadmap": RoadmapSelect,
        }

    field_order = ["goal", "roadmap", "title", "material_url", "priority", "due_date", "status", "memo"]

    def __init__(self, *args, initial_goal=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["roadmap"].queryset = Roadmap.objects.select_related("learning_goal").order_by(
            "learning_goal_id", "sort_order"
        )
        if self.instance.pk:
            self.fields["goal"].initial = self.instance.roadmap.learning_goal_id
        elif initial_goal is not None:
            self.fields["goal"].initial = initial_goal.pk

    def clean(self):
        cleaned = super().clean()
        goal = cleaned.get("goal")
        roadmap = cleaned.get("roadmap")
        if goal and roadmap and roadmap.learning_goal_id != goal.pk:
            self.add_error("roadmap", "選択した学習目標に紐づくロードマップを選択してください。")
        return cleaned


class ReflectionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Reflection
        fields = ["learning_goal", "study_date", "study_time", "learned", "problem", "next_action"]
        labels = {
            "learning_goal": "学習目標",
            "study_date": "学習日",
            "study_time": "学習時間（分）",
            "learned": "学んだこと",
            "problem": "詰まったこと",
            "next_action": "次にやること",
        }
        widgets = {
            "study_date": forms.DateInput(attrs={"type": "date"}),
            "learned": forms.Textarea(attrs={"rows": 3}),
            "problem": forms.Textarea(attrs={"rows": 3}),
            "next_action": forms.Textarea(attrs={"rows": 3}),
            "study_time": forms.NumberInput(attrs={"min": 0, "placeholder": "例）60"}),
        }
