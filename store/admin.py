from django.contrib import admin

from .models import Category, Product

# Register your models here.


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug"]
    prepopulated_fields = {
        "slug": ("name",)
    }  # Slug Field will be prepopulated with same value as Category Name


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author",
        "slug",
        "price",
        "in_stock",
        "is_active",
        "created",
        "updated",
    ]
    list_filter = ["in_stock", "is_active"]
    list_editable = ["price", "in_stock"]
    prepopulated_fields = {
        "slug": ("title",)
    }  # Slug Field will be prepopulated with same value as Product Title name
