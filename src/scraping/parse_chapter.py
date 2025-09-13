import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse
import json


def parse_chapter(url, headers=None):
    """
    Fetches and parses single chapter page from One Piece Fandom wiki.
    Returns dictionary of chapter data
    Missing fields are set to None
    """

    # SAFEGUARD: Handle network errors and bad HTTP responses upfront.
    try:
        response = requests.get(url, timeout=10, headers=headers)
        if response.status_code != 200:
            print(
                f"Failed to retrieve the page {url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred fetching {url}: {e}")
        return None

    # if request is successful, parse the content
    soup = BeautifulSoup(response.content, 'html.parser')
    chapter_data = {
        'url': url,
    }

    # Extract from infobox
    infobox = soup.find('aside', class_='portable-infobox')

    if infobox:
        print("Extracting infobox data...")
        try:
            chapter_data['chapter_title'] = infobox.find(
                'h2', class_='pi-title').get_text(strip=True)
        except AttributeError:
            chapter_data['chapter_title'] = None

        try:
            chapter_num_div = infobox.find(
                'h3', string=re.compile("Chapter")).find_next_sibling('div')
            chapter_data['chapter_number'] = int(
                chapter_num_div.get_text(strip=True)) if chapter_num_div else None
        except (AttributeError, ValueError):
            chapter_data['chapter_number'] = None

        try:
            release_date_div = infobox.find('h3', string=re.compile(
                "Release Date:")).find_next_sibling('div')
            if release_date_div:
                raw_date_str = release_date_div.get_text(strip=True)
                date_obj = parse(raw_date_str, fuzzy=True)
                chapter_data['release_date'] = date_obj.strftime("%Y-%m-%d")
            else:
                chapter_data['release_date'] = None
        except (AttributeError, ValueError):
            chapter_data['release_date'] = None

    else:
        print("No infobox found.")
        chapter_data['chapter_title'] = None
        chapter_data['chapter_number'] = None
        chapter_data['release_date'] = None

    main_content = soup.find('div', class_='mw-parser-output')

    if main_content:
        print("Extracting main content data...")
        # Short summary
        try:
            heading = main_content.find('span', id='Short_Summary')
            if heading:
                # Use a loop to find all subsequent <p> tags until the next heading
                summary_ps = []
                for sibling in heading.find_parent('h2').find_next_siblings():
                    if sibling.name == 'p':
                        summary_ps.append(sibling.get_text(strip=True))
                    else:
                        # Stop when we hit a non-paragraph tag (like the next <h2>)
                        break
                chapter_data['short_summary'] = " ".join(
                    summary_ps) if summary_ps else None
            else:
                chapter_data['short_summary'] = None
        except AttributeError:
            chapter_data['short_summary'] = None

        # Long Summary
        try:
            # Find the heading, trying the ID first, then falling back to text search.
            heading = main_content.find('span', id='Long_Summary')
            if not heading:
                all_spans = main_content.find_all('span', class_='mw-headline')
                for span in all_spans:
                    if span.get_text(strip=True) == "Long Summary":
                        heading = span
                        break

            # If a heading was found, parse all content that follows it.
            if heading:
                # Find the parent heading tag (h2, h3, etc.) to start from.
                parent_heading = heading.find_parent(re.compile(r'h[1-6]'))
                summary_ps = []

                # Iterate through all tags that come AFTER the heading.
                for sibling in parent_heading.find_next_siblings():
                    # Stop condition: If we hit the next major heading, the section is over.
                    if sibling.name in ['h2', 'h3']:
                        break

                    # If the sibling is a div, search for p tags inside it.
                    if sibling.name == 'div':
                        summary_ps.extend([p.get_text(strip=True)
                                          for p in sibling.find_all('p')])
                    # If the sibling is a p tag itself, just grab its text.
                    elif sibling.name == 'p':
                        summary_ps.append(sibling.get_text(strip=True))

                chapter_data['long_summary'] = " ".join(
                    summary_ps) if summary_ps else None
            else:
                # If no heading was found at all, set to None.
                chapter_data['long_summary'] = None
        except AttributeError:
            # Catch any other unexpected parsing errors.
            chapter_data['long_summary'] = None

        # Characters
        try:
            chars_heading = main_content.find('span', id='Characters')
            if chars_heading:
                table_tag = chars_heading.find_parent(
                    'h3').find_next_sibling('table', class_='CharTable')
                if table_tag:
                    character_groups = {}
                    rows = table_tag.find('tbody').find_all('tr')

                    if len(rows) >= 2:
                        headers = [th.get_text(strip=True)
                                   for th in rows[0].find_all('th')]
                        data_cells = rows[1].find_all('td')

                        for i, header in enumerate(headers):
                            if i < len(data_cells):
                                cell = data_cells[i]
                                subgroups_in_cell = {}

                                # Find all <dl> tags, which define the subgroups.
                                subgroup_dls = cell.find_all('dl')

                                if subgroup_dls:
                                    for dl in subgroup_dls:
                                        dt = dl.find('dt')
                                        if not dt:
                                            continue  # Skip if a <dl> has no <dt> title

                                        subgroup_title = dt.get_text(
                                            strip=True)

                                        # STRATEGY:
                                        # First, look for a <ul> INSIDE the <dl> (Pattern A)
                                        character_ul = dl.find('ul')

                                        # If not found, look for a <ul> as the NEXT SIBLING of the <dl> (Pattern B)
                                        if not character_ul:
                                            character_ul = dl.find_next_sibling(
                                                'ul')

                                        if character_ul:
                                            characters = [li.get_text(
                                                strip=True) for li in character_ul.find_all('li')]
                                            subgroups_in_cell[subgroup_title] = characters
                                else:
                                    # Fallback for simple tables with no <dl> subgroups at all.
                                    characters = [li.get_text(
                                        strip=True) for li in cell.find_all('li')]
                                    if characters:
                                        subgroups_in_cell[header] = characters

                                character_groups[header] = subgroups_in_cell

                    chapter_data['characters'] = character_groups
            else:
                chapter_data['characters'] = None
        except (AttributeError, IndexError) as e:
            print(f"An error occurred while extracting characters: {e}")
            chapter_data['characters'] = None

        # Trivia
        try:
            heading = main_content.find('span', id='Trivia')
            if heading:
                ul = heading.find_parent('h2').find_next_sibling('ul')
                trivia = [li.get_text(strip=True)
                          for li in ul.find_all('li', recursive=False)]
                chapter_data['trivia'] = "\n".join(trivia)
            else:
                chapter_data['trivia'] = None
        except AttributeError:
            chapter_data['trivia'] = None

    else:
        print("No main content found.")
        chapter_data['short_summary'] = None
        chapter_data['long_summary'] = None
        chapter_data['notes'] = None
        chapter_data['characters'] = None
        chapter_data['trivia'] = None
        return chapter_data

    return chapter_data


if __name__ == "__main__":
    # Example usage
    test_url = "https://onepiece.fandom.com/wiki/Chapter_1050"
    scraper_headers = {
        'User-Agent': 'OnePieceRAGBot/1.0 (Learning Project; contact: jfcastaneda.led@gmail.com)'
    }
    chapter_info = parse_chapter(test_url, headers=scraper_headers)
    print(json.dumps(chapter_info, indent=2, ensure_ascii=False))
