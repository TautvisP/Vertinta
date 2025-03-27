from django.contrib import admin
from .models import Order, Object, ObjectMeta, UploadedDocument, ObjectImage, Notification, ImageAnnotation, SimilarObject, SimilarObjectMetadata, NearbyOrganization


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'agency', 'status', 'priority', 'created')
    search_fields = ('client__username', 'agency__username', 'status')
    list_filter = ('status', 'priority', 'created')

@admin.register(Object)
class ObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_type', 'latitude', 'longitude')
    search_fields = ('object_type',)
    list_filter = ('object_type', 'latitude', 'longitude')

@admin.register(ObjectMeta)
class ObjectMetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'ev_object', 'meta_key', 'meta_value')
    search_fields = ('ev_object__id', 'meta_key')
    list_filter = ('meta_key',)

@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'file_name', 'uploaded_at')
    search_fields = ('order__id', 'file_name')
    list_filter = ('uploaded_at',)

@admin.register(ObjectImage)
class ObjectImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'object', 'category', 'comment', 'image', 'uploaded_at')
    search_fields = ('object__id', 'category')
    list_filter = ('category', 'uploaded_at')

@admin.register(ImageAnnotation)
class ImageAnnotationAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'x_coordinate', 'y_coordinate', 'annotation_text', 'annotation_image', 'created_at')
    search_fields = ('image__id', 'annotation_text')
    list_filter = ('created_at',)

@admin.register(SimilarObject)
class SimilarObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'original_object', 'price', 'link', 'description')
    search_fields = ('original_object__id', 'description')
    list_filter = ('price',)

@admin.register(SimilarObjectMetadata)
class SimilarObjectMetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'similar_object', 'key', 'value')
    search_fields = ('similar_object__id', 'key', 'value')
    list_filter = ('key',)

@admin.register(NearbyOrganization)
class NearbyOrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'object', 'name', 'distance', 'category', 'latitude', 'longitude')
    search_fields = ('object__id', 'name', 'category')
    list_filter = ('category',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'notification_type', 'title', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('recipient__email', 'title', 'message')
    raw_id_fields = ('recipient', 'sender', 'related_order', 'related_report')