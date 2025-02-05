from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()




USER_GROUP = 'User'
ADMIN_GROUP = 'Admin'

@receiver(post_save, sender=User)
def user_grouping(sender, instance, created, *args, **kwargs):
    """
    Automatically assign users to default groups upon creation.
    """
    if created:
        try:
            # Ensure the necessary groups are created
            user_group, _ = Group.objects.get_or_create(name=USER_GROUP)
            admin_group, _ = Group.objects.get_or_create(name=ADMIN_GROUP)

            # Assign user to the "User" group by default
            instance.groups.add(user_group)

            # If the user is an admin (is_staff and is_superuser), assign to the "Admin" group
            if instance.is_staff and instance.is_superuser:
                instance.groups.add(admin_group)
        except Exception as e:
            print(f"Error in user grouping: {e}")
