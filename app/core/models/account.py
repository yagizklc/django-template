from django.db import models
from django.contrib.auth.models import User
from core.models.organization import Organization


class AccountManager(models.Manager):
    def create_account(
        self, username: str, email: str, password: str, organization_id: int
    ) -> "Account":
        user = User.objects.create_user(
            username=username, email=email, password=password
        )
        try:
            account = Account.objects.create(user=user, organization_id=organization_id)
        except Exception as e:
            user.delete()
            raise e
        return account

    def authenticate(self, username: str, password: str) -> "Account":
        user = User.objects.get(username=username)
        if user.check_password(password):
            return Account.objects.get(user=user)
        raise Exception("Invalid credentials")


class Account(models.Model):
    """
    Proxy model for users
    Holds user related information other than authentication
    https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#extending-the-existing-user-model
    """

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    objects = models.Manager()
    manager = AccountManager()
