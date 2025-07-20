import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import validators
from fake_useragent import UserAgent
import time

def scrape_website(url):
    """Main scraping function that handles all websites"""
    try:
        headers = {'User-Agent': UserAgent().random}
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = response.url

        #extarct data
        data = {
            'URL': url,
            'Company_Name': extract_company_name(soup, url),
            'Email': extract_emails(soup),
            'Phone': extract_phones(soup),
            **extract_social_links(soup, base_url),
            'Description': extract_description(soup),
            'Founded': extract_founded_year(soup),
            'Address': extract_address(soup),
            'Industry': extract_industry(soup),
            'Employees': extract_employee_count(soup),
            'Revenue': extract_revenue(soup),
            'Technologies': extract_technologies(soup),
            'Competitors': detect_competitors(soup),
            'Market_Position': detect_market_position(soup),
            'Last_Updated': time.strftime("%Y-%m-%d %H:%M:%S")
        }

       
        return clean_scraped_data(data)

    except Exception as e:
        return error_result(url, str(e))

# Extraction Functions
def extract_company_name(soup, url):
    """Extract company name using multiple methods"""
    # 1. From meta tags
    for meta in soup.find_all('meta'):
        if meta.get('property', '').lower() in ['og:site_name', 'og:title']:
            name = meta.get('content', '').strip()
            if name: return name
    
    # 2. From title tag
    if soup.title and soup.title.string:
        name = soup.title.string.strip()
       
        name = re.sub(r' - Home Page$| - Official Site$| \|.*$', '', name)
        if name: return name
    
    # 3. From prominent headings
    for tag in ['h1', 'h2']:
        heading = soup.find(tag)
        if heading and heading.string:
            name = heading.string.strip()
            if len(name) > 3 and len(name) < 50:  
                return name
    
    # 4. From URL as fallback
    domain = url.split('//')[-1].split('/')[0]
    return domain.replace('www.', '').split('.')[0].title()

def extract_emails(soup):
    """Find all professional emails on page"""
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = set(re.findall(email_regex, soup.text))
    
    # Filter out personal/disposable emails
    professional_emails = [
        e for e in emails 
        if not any(domain in e for domain in 
                  ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'example.com'])
    ]
    
    return ', '.join(professional_emails[:3]) if professional_emails else 'Not found'

def extract_phones(soup):
    """Extract phone numbers with international formats"""
    phone_regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,3}\)?[-.\s]?\d{2,4}[-.\s]?\d{2,4}'
    phones = set(re.findall(phone_regex, soup.text))
    
   
    valid_phones = [p for p in phones if len(re.sub(r'\D', '', p)) >= 7]
    return ', '.join(valid_phones[:3]) if valid_phones else 'Not found'

def extract_social_links(soup, base_url):
    """Find all social media links"""
    social_links = {
        'LinkedIn': '-',
        'Twitter': '-',
        'Facebook': '-',
        'Instagram': '-',
        'YouTube': '-'
    }
    
    platforms = {
        'LinkedIn': ['linkedin.com'],
        'Twitter': ['twitter.com', 'x.com'],
        'Facebook': ['facebook.com'],
        'Instagram': ['instagram.com'],
        'YouTube': ['youtube.com', 'youtu.be']
    }
    
    for a in soup.find_all('a', href=True):
        href = a['href'].lower()
        for platform, domains in platforms.items():
            if any(domain in href for domain in domains):
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(base_url, href)
                social_links[platform] = href
                break
    
    return social_links

def extract_description(soup):
    """Get company description from meta or content"""
   
    desc = (soup.find('meta', attrs={'name': 'description'}) or 
            soup.find('meta', attrs={'property': 'og:description'}))
    if desc and desc.get('content'):
        return desc['content'].strip()
    
  
    paragraphs = [p.get_text(' ', strip=True) for p in soup.find_all('p')]
    ideal_paragraphs = [p for p in paragraphs if 50 < len(p) < 250]
    if ideal_paragraphs:
        return ideal_paragraphs[0]
    
   
    for h in soup.find_all(['h1', 'h2', 'h3']):
        next_p = h.find_next('p')
        if next_p and next_p.get_text(strip=True):
            return next_p.get_text(' ', strip=True)[:200] + '...'
    
    return 'Not available'



def clean_scraped_data(data):
    """Clean and standardize all scraped data"""

    for field in ['Description', 'Address']:
        if data[field] and len(data[field]) > 200:
            data[field] = data[field][:200] + '...'
    
   
    for key in data:
        if data[key] in ('', None, '-', []):
            data[key] = 'Not available'
    
    return data

def error_result(url, error_msg):
    """Standard error response"""
    return {
        'URL': url,
        'Company_Name': f'Error: {error_msg}',
        'Email': 'Not available',
        'Phone': 'Not available',
        'LinkedIn': 'Not available',
        'Twitter': 'Not available',
        'Facebook': 'Not available',
        'Instagram': 'Not available',
        'Description': 'Not available',
        'Founded': 'Not available',
        'Address': 'Not available',
        'Industry': 'Not available',
        'Employees': 'Not available',
        'Revenue': 'Not available',
        'Technologies': 'Not available',
        'Competitors': 'Not available',
        'Market_Position': 'Not available',
        'Last_Updated': time.strftime("%Y-%m-%d %H:%M:%S")
    }

def scrape_data(search_query, seed_urls):
    """Main function to handle multiple URLs"""
    results = []
    
    if isinstance(seed_urls, str):
        seed_urls = [url.strip() for url in seed_urls.split(',') if validators.url(url.strip())]
    
    for url in seed_urls:
        time.sleep(1)  
        results.append(scrape_website(url))
    
    return results
def extract_founded_year(soup):
    """Extract founding year from page content"""
  
    patterns = [
        r'(?:Founded|Established|Est\.?|Since)\s*(?:in)?\s*(\d{4})',
        r'©\s*\d{4}-?(\d{4})?',
        r'Copyright\s*[©\s]+\d{4}-?(\d{4})?'
    ]
    for pattern in patterns:
        match = re.search(pattern, soup.text, re.IGNORECASE)
        if match:
            return match.group(1) or match.group(0)
    
   
    footer = soup.find('footer') or soup.find(class_=re.compile('footer', re.I))
    if footer:
        year_match = re.search(r'\b(19\d{2}|20\d{2})\b', footer.text)
        if year_match:
            return year_match.group(0)
    
    return 'Not available'

def extract_address(soup):
    """Extract physical address from page"""

    address_tag = soup.find('address')
    if address_tag:
        return address_tag.get_text(' ', strip=True)
    
   
    for elem in soup.find_all(['p', 'div', 'section']):
        text = elem.get_text(' ', strip=True).lower()
        if 'address' in text and 20 < len(text) < 200:
            return elem.get_text(' ', strip=True)

    for class_name in ['address', 'contact-info', 'location']:
        elem = soup.find(class_=re.compile(class_name, re.I))
        if elem:
            return elem.get_text(' ', strip=True)
    
    return 'Not available'

def extract_industry(soup):
    """Extract industry or business category"""
    # Try meta keywords
    keywords = soup.find('meta', attrs={'name': 'keywords'})
    if keywords and keywords.get('content'):
        return keywords['content'].split(',')[0].strip()
    
   
    for tag in ['h1', 'h2', 'h3']:
        for heading in soup.find_all(tag):
            text = heading.get_text(' ', strip=True).lower()
            if any(word in text for word in ['industry', 'sector', 'category']):
                return heading.get_text(' ', strip=True)
    
    return 'Not available'

def extract_employee_count(soup):
    """Extract approximate employee count"""
    patterns = [
        r'(\d{1,5})\s*(?:employees|staff|team)',
        r'team\s*of\s*(\d{1,5})',
        r'over\s*(\d{1,5})\s*people'
    ]
    for pattern in patterns:
        match = re.search(pattern, soup.text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return 'Not available'

def extract_revenue(soup):
    """Extract revenue information"""
    patterns = [
        r'(?:revenue|sales)\s*(?:of|:)?\s*\$?(\d+\.?\d*\s*[MB]?)',
        r'\$(\d+\.?\d*\s*[mb]illion)'
    ]
    for pattern in patterns:
        match = re.search(pattern, soup.text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return 'Not available'

def extract_technologies(soup):
    """Extract technologies used"""
    tech_keywords = [
        'wordpress', 'shopify', 'react', 'angular', 
        'django', 'rails', 'node', 'php', 'aws'
    ]
    found_tech = []
    text = soup.text.lower()
    
    for tech in tech_keywords:
        if tech in text:
            found_tech.append(tech.title())
    
    return ', '.join(found_tech) if found_tech else 'Not available'

def detect_competitors(soup):
    """Detect mentions of competitors"""
    if re.search(r'competitors?|alternatives|similar (?:companies|services)', 
                soup.text, re.IGNORECASE):
        return 'Mentions competitors'
    return 'No competitor mentions'

def detect_market_position(soup):
    """Detect market position indicators"""
    indicators = {
        'Leader': ['leader in', 'market leader', 'industry leader'],
        'Top': ['top rated', 'top provider', r'top \d+'],
        'Growing': ['fast growing', 'rapidly growing']
    }
    
    text = soup.text.lower()
    for position, keywords in indicators.items():
        if any(re.search(keyword, text) for keyword in keywords):
            return position
    
    return 'Not specified'