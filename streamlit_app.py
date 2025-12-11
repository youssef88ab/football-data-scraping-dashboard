# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import the scraper module
try:
    from scraper import scrape_morocco_team_table, get_summary_stats
except ImportError:
    st.error("Error: Could not import scraper module. Make sure scraper.py is in the same directory.")
    st.stop()

# Set page configuration
st.set_page_config(
    page_title="Morocco Football Team Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #3B82F6;
        font-family: 'Arial Black', sans-serif;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2563EB;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-left: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        margin: 0.5rem;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    .player-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 5px solid #3B82F6;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #F0F2F6;
        border-radius: 5px 5px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Cache the data scraping function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return scrape_morocco_team_table()


# Sidebar
with st.sidebar:
    st.title("⚽ Dashboard Controls")

    st.markdown("---")

    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    # Filters
    st.subheader("🔍 Filters")

    # Load data first for filters
    df = load_data()

    if df is not None:
        # Position filter
        positions = sorted(df['Position'].unique())
        selected_positions = st.multiselect(
            "Select Positions",
            positions,
            default=positions,
            placeholder="All positions"
        )

        # Caps range filter
        if 'Caps' in df.columns:
            min_caps, max_caps = st.slider(
                "Caps Range",
                int(df['Caps'].min()),
                int(df['Caps'].max()),
                (0, int(df['Caps'].max()))
            )

        # Goals range filter
        if 'Goals' in df.columns:
            min_goals, max_goals = st.slider(
                "Goals Range",
                int(df['Goals'].min()),
                int(df['Goals'].max()),
                (0, int(df['Goals'].max()))
            )

        # Age filter (if available)
        if 'Age' in df.columns:
            min_age, max_age = st.slider(
                "Age Range",
                int(df['Age'].min()),
                int(df['Age'].max()),
                (int(df['Age'].min()), int(df['Age'].max()))
            )

    st.markdown("---")

    # Info section
    st.info("""
    **Dashboard Info:**
    - Data is fetched from Wikipedia
    - Auto-refresh every hour
    - Click refresh to get latest data
    """)

# Main content
st.markdown('<h1 class="main-header">🇲🇦 Morocco National Football Team Dashboard</h1>', unsafe_allow_html=True)

# Load data with spinner
with st.spinner("Loading team data..."):
    df = load_data()

if df is None:
    st.error("❌ Failed to load data. Please check your internet connection and try again.")
    st.stop()

# Apply filters
if 'df' in locals():
    filtered_df = df.copy()

    if 'selected_positions' in locals() and selected_positions:
        filtered_df = filtered_df[filtered_df['Position'].isin(selected_positions)]

    if 'min_caps' in locals() and 'max_caps' in locals() and 'Caps' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Caps'] >= min_caps) & (filtered_df['Caps'] <= max_caps)]

    if 'min_goals' in locals() and 'max_goals' in locals() and 'Goals' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Goals'] >= min_goals) & (filtered_df['Goals'] <= max_goals)]

    if 'min_age' in locals() and 'max_age' in locals() and 'Age' in filtered_df.columns:
        filtered_df = filtered_df[(filtered_df['Age'] >= min_age) & (filtered_df['Age'] <= max_age)]

# Display key metrics
st.markdown('<h2 class="sub-header">📊 Team Overview</h2>', unsafe_allow_html=True)

# Create metrics columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:,}</div>
        <div class="metric-label">Total Players</div>
    </div>
    """.format(len(filtered_df)), unsafe_allow_html=True)

with col2:
    total_caps = int(filtered_df['Caps'].sum()) if 'Caps' in filtered_df.columns else 0
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:,}</div>
        <div class="metric-label">Total Caps</div>
    </div>
    """.format(total_caps), unsafe_allow_html=True)

with col3:
    total_goals = int(filtered_df['Goals'].sum()) if 'Goals' in filtered_df.columns else 0
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:,}</div>
        <div class="metric-label">Total Goals</div>
    </div>
    """.format(total_goals), unsafe_allow_html=True)

with col4:
    avg_age = float(filtered_df['Age'].mean()) if 'Age' in filtered_df.columns else 0
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">{:.1f}</div>
        <div class="metric-label">Average Age</div>
    </div>
    """.format(avg_age), unsafe_allow_html=True)

# Create tabs for different views
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Player Roster",
    "📈 Statistics",
    "🎯 Top Performers",
    "🏢 Club Analysis",
    "📊 Data Explorer"
])

with tab1:
    st.markdown('<h3 class="sub-header">Player Roster</h3>', unsafe_allow_html=True)

    # Search functionality
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_query = st.text_input("Search players by name:", "",
                                     placeholder="Type player name to search...")

    # Display filtered data
    display_df = filtered_df.copy()
    if search_query:
        display_df = display_df[display_df['Player'].str.contains(search_query, case=False, na=False)]

    # Select columns to display
    default_cols = ['Number', 'Position', 'Player', 'Age', 'Caps', 'Goals', 'Club']
    available_cols = [col for col in default_cols if col in display_df.columns]

    # Format the dataframe display
    st.dataframe(
        display_df[available_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Number": st.column_config.NumberColumn("No.", format="%d"),
            "Caps": st.column_config.NumberColumn("Caps", format="%d"),
            "Goals": st.column_config.NumberColumn("Goals", format="%d"),
            "Age": st.column_config.NumberColumn("Age", format="%d"),
            "Player": st.column_config.TextColumn("Player", width="large"),
            "Club": st.column_config.TextColumn("Club", width="medium"),
        }
    )

with tab2:
    st.markdown('<h3 class="sub-header">Team Statistics</h3>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        # Position distribution pie chart
        if 'Position' in filtered_df.columns:
            position_counts = filtered_df['Position'].value_counts().reset_index()
            position_counts.columns = ['Position', 'Count']

            fig1 = px.pie(
                position_counts,
                values='Count',
                names='Position',
                title="Players by Position",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4
            )
            fig1.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Age distribution histogram
        if 'Age' in filtered_df.columns:
            fig2 = px.histogram(
                filtered_df,
                x='Age',
                nbins=15,
                title="Age Distribution",
                color_discrete_sequence=['#3B82F6'],
                opacity=0.8
            )
            fig2.update_layout(bargap=0.1)
            st.plotly_chart(fig2, use_container_width=True)

    # Caps vs Goals scatter plot
    if all(col in filtered_df.columns for col in ['Caps', 'Goals']):
        fig3 = px.scatter(
            filtered_df,
            x='Caps',
            y='Goals',
            size='Goals',
            color='Position',
            hover_name='Player',
            title="Caps vs Goals Analysis",
            size_max=20,
            opacity=0.7
        )
        fig3.update_layout(
            xaxis_title="Number of Caps",
            yaxis_title="Number of Goals"
        )
        st.plotly_chart(fig3, use_container_width=True)

with tab3:
    st.markdown('<h3 class="sub-header">Top Performers</h3>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🏆 Top Scorers")
        if 'Goals' in filtered_df.columns:
            top_scorers = filtered_df.nlargest(5, 'Goals')[['Player', 'Goals', 'Caps', 'Club']]
            for idx, row in top_scorers.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="player-card">
                        <strong>{row['Player']}</strong><br>
                        ⚽ {int(row['Goals'])} goals | 👕 {int(row['Caps'])} caps<br>
                        🏢 {row['Club']}
                    </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.subheader("🎖️ Most Experienced")
        if 'Caps' in filtered_df.columns:
            most_caps = filtered_df.nlargest(5, 'Caps')[['Player', 'Caps', 'Goals', 'Club']]
            for idx, row in most_caps.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="player-card">
                        <strong>{row['Player']}</strong><br>
                        👕 {int(row['Caps'])} caps | ⚽ {int(row['Goals'])} goals<br>
                        🏢 {row['Club']}
                    </div>
                    """, unsafe_allow_html=True)

    with col3:
        st.subheader("📊 Best Goal Ratio")
        if all(col in filtered_df.columns for col in ['Caps', 'Goals']):
            filtered_df['Goal_Ratio'] = filtered_df['Goals'] / filtered_df['Caps'].replace(0, 1)
            best_ratio = filtered_df[filtered_df['Caps'] >= 5].nlargest(5, 'Goal_Ratio')[
                ['Player', 'Goal_Ratio', 'Goals', 'Caps']]
            for idx, row in best_ratio.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="player-card">
                        <strong>{row['Player']}</strong><br>
                        📈 {row['Goal_Ratio']:.2f} goals/cap<br>
                        ⚽ {int(row['Goals'])} goals in {int(row['Caps'])} caps
                    </div>
                    """, unsafe_allow_html=True)

with tab4:
    st.markdown('<h3 class="sub-header">Club Analysis</h3>', unsafe_allow_html=True)

    if 'Club' in filtered_df.columns:
        # Club distribution
        club_counts = filtered_df['Club'].value_counts().reset_index()
        club_counts.columns = ['Club', 'Player Count']

        col1, col2 = st.columns([2, 1])

        with col1:
            fig4 = px.bar(
                club_counts.head(10),
                x='Club',
                y='Player Count',
                title="Top 10 Clubs by Player Count",
                color='Player Count',
                color_continuous_scale='Viridis'
            )
            fig4.update_layout(xaxis_tickangle=45)
            st.plotly_chart(fig4, use_container_width=True)

        with col2:
            st.subheader("Club Stats")
            st.dataframe(
                club_counts,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Club": st.column_config.TextColumn("Club Name"),
                    "Player Count": st.column_config.NumberColumn("Players", format="%d")
                }
            )

with tab5:
    st.markdown('<h3 class="sub-header">Data Explorer</h3>', unsafe_allow_html=True)

    # Show raw data with option to select columns
    st.subheader("Complete Dataset")

    # Let user select which columns to display
    all_columns = list(filtered_df.columns)
    default_selected = ['Number', 'Position', 'Player', 'Age', 'Caps', 'Goals', 'Club']

    selected_columns = st.multiselect(
        "Select columns to display:",
        all_columns,
        default=default_selected
    )

    if selected_columns:
        st.dataframe(
            filtered_df[selected_columns],
            use_container_width=True,
            hide_index=True
        )

    # Data download section
    st.subheader("Download Data")

    col1, col2 = st.columns(2)

    with col1:
        # Download as CSV
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"morocco_team_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # Download as JSON
        json_data = filtered_df.to_json(orient='records', indent=2)
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"morocco_team_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

# Footer
st.markdown("---")
st.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;'>
        Data sourced from Wikipedia • Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 
        Showing {len(filtered_df)} of {len(df)} players
    </div>
    """,
    unsafe_allow_html=True
)