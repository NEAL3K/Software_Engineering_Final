"""
URL configuration for Database_Supermarket project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from Database import views as v

urlpatterns = [
    path("", v.home, name="home"),
    path("admin/", admin.site.urls),
    path("login/", v.login),
    path("home/", v.home),
    path('register/', v.register),
    path("detail/", v.show_personal_info),
    path("cart/",v.cart),
    path("remove_from_cart/",v.remove_from_cart),
    path("update_cart/",v.update_cart),
    path("inventory/", v.inventory),
    path("inventory/modify/", v.modify),
    path('edit_product/', v.edit_product, name='edit_product'),
    # --------------------------------
    path("importi/", v.importi),
    path("importi/modify/", v.modify),
    path("importi/importi_modify/", v.importi_modify),
    path("importi/importi_modify_add/", v.importi_modify_add),
    path("importilog/", v.importilog),
    # --------------------------------
    path("exporti/", v.exporti),
    path("exorti/modify/", v.modify),
    path("exporti/exporti_modify/", v.exporti_modify),
    path("exporti/exporti_modify_add/", v.exporti_modify_add),
    path("exportilog/", v.exportilog),
    # --------------------------------
    path("superadmin/", v.superadmin),
    path("superadmin/importi_modify_add/", v.importi_modify_add),
    path("superadmin/modify/", v.modify),
    path("logout/", v.logout),
]
