from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("signup/borrower/", views.BorrowerSignUp.as_view(), name="borrowersignup"),
    path("signup/lender/", views.LenderSignUp.as_view(), name="lendersignup")
]
