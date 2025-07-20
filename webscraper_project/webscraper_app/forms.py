from django import forms

class ScraperForm(forms.Form):
    search_query = forms.CharField(
        label='Search Query (optional)', 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Fintech companies in India'})
    )
    seed_urls = forms.CharField(
        label='Seed URLs (comma-separated)',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'https://example1.com, https://example2.com'})
    )
