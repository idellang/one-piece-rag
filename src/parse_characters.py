import requests
from bs4 import BeautifulSoup
import re


def parse_infobox(url):
    """
    Parse character details from a One Piece wiki character page.

    Args:
        url (str): URL of the character page

    Returns:
        dict: Dictionary containing character information
    """

    scraper_headers = {
        'User-Agent': 'OnePieceRAGBot/1.0 Character Parser - jfcastaneda.led@gmail.com'
    }

    try:
        response = requests.get(url, headers=scraper_headers)
        if response.status_code != 200:
            return {'url': url, 'error': f'Failed to retrieve page. Status code: {response.status_code}'}

        soup = BeautifulSoup(response.content, 'html.parser')
        character_data = {'url': url}

        # Find infobox
        infobox = soup.find('aside', class_='portable-infobox')
        if not infobox:
            return {'url': url, 'error': 'No infobox found'}

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
                label_tag = infobox.find(
                    'b', string=re.compile("Affiliations:"))
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
                label_tag = infobox.find(
                    'b', string=re.compile("Occupation(s)?:"))
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

        # parse status
        try:
            status = None
            origin_section = infobox.find('h2', string='Status')
            if origin_section:
                origin_div = origin_section.find_next(
                    'div', class_='pi-data-value')
                if origin_div:
                    origin = origin_div.get_text(strip=True)

            if not residence:
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
                eng_name_tag = df_section.find_next(
                    'h3', string='English Name:')
                if eng_name_tag:
                    devil_fruit_data['english_name'] = eng_name_tag.find_next_sibling(
                        'div').get_text(strip=True)

                jpn_name_tag = df_section.find_next(
                    'h3', string='Japanese Name:')
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
            bounty_container = infobox.find(
                'div', attrs={'data-source': 'bounty'})

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

    except Exception as e:
        return {'url': url, 'error': f'Exception occurred: {str(e)}'}
