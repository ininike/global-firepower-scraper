import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re

DOMAIN = "https://www.globalfirepower.com"

class GlobalFirePowerScraper:
    def __init__(self):
        pass
        
    def search(self, country_id: str) -> list:
        """run search in an event loop"""
        results = asyncio.run(self._search(country_id))
        return results
       
    async def _search(self, country_id) -> list:
        """Search EFCC site based on a keyword"""
        async with aiohttp.ClientSession() as session:
            html = await self._get_page(session, country_id)
            if html:
                results = self._extract_content(html)
                return results
            return []

    async def _get_page(self, session, country_id) -> str | None:
        """Search for the results of the first page"""
        url = f"{DOMAIN}/country-military-strength-detail.php?country_id={country_id}"
        try:
            async with session.get(url) as response:
                html = await response.text()
                return html
        except Exception as e:
            print("Error:", e)
            return None

    def _extract_content(self, html) -> list:
        """Extract search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = {}
        
        results_headers = [ (header.text.rstrip(' [+]')).lower() for header in soup.select(".contentStripInner .collapsible")]
        for header in results_headers:
            match header:
                case 'at-a-glance':
                    content = (soup.find("button",string="AT-A-GLANCE [+]")).find_next_sibling("div")
                    graph_data = self._get_graph_data(soup)
                    
                    results['at-a-glance'] = {
                        'graph_data': graph_data,
                        'graph_info': (content.select_one(".textSmall2").text.strip()).replace('\r\n                            ',' '),
                        'country_info': content.select_one(".textNormal").text.strip(),
                        'quick_facts': [ (fact.text.lower()).strip() for fact in content.select('.glanceDescription') ]
                    }
                    
                case 'overview':
                    content = (soup.find("button",string="OVERVIEW [+]")).find_next_sibling("div")
                    rankings = content.select('.rankBaseContainer')
                    ranks = {}
                    for ranking in rankings:
                        rank_title = ranking.select_one(".textNormal").text.strip()
                        rank_value = ranking.select_one(".textJumbo").text.strip() + ranking.select_one(".textSmall1").text.strip() 
                        ranks[rank_title] = rank_value
                        
                    results['overview'] = {
                        'ranks': ranks,
                        'capabilities': [ (capability.text.lower()).strip() for capability in content.select('.capabilitiesBoxes')]
                    }
                    
                case 'capital':
                    content = (soup.find("button",string="CAPITAL [+]")).find_next_sibling("div")
                    capital = (content.select_one("div:nth-of-type(1)").text.split(': '))[1]
                    population = (content.select_one("div:nth-of-type(2)").text.split(':'))[1]
                    monthly_temperatures = content.select(".calenderContainers")
                    temperatures = {}
                    for month in monthly_temperatures:
                        month_name = (month.select_one(".textNormal").text.strip())[:3]
                        month_temp = month.select_one(".textBold").text.strip()
                        temperatures[month_name] = month_temp

                    results['capital'] = {
                        'capital_name': capital,
                        'capital_population': population,
                        'average_monthly_temperatures': temperatures,
                        'metric': "Average monthly temperatures are presented in Farenheit (°F)."
                    }
            
                case 'financials':
                    content = (soup.find("button",string="FINANCIALS [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['metric'] = 'All monetary values presented in United States Dollar (USD$).'
                    
                    results['financials'] = stats
            
                case 'geography':
                    content = (soup.find("button",string="GEOGRAPHY [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['metric'] = 'All distances presented in kilometers (km).'
                    
                    results['geography'] = stats
                    
                case 'manpower':
                    content = (soup.find("button",string="MANPOWER [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['description'] = 'The following values detail the maximum, theoretical persons the nation can commit to a war effort. The percentages represent the percentage of the total population'
                    
                    results['manpower'] = stats
                    
                case 'airpower':
                    content = (soup.find("button",string="AIRPOWER [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['description'] = "These following values tracks specific categories related to aerial warfare capabilities of a given power. Rates are based on the U.S. Air Force's 75 percent average across all categories to account for availability of individual over-battlefield assets due against the backdrop of general maintenance, modernization, refurbishment and the like. Percent values are a percentage of total inventory stock available."
                    
                    results['air-power'] = stats
                    
                case 'land forces':
                    content = (soup.find("button",string="LAND FORCES [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['description'] = "These following values track specific categories related to land warfare capabilities of a given power.  rates are based against the U.S. Army's 80 percent average across all categories to account for availability of individual battlefield assets due to general maintenance, modernization, refurbishment and the like."
                    
                    results['land forces'] = stats
                    
                case 'naval forces':
                    content = (soup.find("button",string="NAVAL FORCES [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    hull_containers = content.select(".hullClassContainers")
                    hull_types_descriptions = {}
                    for hull in hull_containers:
                        hull_type = hull.select_one(".textNormal").text.strip()
                        hull_description = hull.select_one(".textSmall1").text.strip()
                        hull_types_descriptions[hull_type] = hull_description
                        stats['hull_types_descriptions'] = hull_types_descriptions
                    
                    results['naval forces'] = stats
                    
                case 'end-use products':
                    content = (soup.find("button",string="END-USE PRODUCTS [+]")).find_next_sibling("div")
                    results['end-use products'] = {
                        'description': "End-use products reflect a given nation's ability to produce goods and services through manufacturing, industry, and / or agriculture. The entries reflect industries that would become stressed, disrupted, or spoils-of-war in the event of Total War.",
                        'products': [ (product.text.lower()).strip() for product in soup.select('.prodTitleContainer') ]
                    }
                case 'natural resources':
                    content = (soup.find("button",string="NATURAL RESOURCES [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    stats['metrics'] = "Oil bbl represented as unit 'barrel of oil'. Natural Gas represented in 'cubic meters'. Coal represented in 'metric tons'."
                    
                    results['natural resources'] = stats
                    
                case 'logistics':
                    content = (soup.find("button",string="LOGISTICS [+]")).find_next_sibling("div")
                    stats = self._extract_statistics(content)
                    
                    results['logistics'] = stats
                    
                case _:
                    pass
        results['comparable_powers'] = [ country.text.strip() for country in soup.select(".moreLikePanel .textLargest") ]
        results['neighbouring_powers'] = [ country.text.strip() for country in soup.select(".neighborPanel .textLargest") ]
        return results
    
    def _get_graph_data(self, soup) -> dict:
        """Extract the graph data from the page"""
        scripts = soup.find_all('script')
        for s in scripts:
            script_text = s.string
            if script_text:
                data_match = re.search(r"data: (\[.*?\])", script_text)
                if data_match:
                    values = eval(data_match.group(1))
                    labels = ['Manpower', 'Airpower', 'Land Power', 'Naval Power', 'Financials']
                    graph_data = dict(zip(labels, values))
                    return graph_data
    
    def _extract_statistics(self, content_html) -> dict:
        """Scrape the statistics from a category's content"""
        stats = {}
        statistics = content_html.select(".specsGenContainers")
        for stat in statistics:
            title = stat.select_one(".textLarge:nth-of-type(1)").text.strip()
            value = stat.select_one(".textLarge:nth-of-type(2)").text.strip()
            value = value.replace('\t', '').replace('\n', '').replace('R', ', R').replace('            ', '') #clean the output of the strings 
            value_2 = stat.select_one(".textLarge:nth-of-type(3)")
            if value_2:
                value = [ value, value_2.text.strip() ]
            rank = stat.select_one(".specsRankBox")
            if not rank:
                stats[title] = {'quantity': value, 'rank': None}
                return stats
            rank = rank.text.strip()
            stats[title] = {'quantity': value, 'rank': rank}
        return stats
        
    
    

gfp = GlobalFirePowerScraper()
print(gfp.search("united-states-of-america"))


