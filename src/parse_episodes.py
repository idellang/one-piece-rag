# add necessary imports
import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse


def parse_anime(url, headers=None):
    """
    Fetches and parses a single anime episode page with robust safeguards.
    Returns a dictionary of episode data, or None if the page fails to load.
    Missing fields within the page will be set to None.
    """
    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code != 200:
            # Return None for pages that don't exist (like future episodes)
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred fetching {url}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    episode_data = {'url': url}

    # From infobox
    infobox = soup.find('aside', class_='portable-infobox')
    if infobox:
        # Episode Number (with fallback)
        try:
            num_div = infobox.find('div', string='Episode #')
            if num_div:
                episode_data['episode_number'] = int(
                    num_div.find_next_sibling('div').get_text(strip=True))
            else:  # Fallback
                nav_tag = infobox.find('nav', class_='pi-navigation')
                span_tag = nav_tag.find('span', class_='nomobile')
                num_match = re.search(r'\d+', span_tag.get_text(strip=True))
                episode_data['episode_number'] = int(
                    num_match.group(0)) if num_match else None
        except (AttributeError, ValueError):
            episode_data['episode_number'] = None

        # Titles and Airdate
        try:
            title_div = infobox.find('h2', class_='pi-title')
            episode_data['episode_title'] = title_div.get_text(
                strip=True, separator=' ') if title_div else None
        except AttributeError:
            episode_data['episode_title'] = None
        try:
            date_div = infobox.find(
                'h3', string='Airdate').find_next_sibling('div')
            episode_data['air_date'] = parse(date_div.get_text(strip=True).split('[')[
                                             0]).strftime('%Y-%m-%d') if date_div else None
        except (AttributeError, ValueError, TypeError):
            episode_data['air_date'] = None
        try:
            chapters_div = infobox.find(
                'h3', string='Chapters').find_next_sibling('div')
            episode_data['source_chapters'] = chapters_div.get_text(
                strip=True, separator=', ') if chapters_div else None
        except AttributeError:
            episode_data['source_chapters'] = None
    else:
        episode_data.update({'episode_number': None, 'episode_title': None,
                            'air_date': None, 'source_chapters': None})

    # from Main Content ---
    main_content = soup.find('div', class_='mw-parser-output')
    if main_content:
        def get_summary_text(summary_id):
            try:
                heading = main_content.find('span', id=summary_id)
                if heading:
                    summary_ps = []
                    parent_heading = heading.find_parent(re.compile(r'h[1-6]'))
                    for sibling in parent_heading.find_next_siblings():
                        if sibling.name in ['h2', 'h3']:
                            break
                        if sibling.name == 'p':
                            summary_ps.append(sibling.get_text(strip=True))
                    return " ".join(summary_ps) if summary_ps else None
                return None
            except AttributeError:
                return None

        episode_data['short_summary'] = get_summary_text('Short_Summary')
        episode_data['long_summary'] = get_summary_text('Long_Summary')

        try:
            characters = None
            heading = main_content.find(
                'span', id='Characters_in_Order_of_Appearance')
            if heading:
                parent_heading = heading.find_parent(re.compile(r'h[1-6]'))
                next_element = parent_heading.find_next_sibling()
                ul_tag = None
                if next_element:
                    if next_element.name == 'ul':
                        ul_tag = next_element
                    elif next_element.name == 'div':
                        ul_tag = next_element.find('ul')
                if ul_tag:
                    characters = ul_tag.get_text(separator='\n', strip=True)
            episode_data['characters'] = characters
        except AttributeError:
            episode_data['characters'] = None

        try:
            notes = None
            heading = main_content.find('span', id='Anime_Notes')
            if heading:
                ul_tag = heading.find_parent(
                    re.compile(r'h[1-6]')).find_next_sibling('ul')
                if ul_tag:
                    notes_list = [li.get_text(strip=True) for li in ul_tag.find_all(
                        'li', recursive=False)]
                    notes = "\n".join(notes_list)
            episode_data['anime_notes'] = notes
        except AttributeError:
            episode_data['anime_notes'] = None

        try:
            trivia = None
            heading = main_content.find('span', id='Trivia')
            if heading:
                ul_tag = heading.find_parent(
                    re.compile(r'h[1-6]')).find_next_sibling('ul')
                if ul_tag:
                    for sup in ul_tag.find_all('sup'):
                        sup.decompose()
                    trivia_list = [li.get_text(
                        strip=True) for li in ul_tag.find_all('li', recursive=False)]
                    trivia = "\n".join(trivia_list)
            episode_data['trivia'] = trivia
        except AttributeError:
            episode_data['trivia'] = None
    else:
        episode_data.update({'short_summary': None, 'long_summary': None,
                            'characters': None, 'anime_notes': None, 'trivia': None})

    return episode_data


if __name__ == "__main__":
    # Example usage
    url = "https://onepiece.fandom.com/wiki/Episode_1000"
    episode_info = parse_anime(url)
    print(episode_info)
