from django import forms


class CheckoutForm(forms.Form):
    address = forms.CharField(label='Адрес доставки', widget=forms.Textarea(attrs={'rows': 3}))
    phone = forms.CharField(label='Телефон', max_length=20)
    email = forms.EmailField(label='Email')
    comment = forms.CharField(label='Комментарий к заказу', required=False, widget=forms.Textarea(attrs={'rows': 2}))