# run.py
import subprocess
import sys
import os


def main():
    print("=" * 50)
    print("Morocco Football Team Dashboard")
    print("=" * 50)

    print("\nOptions:")
    print("1. Run Streamlit Dashboard")
    print("2. Run Scraper Only")
    print("3. Install Dependencies")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == '1':
        print("\n🚀 Starting Streamlit dashboard...")
        print("The app will open in your browser at http://localhost:8501")
        print("Press Ctrl+C to stop the server")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])

    elif choice == '2':
        print("\n📊 Running scraper only...")
        from scraper import scrape_morocco_team_table, save_to_csv, get_summary_stats

        df = scrape_morocco_team_table()
        if df is not None:
            save_to_csv(df)
            stats = get_summary_stats(df)

            print(f"\n✅ Scraped {stats['total_players']} players")
            print(f"📁 Data saved to 'morocco_football_team.csv'")
        else:
            print("❌ Failed to scrape data")

    elif choice == '3':
        print("\n📦 Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    elif choice == '4':
        print("\n👋 Goodbye!")

    else:
        print("\n❌ Invalid choice. Please run again.")


if __name__ == "__main__":
    main()