from django.shortcuts import render
from django.http import HttpResponse
import json
import csv
import validators
from html import unescape  
from .forms import ScraperForm
from .scraper import scrape_data

def index(request):
    if request.method == 'POST':
        form = ScraperForm(request.POST)
        if form.is_valid():
            search_query = form.cleaned_data['search_query']
            seed_urls = [
                url.strip()
                for url in form.cleaned_data['seed_urls'].split(',')
                if validators.url(url.strip())
            ]
            results = scrape_data(search_query, seed_urls)
            request.session['scraped_results'] = results 
            context = {
                'form': form,
                'results': results,
            }
            return render(request, 'index.html', context)
    else:
        form = ScraperForm()
    return render(request, 'index.html', {'form': form})

def download_csv(request):
   
    results = request.session.get('scraped_results', [])
    
  
    if not results and request.method == 'POST':
        try:
            raw_data = request.POST.get('data', '[]')
            decoded_data = unescape(raw_data)
            results = json.loads(decoded_data)
        except Exception as e:
            return HttpResponse(f"Error processing data: {str(e)}", status=400)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scraped_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'URL', 'Company Name', 'Email', 'Phone', 
        'LinkedIn', 'Twitter', 'Description',
        'Founded', 'Address', 'Competitors', 'Market Position'
    ])
    
    for item in results:
        writer.writerow([
            item.get('URL', ''),
            item.get('Company_Name', ''),
            item.get('Email', ''),
            item.get('Phone', ''),
            item.get('LinkedIn', ''),
            item.get('Twitter', ''),
            item.get('Description', ''),
            item.get('Founded', ''),
            item.get('Address', ''),
            item.get('Competitors', ''),
            item.get('Market_Position', '')
        ])
    
    return response