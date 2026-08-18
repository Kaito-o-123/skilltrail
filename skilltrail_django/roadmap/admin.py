from django.contrib import admin

from .models import Category, LearningGoal, LearningTask, Reflection, Roadmap


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


class RoadmapInline(admin.TabularInline):
    model = Roadmap
    extra = 0
    fields = ("title", "sort_order", "status")


@admin.register(LearningGoal)
class LearningGoalAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "start_date", "target_date", "progress_rate")
    list_filter = ("status", "category")
    search_fields = ("title", "purpose")
    inlines = [RoadmapInline]

    @admin.display(description="進捗率")
    def progress_rate(self, obj):
        return f"{obj.progress_rate}%"


class LearningTaskInline(admin.TabularInline):
    model = LearningTask
    extra = 0
    fields = ("title", "priority", "status", "due_date")


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("title", "learning_goal", "sort_order", "status")
    list_filter = ("status",)
    search_fields = ("title",)
    inlines = [LearningTaskInline]


@admin.register(LearningTask)
class LearningTaskAdmin(admin.ModelAdmin):
    list_display = ("title", "roadmap", "priority", "status", "due_date")
    list_filter = ("status", "priority")
    search_fields = ("title", "memo")


@admin.register(Reflection)
class ReflectionAdmin(admin.ModelAdmin):
    list_display = ("learning_goal", "study_date", "study_time")
    list_filter = ("learning_goal",)
    search_fields = ("learned", "problem", "next_action")
