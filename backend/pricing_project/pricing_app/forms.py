from django import forms

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class SuperUserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter superuser username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Enter password'
    }))

    def confirm_login_allowed(self, user):
        if not user.is_superuser:
            raise forms.ValidationError(
                "Only superusers are allowed to log in.",
                code='superuser_only',
            )


class PricePredictionForm(forms.Form):
    product_id = forms.IntegerField(label="Product ID")
    sales_units = forms.IntegerField(label="Sales Units")
    holiday_season = forms.ChoiceField(choices=[(1, "Yes"), (0, "No")], label="Holiday Season")
    promotion_applied = forms.ChoiceField(choices=[(1, "Yes"), (0, "No")], label="Promotion Applied")
    competitor_price_index = forms.FloatField(label="Competitor Price Index")
    economic_index = forms.FloatField(label="Economic Index")
    weather_impact = forms.FloatField(label="Weather Impact")
    discount_percentage = forms.FloatField(label="Discount Percentage (0-1)")
    sales_revenue = forms.FloatField(label="Sales Revenue")

    # categorical features
    region = forms.ChoiceField(choices=[("Europe", "Europe"), ("North America", "North America")])
    store_type = forms.ChoiceField(choices=[("Retail", "Retail"), ("Wholesale", "Wholesale")])
    category = forms.ChoiceField(choices=[
        ("Cabinets", "Cabinets"),
        ("Chairs", "Chairs"),
        ("Sofas", "Sofas"),
        ("Tables", "Tables"),
    ])

    date = forms.DateField(label="Date (dd-mm-yyyy)", input_formats=['%d-%m-%Y'])
