from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
import logging

# Setup logging
logger = logging.getLogger(__name__)

User = get_user_model()

USER_GROUP = 'Buyer'
INVENTORY_MANAGER_GROUP = 'Inventory Manager'
ADMIN_GROUP = 'Admin'

@receiver(post_save, sender=User)
def user_grouping(sender, instance, created, **kwargs):
    """
    Assign users to the correct group upon creation.
    """
    try:
        # Ensure the necessary groups exist
        buyer_group, _ = Group.objects.get_or_create(name=USER_GROUP)
        inventory_manager_group, _ = Group.objects.get_or_create(name=INVENTORY_MANAGER_GROUP)
        admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP)

        # Remove any existing groups to avoid duplicate assignments
        instance.groups.clear()

        # Assign correct group AFTER the instance has been fully saved
        user = User.objects.get(pk=instance.pk)  # Fetch fresh user object

        if user.is_superuser and user.is_staff:
            user.groups.add(admin_group)
        elif user.is_staff:
            user.groups.add(inventory_manager_group)
        else:
            user.groups.add(buyer_group)

    except Exception as e:
        logger.error(f"Error in user grouping: {e}")
