from django.urls import path
from . import views
from .views.main_view import EditEvaluatorAccountView, EvaluationStepsView,  RCDataEditView, index
from .views.object_data_view import EditObjectDataView, EditEvaluationAndDecoInfo, EditCommonInfo, EditUtilityInfo, EvaluatorEditAdditionalBuildings
from .views.object_gallery_view import EditObjectGalleryView, ImageAnnotationView, AnnotationDetailView
from .views.similar_objects_view import SimilarObjectSearchView, SimilarObjectListView, SimilarObjectResultsView, EditSimilarObjectDataView, EditSimilarObjectDecorationView, EditSimilarObjectCommonInfoView, EditSimilarObjectUtilityInfoView

app_name = 'modules.evaluator'

urlpatterns = [
    path('', index, name='evaluator_index'),
    path('edit/', EditEvaluatorAccountView.as_view(), name='edit_own_evaluator_account'),

    #used for agency to edit evaluator profile
    path('edit/<int:pk>/', EditEvaluatorAccountView.as_view(), name='edit_evaluator_account'),

    #multi step evaluation process
    #0
    path('evaluation_steps/<int:order_id>/', EvaluationStepsView.as_view(), name='evaluation_steps'),
    
    #1
    path('evaluation_steps/<int:order_id>/edit_object_data/<int:pk>/', EditObjectDataView.as_view(), name='edit_object_data'),
    path('evaluation_steps/<int:order_id>/edit_evaluation_decoration/<int:pk>/', EditEvaluationAndDecoInfo.as_view(), name='edit_evaluation_decoration'),
    path('evaluation_steps/<int:order_id>/edit_common_info/<int:pk>/', EditCommonInfo.as_view(), name='edit_common_info'),
    path('evaluation_steps/<int:order_id>/edit_utility_info/<int:pk>/', EditUtilityInfo.as_view(), name='edit_utility_info'),
    
    #2
    path('evaluation_steps/<int:order_id>/edit_additional_buildings/<int:pk>/', EvaluatorEditAdditionalBuildings.as_view(), name='edit_additional_buildings'),
    
    #3
    path('evaluation_steps/<int:order_id>/edit_RC_data/<int:pk>/', RCDataEditView.as_view(), name='edit_RC_data'),

    #4
    path('evaluation_steps/<int:order_id>/edit_gallery/<int:pk>/', EditObjectGalleryView.as_view(), name='edit_gallery'),
    path('evaluation_steps/<int:order_id>/image_annotation/<int:image_id>/', ImageAnnotationView.as_view(), name='image_annotation'),
    path('api/annotations/<int:annotation_id>/', AnnotationDetailView.as_view(), name='annotation_detail'),

    #5
    path('evaluation_steps/<int:order_id>/similar_object_search/<int:pk>/', SimilarObjectSearchView.as_view(), name='similar_object_search'),
    path('evaluation_steps/<int:order_id>/similar_object_list/<int:pk>/', SimilarObjectListView.as_view(), name='similar_object_list'),
    path('evaluation_steps/<int:order_id>/similar_object_results/<int:pk>/', SimilarObjectResultsView.as_view(), name='similar_object_results'),

    #Similar object addition and editing
    path('evaluation_steps/<int:order_id>/edit_similar_object_data/<int:pk>/', EditSimilarObjectDataView.as_view(), name='edit_similar_object_data'),
    path('evaluation_steps/<int:order_id>/edit_similar_object_decoration/<int:pk>/<int:similar_object_id>/', EditSimilarObjectDecorationView.as_view(), name='edit_similar_object_decoration'),
    path('evaluation_steps/<int:order_id>/edit_similar_object_common_info/<int:pk>/<int:similar_object_id>/', EditSimilarObjectCommonInfoView.as_view(), name='edit_similar_object_common_info'),
    path('evaluation_steps/<int:order_id>/edit_similar_object_utility_info/<int:pk>/<int:similar_object_id>/', EditSimilarObjectUtilityInfoView.as_view(), name='edit_similar_object_utility_info'),


]