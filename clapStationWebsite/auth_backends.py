# from django.contrib.auth import get_user_model
# from django.contrib.auth.backends import ModelBackend

# CustomUser = get_user_model()

# class CustomUserAuthBackend(ModelBackend):
#     def authenticate(self, request, contact=None, password=None, **kwargs):
#         try:
#             user = CustomUser.objects.get(contact=contact)
#             if user.check_password(password):
#                 return user
#         except CustomUser.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return CustomUser.objects.get(pk=user_id)
#         except CustomUser.DoesNotExist:
#             return None