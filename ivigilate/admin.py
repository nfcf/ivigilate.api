from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib import admin
from ivigilate.models import *
import json, logging


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            try:
                account_metadata = json.loads(obj.metadata)
                if 'setup' in account_metadata:
                    description = 'Hardware and Setup Costs + {0} Month(s) Subscription'.format(account_metadata['setup']['duration_in_months'])
                    license = License.objects.create(account=obj,
                                                     amount=account_metadata['setup']['amount'],
                                                     currency=account_metadata['setup']['currency'],
                                                     description=description,
                                                     metadata=json.dumps(account_metadata['setup']))
            except Exception as ex:
                logger.exception('Failed to create initial license for account with exception:')


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    pass


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = get_user_model()
        fields = ('account', 'email', 'password', 'first_name', 'last_name', 'metadata',
                  'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserCreationForm(forms.ModelForm):
    company_id = forms.CharField(label='Company ID')
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = get_user_model()
        fields = ('company_id', 'email')

    def clean_company_id(self):
        company_id = self.cleaned_data['company_id']
        try:
            account = Account.objects.get(company_id=company_id)
        except Account.DoesNotExist:
            raise forms.ValidationError('Invalid Company ID.')
        return account

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('confirm_password')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('Passwords don\'t match.')
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.account = self.cleaned_data['company_id']
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


@admin.register(AuthUser)
class AuthUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff',)
    fieldsets = (
        (None, {'fields': [('account', 'email', 'password'), ]}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'metadata')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                      'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login', )}),
        )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('company_id', 'email', 'first_name', 'last_name', 'password', 'confirm_password')}
         ),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email', 'first_name', 'last_name')
    filter_horizontal = ()


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass


@admin.register(Beacon)
class BeaconAdmin(admin.ModelAdmin):
    pass


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass