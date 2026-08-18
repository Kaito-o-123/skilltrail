from datetime import timedelta

from django.contrib import messages
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import GoalForm, ReflectionForm, RoadmapForm, TaskForm
from .models import Category, LearningGoal, LearningTask, Reflection, Roadmap


# ---------------------------------------------------------------------------
# 10. ダッシュボード表示機能 / 12. ダッシュボード表示処理
# ---------------------------------------------------------------------------
def dashboard(request):
    today = timezone.localdate()
    goals = LearningGoal.objects.select_related("category")

    in_progress_count = goals.filter(status=LearningGoal.STATUS_IN_PROGRESS).count()
    completed_count = goals.filter(status=LearningGoal.STATUS_COMPLETED).count()
    incomplete_tasks = LearningTask.objects.exclude(status=LearningTask.STATUS_COMPLETED).count()

    upcoming_tasks = (
        LearningTask.objects.select_related("roadmap__learning_goal")
        .exclude(status=LearningTask.STATUS_COMPLETED)
        .filter(due_date__isnull=False, due_date__lte=today + timedelta(days=14))
        .order_by("due_date")[:6]
    )

    month_minutes = (
        Reflection.objects.filter(study_date__year=today.year, study_date__month=today.month).aggregate(
            total=Sum("study_time")
        )["total"]
        or 0
    )

    recent_reflections = Reflection.objects.select_related("learning_goal").order_by("-study_date", "-id")[:3]
    active_goals = goals.exclude(status=LearningGoal.STATUS_COMPLETED).order_by("-updated_at")

    context = {
        "active": "dashboard",
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "incomplete_tasks": incomplete_tasks,
        "month_minutes": month_minutes,
        "upcoming_tasks": upcoming_tasks,
        "recent_reflections": recent_reflections,
        "active_goals": active_goals,
        "today": today,
    }
    return render(request, "roadmap/dashboard.html", context)


# ---------------------------------------------------------------------------
# 4. 学習目標管理機能 / 2. 3. 4. 学習目標登録・更新・削除処理
# ---------------------------------------------------------------------------
def goal_list(request):
    goals = LearningGoal.objects.select_related("category")

    keyword = request.GET.get("kw", "").strip()
    category_id = request.GET.get("category", "")
    status = request.GET.get("status", "")

    if keyword:
        goals = goals.filter(Q(title__icontains=keyword) | Q(purpose__icontains=keyword))
    if category_id:
        goals = goals.filter(category_id=category_id)
    if status:
        goals = goals.filter(status=status)

    context = {
        "active": "goals",
        "goals": goals.order_by("-created_at"),
        "categories": Category.objects.all(),
        "status_choices": LearningGoal.STATUS_CHOICES,
        "filters": {"kw": keyword, "category": category_id, "status": status},
    }
    return render(request, "roadmap/goal_list.html", context)


def goal_detail(request, pk):
    goal = get_object_or_404(LearningGoal.objects.select_related("category"), pk=pk)
    roadmaps = goal.roadmaps.prefetch_related("tasks")
    reflections = goal.reflections.all()
    context = {
        "active": "goals",
        "goal": goal,
        "roadmaps": roadmaps,
        "reflections": reflections,
    }
    return render(request, "roadmap/goal_detail.html", context)


def goal_create(request):
    if request.method == "POST":
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            if request.user.is_authenticated:
                goal.user = request.user
            goal.save()
            messages.success(request, "登録しました。")
            return redirect("roadmap:goal_list")
        messages.error(request, "入力内容を確認してください。")
    else:
        form = GoalForm()
    return render(request, "roadmap/goal_form.html", {"active": "goals", "form": form, "is_edit": False})


def goal_update(request, pk):
    goal = get_object_or_404(LearningGoal, pk=pk)
    if request.method == "POST":
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
            return redirect("roadmap:goal_detail", pk=goal.pk)
        messages.error(request, "入力内容を確認してください。")
    else:
        form = GoalForm(instance=goal)
    return render(
        request,
        "roadmap/goal_form.html",
        {"active": "goals", "form": form, "is_edit": True, "goal": goal},
    )


def goal_delete(request, pk):
    goal = get_object_or_404(LearningGoal, pk=pk)
    if request.method == "POST":
        goal.delete()
        messages.success(request, "削除しました。")
        return redirect("roadmap:goal_list")
    return render(
        request,
        "roadmap/confirm_delete.html",
        {
            "active": "goals",
            "object": goal,
            "type_label": "学習目標",
            "cancel_url": goal.get_absolute_url(),
            "warning": "紐づくロードマップ・タスク・振り返りもすべて削除されます。",
        },
    )


# ---------------------------------------------------------------------------
# 5. ロードマップ管理機能 / 5. ロードマップ登録処理
# ---------------------------------------------------------------------------
def roadmap_create(request, goal_pk):
    goal = get_object_or_404(LearningGoal, pk=goal_pk)
    if request.method == "POST":
        form = RoadmapForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.learning_goal = goal
            step.save()
            messages.success(request, "登録しました。")
            return redirect("roadmap:goal_detail", pk=goal.pk)
        messages.error(request, "入力内容を確認してください。")
    else:
        next_order = goal.roadmaps.count() + 1
        form = RoadmapForm(initial={"sort_order": next_order})
    return render(
        request,
        "roadmap/roadmap_form.html",
        {"active": "goals", "form": form, "goal": goal, "is_edit": False},
    )


def roadmap_update(request, pk):
    step = get_object_or_404(Roadmap, pk=pk)
    goal = step.learning_goal
    if request.method == "POST":
        form = RoadmapForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
            return redirect("roadmap:goal_detail", pk=goal.pk)
        messages.error(request, "入力内容を確認してください。")
    else:
        form = RoadmapForm(instance=step)
    return render(
        request,
        "roadmap/roadmap_form.html",
        {"active": "goals", "form": form, "goal": goal, "is_edit": True, "step": step},
    )


def roadmap_delete(request, pk):
    step = get_object_or_404(Roadmap, pk=pk)
    goal = step.learning_goal
    if request.method == "POST":
        step.delete()
        messages.success(request, "削除しました。")
        return redirect("roadmap:goal_detail", pk=goal.pk)
    return render(
        request,
        "roadmap/confirm_delete.html",
        {
            "active": "goals",
            "object": step,
            "type_label": "ロードマップステップ",
            "cancel_url": goal.get_absolute_url(),
            "warning": "紐づくタスクもすべて削除されます。",
        },
    )


def roadmap_move(request, pk, direction):
    """並び順変更（上へ/下へ）"""
    step = get_object_or_404(Roadmap, pk=pk)
    siblings = list(step.learning_goal.roadmaps.order_by("sort_order", "id"))
    idx = siblings.index(step)
    target_idx = idx - 1 if direction == "up" else idx + 1
    if 0 <= target_idx < len(siblings):
        other = siblings[target_idx]
        step.sort_order, other.sort_order = other.sort_order, step.sort_order
        step.save(update_fields=["sort_order"])
        other.save(update_fields=["sort_order"])
    return redirect("roadmap:goal_detail", pk=step.learning_goal_id)


# ---------------------------------------------------------------------------
# 6. 学習タスク管理機能 / 6. 7. 8. タスク登録・更新・完了処理
# ---------------------------------------------------------------------------
def task_list(request):
    tasks = LearningTask.objects.select_related("roadmap__learning_goal")

    keyword = request.GET.get("kw", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    goal_id = request.GET.get("goal", "")

    if keyword:
        tasks = tasks.filter(Q(title__icontains=keyword) | Q(memo__icontains=keyword))
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if goal_id:
        tasks = tasks.filter(roadmap__learning_goal_id=goal_id)

    context = {
        "active": "tasks",
        "tasks": tasks.order_by("due_date", "id"),
        "goals": LearningGoal.objects.all(),
        "status_choices": LearningTask.STATUS_CHOICES,
        "priority_choices": LearningTask.PRIORITY_CHOICES,
        "filters": {"kw": keyword, "status": status, "priority": priority, "goal": goal_id},
        "today": timezone.localdate(),
    }
    return render(request, "roadmap/task_list.html", context)


def task_create(request):
    initial_goal = None
    roadmap_id = request.GET.get("roadmap") or request.POST.get("roadmap_hint")
    goal_id = request.GET.get("goal")
    if roadmap_id:
        rm = Roadmap.objects.filter(pk=roadmap_id).first()
        if rm:
            initial_goal = rm.learning_goal
    elif goal_id:
        initial_goal = LearningGoal.objects.filter(pk=goal_id).first()

    next_url = request.GET.get("next", "")

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "登録しました。")
            return redirect(request.POST.get("next") or reverse("roadmap:task_list"))
        messages.error(request, "入力内容を確認してください。")
    else:
        initial = {"roadmap": roadmap_id} if roadmap_id else {}
        form = TaskForm(initial=initial, initial_goal=initial_goal)

    return render(
        request,
        "roadmap/task_form.html",
        {"active": "tasks", "form": form, "is_edit": False, "next": next_url},
    )


def task_update(request, pk):
    task = get_object_or_404(LearningTask, pk=pk)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("roadmap:task_list")
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
            return redirect(next_url)
        messages.error(request, "入力内容を確認してください。")
    else:
        form = TaskForm(instance=task)
    return render(
        request,
        "roadmap/task_form.html",
        {"active": "tasks", "form": form, "is_edit": True, "task": task, "next": next_url},
    )


def task_delete(request, pk):
    task = get_object_or_404(LearningTask, pk=pk)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("roadmap:task_list")
    if request.method == "POST":
        task.delete()
        messages.success(request, "削除しました。")
        return redirect(next_url)
    return render(
        request,
        "roadmap/confirm_delete.html",
        {
            "active": "tasks",
            "object": task,
            "type_label": "タスク",
            "cancel_url": next_url,
            "next": next_url,
        },
    )


def task_complete(request, pk):
    """8. タスク完了処理: ステータスをcompletedに更新し、進捗率は
    LearningGoal.progress_rate 経由でテンプレート側が再計算して表示する。"""
    task = get_object_or_404(LearningTask, pk=pk)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("roadmap:task_list")
    if request.method == "POST":
        task.status = LearningTask.STATUS_COMPLETED
        task.save(update_fields=["status"])
        messages.success(request, "タスクを完了にしました。")
    return redirect(next_url)


# ---------------------------------------------------------------------------
# 8. 振り返り管理機能 / 10. 振り返り登録処理
# ---------------------------------------------------------------------------
def reflection_list(request):
    reflections = Reflection.objects.select_related("learning_goal")
    goal_id = request.GET.get("goal", "")
    if goal_id:
        reflections = reflections.filter(learning_goal_id=goal_id)
    context = {
        "active": "reflections",
        "reflections": reflections.order_by("-study_date", "-id"),
        "goals": LearningGoal.objects.all(),
        "filters": {"goal": goal_id},
    }
    return render(request, "roadmap/reflection_list.html", context)


def reflection_create(request):
    goal_id = request.GET.get("goal")
    next_url = request.GET.get("next", "")
    if request.method == "POST":
        form = ReflectionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "登録しました。")
            return redirect(request.POST.get("next") or reverse("roadmap:reflection_list"))
        messages.error(request, "入力内容を確認してください。")
    else:
        initial = {"study_date": timezone.localdate()}
        if goal_id:
            initial["learning_goal"] = goal_id
        form = ReflectionForm(initial=initial)
    return render(
        request,
        "roadmap/reflection_form.html",
        {"active": "reflections", "form": form, "is_edit": False, "next": next_url},
    )


def reflection_update(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("roadmap:reflection_list")
    if request.method == "POST":
        form = ReflectionForm(request.POST, instance=reflection)
        if form.is_valid():
            form.save()
            messages.success(request, "更新しました。")
            return redirect(next_url)
        messages.error(request, "入力内容を確認してください。")
    else:
        form = ReflectionForm(instance=reflection)
    return render(
        request,
        "roadmap/reflection_form.html",
        {"active": "reflections", "form": form, "is_edit": True, "reflection": reflection, "next": next_url},
    )


def reflection_delete(request, pk):
    reflection = get_object_or_404(Reflection, pk=pk)
    next_url = request.POST.get("next") or request.GET.get("next") or reverse("roadmap:reflection_list")
    if request.method == "POST":
        reflection.delete()
        messages.success(request, "削除しました。")
        return redirect(next_url)
    return render(
        request,
        "roadmap/confirm_delete.html",
        {
            "active": "reflections",
            "object": reflection,
            "type_label": "振り返り",
            "cancel_url": next_url,
        },
    )
