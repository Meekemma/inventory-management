from django.apps import AppConfig


class InventoryManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory_management'

    def ready(self):
        import inventory_management.signals
