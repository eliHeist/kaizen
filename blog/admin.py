from django.contrib import admin

from blog.models import Author, Category, Post, Tag
from destinations.admin import SEO_FIELDSET, thumb


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'role')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = ((None, {'fields': ('name', 'slug', 'description', 'order')}), SEO_FIELDSET)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'preview', 'category', 'author', 'status', 'published_at', 'is_featured')
    list_editable = ('status', 'is_featured')
    list_filter = ('status', 'category', 'author', 'tags', 'is_featured')
    search_fields = ('title', 'excerpt', 'body')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('tags',)
    filter_horizontal = ('destinations', 'places', 'itineraries')
    date_hierarchy = 'published_at'
    save_on_top = True
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'excerpt', 'cover', 'body')}),
        ('Publishing', {'fields': ('status', 'published_at', 'author', 'category', 'tags', 'is_featured')}),
        ('Related trips and places', {'fields': ('destinations', 'places', 'itineraries')}),
        SEO_FIELDSET,
    )

    @admin.display(description='Cover')
    def preview(self, obj):
        return thumb(obj.cover)
