from rest_framework.permissions import BasePermission

class BorrowerPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.account.type == "borrower":
            return True
        return False
    
class LenderPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.account.type == "lender":
            return True
        return False