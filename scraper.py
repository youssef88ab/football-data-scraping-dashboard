# scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re


def scrape_morocco_team_table():
    url = "https://en.wikipedia.org/wiki/Morocco_national_football_team"

    try:
        # Send request to Wikipedia
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Method 1: Look for tables with players section heading
        players_section = None
        for h2 in soup.find_all(['h2', 'h3', 'h4']):
            if 'player' in h2.get_text(strip=True).lower():
                players_section = h2
                break

        target_table = None

        # First try to find table near players section
        if players_section:
            next_element = players_section.find_next_sibling()
            while next_element:
                if next_element.name == 'table':
                    target_table = next_element
                    break
                next_element = next_element.find_next_sibling()

        # If not found, try all tables on page
        if not target_table:
            all_tables = soup.find_all('table')
            for i, table in enumerate(all_tables):
                table_text = table.get_text()
                if any(keyword in table_text.lower() for keyword in ['gk', 'df', 'mf', 'fw', 'caps', 'goals']):
                    headers = []
                    try:
                        header_row = table.find('tr')
                        for th in header_row.find_all(['th', 'td']):
                            header_text = th.get_text(strip=True)
                            headers.append(header_text)
                        if any(hdr in str(headers) for hdr in ['No.', 'Pos.', 'Player', 'Caps', 'Goals']):
                            target_table = table
                            break
                    except:
                        continue

        if not target_table:
            return None

        # Extract headers
        headers = []
        header_row = target_table.find('tr')
        if not header_row:
            thead = target_table.find('thead')
            if thead:
                header_row = thead.find('tr')

        if header_row:
            for th in header_row.find_all(['th', 'td']):
                header_text = th.get_text(strip=True)
                if header_text == 'No.':
                    headers.append('Number')
                elif header_text == 'Pos.':
                    headers.append('Position')
                elif header_text == 'Player':
                    headers.append('Player')
                elif 'Date of birth' in header_text or 'Birth' in header_text:
                    headers.append('Date_of_Birth')
                elif header_text == 'Caps':
                    headers.append('Caps')
                elif header_text == 'Goals':
                    headers.append('Goals')
                elif header_text == 'Club':
                    headers.append('Club')
                else:
                    headers.append(header_text)
        else:
            headers = ['Number', 'Position', 'Player', 'Date_of_Birth', 'Caps', 'Goals', 'Club']

        # Extract data rows
        data = []
        tbody = target_table.find('tbody')
        rows = tbody.find_all('tr') if tbody else target_table.find_all('tr')[1:]

        for row in rows:
            if 'sortbottom' in row.get('class', []) or 'mw-empty-elt' in row.get('class', []):
                continue

            row_data = []
            cells = row.find_all(['td', 'th'])

            if len(cells) >= 4:
                for i, cell in enumerate(cells):
                    text = cell.get_text(strip=True, separator=' ')

                    if i == 0:
                        text = re.sub(r'\[.*?\]', '', text)
                    elif i == 2:
                        text = re.sub(r'\[.*?\]', '', text)
                    elif i == 3:
                        text = re.sub(r'\(age.*?\)', '', text)
                        text = re.sub(r'[()]', '', text).strip()

                    row_data.append(text)

                while len(row_data) < len(headers):
                    row_data.append('')

                data.append(row_data[:len(headers)])

        if not data:
            return None

        # Create DataFrame
        df = pd.DataFrame(data, columns=headers)

        # Clean the data
        df = df[df['Player'].notna() & (df['Player'] != '')]

        # Convert numeric columns
        for col in ['Number', 'Caps', 'Goals']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Extract birth year and calculate age
        if 'Date_of_Birth' in df.columns:
            df['Birth_Year'] = df['Date_of_Birth'].str.extract(r'(\d{4})')
            df['Birth_Year'] = pd.to_numeric(df['Birth_Year'], errors='coerce')
            from datetime import datetime
            current_year = datetime.now().year
            df['Age'] = current_year - df['Birth_Year']

        # Calculate goal ratio
        if all(col in df.columns for col in ['Caps', 'Goals']):
            df['Goal_Ratio'] = df.apply(
                lambda x: x['Goals'] / x['Caps'] if x['Caps'] > 0 else 0,
                axis=1
            )

        return df

    except Exception as e:
        print(f"Error: {e}")
        return None


def save_to_csv(df, filename='morocco_football_team.csv'):
    """Save DataFrame to CSV file"""
    if df is not None:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"✅ Data saved to {filename}")
        return True
    return False


def get_summary_stats(df):
    """Get summary statistics from the DataFrame"""
    if df is None:
        return {}

    stats = {
        'total_players': len(df),
        'positions': {},
        'total_caps': 0,
        'total_goals': 0,
        'avg_age': None,
        'top_scorer': None,
        'most_experienced': None
    }

    if 'Position' in df.columns:
        stats['positions'] = df['Position'].value_counts().to_dict()

    if 'Caps' in df.columns:
        stats['total_caps'] = int(df['Caps'].sum())

    if 'Goals' in df.columns:
        stats['total_goals'] = int(df['Goals'].sum())

    if 'Age' in df.columns:
        stats['avg_age'] = float(df['Age'].mean())

    if all(col in df.columns for col in ['Player', 'Goals']):
        if not df['Goals'].isna().all():
            top_idx = df['Goals'].idxmax()
            stats['top_scorer'] = {
                'name': df.loc[top_idx, 'Player'],
                'goals': int(df.loc[top_idx, 'Goals']),
                'caps': int(df.loc[top_idx, 'Caps']) if 'Caps' in df.columns else 0
            }

    if all(col in df.columns for col in ['Player', 'Caps']):
        if not df['Caps'].isna().all():
            top_idx = df['Caps'].idxmax()
            stats['most_experienced'] = {
                'name': df.loc[top_idx, 'Player'],
                'caps': int(df.loc[top_idx, 'Caps']),
                'goals': int(df.loc[top_idx, 'Goals']) if 'Goals' in df.columns else 0
            }

    return stats


if __name__ == "__main__":
    # Run as standalone script
    print("=" * 70)
    print("SCRAPING MOROCCO NATIONAL FOOTBALL TEAM DATA")
    print("=" * 70)

    df = scrape_morocco_team_table()

    if df is not None:
        print(f"✅ Successfully scraped {len(df)} players!")

        # Save to CSV
        save_to_csv(df)

        # Print summary
        stats = get_summary_stats(df)
        print("\n📊 SUMMARY STATISTICS:")
        print("-" * 40)
        print(f"Total Players: {stats['total_players']}")

        if stats['positions']:
            print("\nPlayers by Position:")
            for pos, count in stats['positions'].items():
                print(f"  {pos}: {count}")

        print(f"\nTotal Caps: {stats['total_caps']:,}")
        print(f"Total Goals: {stats['total_goals']:,}")

        if stats['avg_age']:
            print(f"Average Age: {stats['avg_age']:.1f}")

        if stats['top_scorer']:
            scorer = stats['top_scorer']
            print(f"\n🏆 Top Scorer: {scorer['name']} ({scorer['goals']} goals, {scorer['caps']} caps)")

        if stats['most_experienced']:
            exp = stats['most_experienced']
            print(f"🎖️ Most Experienced: {exp['name']} ({exp['caps']} caps, {exp['goals']} goals)")

        print("\n📋 First 5 players:")
        print(df[['Number', 'Position', 'Player', 'Caps', 'Goals', 'Club']].head().to_string(index=False))
    else:
        print("❌ Failed to scrape data")