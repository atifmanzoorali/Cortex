import re

def test_revenue_extraction():
    # Test cases from video titles
    titles = [
        'How I Work: $77K/Month Solopreneur',
        'I Spent 24 Hours With A SaaS Millionaire',
        'I Made $1.5M From An App',
        'My Niche Mobile App Makes $20KMonth',
        'How This App Makes $35KMonth',
        'I Make $250KMonth From 13 Businesses',
        'I Make $17KMonth With One Strategy',
        'I Make $60KMonth From the Most Boring SaaS',
        'I Made $500K From 8 Different Income Streams',
        'I Built a $100KMonth Android App'
    ]
    
    for title in titles:
        # Simple pattern: find $XXK or $XXM
        match = re.search(r'\$(\d+)([KM])', title)
        if match:
            amount = float(match.group(1))
            multiplier = 1000 if match.group(2) == 'K' else 1000000
            revenue = amount * multiplier
            print(f'{title[:40]:40} -> ${revenue:,.0f}')
        else:
            print(f'{title[:40]:40} -> No revenue found')

if __name__ == '__main__':
    test_revenue_extraction()
