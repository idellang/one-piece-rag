import requests
from bs4 import BeautifulSoup
import re


def get_page_soup(url):
    """
    Fetches the content from a URL and returns a BeautifulSoup object.

    Args:
        url (str): The URL of the page to scrape.

    Returns:
        BeautifulSoup: The parsed BeautifulSoup object of the page, or None if an error occurs.
    """
    scraper_headers = {
        'User-Agent': 'OnePieceRAGBot/1.0 Character Parser - jfcastaneda.led@gmail.com'
    }
    try:
        response = requests.get(url, headers=scraper_headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None


def parse_infobox(soup):
    """
    Parse character infobox details from BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML content

    Returns:
        dict: Dictionary containing infobox character information
    """
    character_data = {}

    # Find infobox
    infobox = soup.find('aside', class_='portable-infobox')
    if not infobox:
        return {'error': 'No infobox found'}

    # Parse name
    try:
        character_data['name'] = infobox.find(
            'h2', class_='pi-title').get_text(strip=True)
    except AttributeError:
        character_data['name'] = None

    # Parse affiliations
    try:
        affiliations = None
        label_tag = infobox.find('h3', string=re.compile("Affiliations"))
        if label_tag:
            value_tag = label_tag.find_next_sibling('div')
            if value_tag:
                affiliation_links = value_tag.find_all('a')
                affiliation_names = [link.get_text(
                    strip=True) for link in affiliation_links]
                affiliations = ", ".join(
                    affiliation_names) if affiliation_names else None

        # Fallback
        if not affiliations:
            label_tag = infobox.find('b', string=re.compile("Affiliations:"))
            if label_tag:
                value_parts = []
                for sibling in label_tag.next_siblings:
                    if getattr(sibling, 'name', None) == 'b':
                        break
                    if isinstance(sibling, str):
                        cleaned = sibling.strip().replace(':', '').strip()
                        if cleaned:
                            value_parts.append(cleaned)
                affiliations = " ".join(value_parts)

        character_data['affiliations'] = affiliations
    except:
        character_data['affiliations'] = None

    # Parse occupation
    try:
        occupations = None
        label_tag = infobox.find('h3', string=re.compile("Occupation"))
        if label_tag:
            value_tag = label_tag.find_next_sibling('div')
            if value_tag:
                for sup in value_tag.find_all('sup'):
                    sup.decompose()

                occupation_list = [text.strip().replace(';', '')
                                   for text in value_tag.stripped_strings]

                final_list = []
                for item in occupation_list:
                    if item.startswith('(') and final_list:
                        final_list[-1] += f" {item}"
                    else:
                        final_list.append(item)

                occupations = ", ".join(final_list) if final_list else None

        # Fallback
        if not occupations:
            label_tag = infobox.find('b', string=re.compile("Occupation(s)?:"))
            if label_tag:
                value_parts = []
                for sibling in label_tag.next_siblings:
                    if getattr(sibling, 'name', None) == 'b':
                        break
                    if isinstance(sibling, str):
                        cleaned = sibling.strip().replace(':', '').strip()
                        if cleaned:
                            value_parts.append(cleaned)
                occupations = " ".join(value_parts)

        character_data['occupations'] = occupations
    except:
        character_data['occupations'] = None

    # Parse origin
    try:
        origin = None
        origin_section = infobox.find('h2', string='Origin')
        if origin_section:
            origin_div = origin_section.find_next(
                'div', class_='pi-data-value')
            if origin_div:
                origin = origin_div.get_text(strip=True)

        if not origin:
            label_tag = infobox.find('h3', string=re.compile("Origin"))
            if label_tag:
                value_tag = label_tag.find_next_sibling('div')
                if value_tag:
                    origin = value_tag.get_text(strip=True)

        character_data['origin'] = origin
    except:
        character_data['origin'] = None

    # Parse residence
    try:
        residence = None
        residence_section = infobox.find('h2', string='Residence')
        if residence_section:
            residence_div = residence_section.find_next(
                'div', class_='pi-data-value')
            if residence_div:
                residence = residence_div.get_text(strip=True)

        if not residence:
            label_tag = infobox.find('h3', string=re.compile("Residence"))
            if label_tag:
                value_tag = label_tag.find_next_sibling('div')
                if value_tag:
                    residence = value_tag.get_text(strip=True)

        character_data['residence'] = residence
    except:
        character_data['residence'] = None

    # Parse birthday
    try:
        birthday = None
        birthday_section = infobox.find('h2', string='Birthday')
        if birthday_section:
            birthday_div = birthday_section.find_next(
                'div', class_='pi-data-value')
            if birthday_div:
                birthday = birthday_div.get_text(strip=True)

        if not birthday:
            label_tag = infobox.find('h3', string=re.compile("Birthday"))
            if label_tag:
                value_tag = label_tag.find_next_sibling('div')
                if value_tag:
                    birthday = value_tag.get_text(strip=True)

        character_data['birthday'] = birthday
    except:
        character_data['birthday'] = None

    # Parse status
    try:
        status = None
        status_section = infobox.find('h2', string='Status')
        if status_section:
            status_div = status_section.find_next(
                'div', class_='pi-data-value')
            if status_div:
                status = status_div.get_text(strip=True)

        if not status:
            label_tag = infobox.find('h3', string=re.compile("Status"))
            if label_tag:
                value_tag = label_tag.find_next_sibling('div')
                if value_tag:
                    status = value_tag.get_text(strip=True)

        character_data['status'] = status
    except:
        character_data['status'] = None

    # Parse devil fruit
    try:
        devil_fruit_data = {
            'english_name': None,
            'japanese_name': None,
            'meaning': None,
            'type': None
        }

        df_section = infobox.find(
            'h2', class_='pi-header', string='Devil Fruit')

        if df_section:
            eng_name_tag = df_section.find_next('h3', string='English Name:')
            if eng_name_tag:
                devil_fruit_data['english_name'] = eng_name_tag.find_next_sibling(
                    'div').get_text(strip=True)

            jpn_name_tag = df_section.find_next('h3', string='Japanese Name:')
            if jpn_name_tag:
                devil_fruit_data['japanese_name'] = jpn_name_tag.find_next_sibling(
                    'div').get_text(strip=True)

            meaning_tag = df_section.find_next('h3', string='Meaning:')
            if meaning_tag:
                devil_fruit_data['meaning'] = meaning_tag.find_next_sibling(
                    'div').get_text(strip=True)

            type_tag = df_section.find_next('h3', string='Type:')
            if type_tag:
                devil_fruit_data['type'] = type_tag.find_next_sibling(
                    'div').get_text(strip=True)

        # Fallback
        if not devil_fruit_data.get('english_name'):
            label_tag = infobox.find(
                'h3', string=re.compile("Devil Fruit Name"))
            if label_tag:
                value_tag = label_tag.find_next_sibling('div')
                if value_tag:
                    devil_fruit_data['english_name'] = value_tag.get_text(
                        strip=True)

        if devil_fruit_data.get('english_name'):
            character_data['devil_fruit'] = devil_fruit_data
        else:
            character_data['devil_fruit'] = None
    except:
        character_data['devil_fruit'] = None

    # Parse bounty
    try:
        bounty = None
        bounty_container = infobox.find('div', attrs={'data-source': 'bounty'})

        if bounty_container:
            full_text = bounty_container.get_text()
            match = re.search(r'([\d,]+)', full_text)

            if match:
                bounty = match.group(1).replace(',', '')

        character_data['bounty'] = bounty
    except:
        character_data['bounty'] = None

    # Parse debut information
    try:
        manga_debut, anime_debut = None, None
        label_tag = infobox.find(
            'h3', string=lambda text: text and "Debut" in text.strip())

        if label_tag:
            value_tag = label_tag.find_next_sibling('div')
            if value_tag:
                for sup in value_tag.find_all('sup'):
                    sup.decompose()

                debut_text = value_tag.get_text(strip=True)
                parts = re.split(r'[;,]', debut_text)

                for part in parts:
                    part = part.strip()
                    if part.startswith("Chapter"):
                        manga_debut = part
                    elif part.startswith("Episode"):
                        anime_debut = part

        character_data['manga_debut'] = manga_debut
        character_data['anime_debut'] = anime_debut
    except:
        character_data['manga_debut'] = None
        character_data['anime_debut'] = None

    return character_data


def parse_main_content(soup):
    """
    Parse main content sections from BeautifulSoup object.

    Args:
        soup (BeautifulSoup): Parsed HTML content

    Returns:
        dict: Dictionary containing main content sections
    """
    content_data = {}

    main_content = soup.find('div', class_='mw-parser-output')
    if not main_content:
        return {'error': 'No main content found'}

    def parse_section(main_content, section_id_pattern):
        """
        A generic function to parse a specific section from the main content area.
        """
        section_header = main_content.find('span', id=section_id_pattern)
        if not section_header:
            return None

        section_texts = []
        element = section_header.find_parent('h2')

        for sibling in element.find_next_siblings():
            if sibling.name == 'h2':
                break

            if sibling.name == 'p':
                for sup in sibling.find_all('sup'):
                    sup.decompose()
                section_texts.append(sibling.get_text(strip=True))
            elif sibling.name == 'ul':
                for li in sibling.find_all('li'):
                    for sup in li.find_all('sup'):
                        sup.decompose()
                    section_texts.append(li.get_text(strip=True))

        return " ".join(section_texts) if section_texts else None

    # Parse general info (content before first h2)
    try:
        general_info_texts = []
        for element in main_content.find_all(recursive=False):
            if element.name == 'h2':
                break
            if element.name in ['p']:
                for sup in element.find_all('sup'):
                    sup.decompose()
                general_info_texts.append(element.get_text(strip=True))

        content_data['general_info'] = " ".join(
            general_info_texts) if general_info_texts else None
    except:
        content_data['general_info'] = None

    # Parse specific sections
    content_data['appearance'] = parse_section(main_content, "Appearance")
    content_data['personality'] = parse_section(main_content, "Personality")
    content_data['history'] = parse_section(main_content, "History")
    content_data['abilities'] = parse_section(
        main_content, re.compile(r'^Abilities_and'))
    content_data['relationships'] = parse_section(
        main_content, "Relationships")

    # Parse trivia
    try:
        trivia_header = main_content.find('span', id='Trivia')
        if trivia_header:
            trivia_texts = []
            element = trivia_header.find_parent('h2')
            for sibling in element.find_next_siblings():
                if sibling.name == 'h2':
                    break
                if sibling.name == 'ul':
                    for li in sibling.find_all('li'):
                        for sup in li.find_all('sup'):
                            sup.decompose()
                        trivia_texts.append(li.get_text(strip=True))
            content_data['trivia'] = " ".join(
                trivia_texts) if trivia_texts else None
        else:
            content_data['trivia'] = None
    except:
        content_data['trivia'] = None

    return content_data


def parse_character(url):
    """
    Orchestrator function to parse complete character information.

    Args:
        url (str): URL of the character page

    Returns:
        dict: Complete dictionary containing all character information
    """
    # Get the soup object
    soup = get_page_soup(url)
    if not soup:
        return {'url': url, 'error': 'Failed to fetch page'}

    # Initialize character data with URL
    character_data = {'url': url}

    # Parse infobox
    infobox_data = parse_infobox(soup)
    if 'error' in infobox_data:
        character_data.update(infobox_data)
        return character_data

    character_data.update(infobox_data)

    # Parse main content
    content_data = parse_main_content(soup)
    if 'error' in content_data:
        character_data['content_error'] = content_data['error']
    else:
        character_data.update(content_data)

    return character_data
