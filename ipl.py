import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector

st.set_page_config(page_title="IPL",page_icon="🏏",layout="wide")
@st.cache_data

def load_data():
    conn=mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        db="sample"
    )
    query = "SELECT * FROM `match`"
    df=pd.read_sql(query,conn)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    conn.close()

    numeric_df=df.select_dtypes(['float','int'])
    numeric_cols=numeric_df.columns
    non_numeric_cols = list(df.select_dtypes(['object']).columns)
    non_numeric_cols.append(None)

    teams_col=df["team1"]
    teams=teams_col.unique()
    return df, numeric_cols, teams, non_numeric_cols

df, numeric_cols, teams, non_numeric_cols = load_data()
###################################################################################################
st.title("IPL Dashboard 🏏")

st.markdown("---")
check_box = st.checkbox(label="Display Dataset")
if check_box:
    st.write(df)
with st.expander("Tabular"):
        showData=st.multiselect("filter:",non_numeric_cols,default=[])
        st.write(df[showData])

st.write("statistics")
most_wins_team = df['winner'].mode()[0]
most_wins_count = df['winner'].value_counts().max()
most_mom_player = df['player_of_match'].mode()[0]
most_mom_count = df['player_of_match'].value_counts().max()

total1,total2=st.columns(2,gap='large')
with total1:
    st.metric(label="### Team with the Most Wins:📌", value=f"{most_wins_team}", delta=f"{most_wins_count} wins")
with total2:
    st.metric(label="### Player with the Most Man of the Match Awards📌", value=f"{most_mom_player}", delta=f"{most_mom_count} awards")

################################################################################################################
st.write("## Number of Matches Won by Each Team")
wins = df.groupby(['year', 'winner']).size().reset_index(name='Wins')
fig = px.bar(wins, x='winner', y='Wins', color='winner', animation_frame='year', title='Number of Matches Won by Each Team')
st.plotly_chart(fig)

st.write("## Team Comparison")
team1 = st.selectbox('Select Team 1', df['team1'].unique())
team2 = st.selectbox('Select Team 2', df['team2'].unique())

if team1 and team2:
        team_comparison = df[((df['team1'] == team1) & (df['team2'] == team2)) | ((df['team1'] == team2) & (df['team2'] == team1))]
        wins_comparison = team_comparison['winner'].value_counts().reset_index()
        wins_comparison.columns = ['Team', 'Wins']
        fig = px.bar(wins_comparison, x='Team', y='Wins', title=f'Wins Comparison between {team1} and {team2}')
        st.plotly_chart(fig)

st.write("## team performance")
team = st.selectbox('Select Team', df['team1'].unique())

g1,g2=st.columns(2,gap="large")
with g1:
    chasing_wins = df[(df['winner'] == team) & (df['toss_decision'] == 'field')].groupby('year').size().reset_index(name='Wins')
    fig_chasing = px.line(chasing_wins, x='year', y='Wins', title=f'{team} Wins While Chasing', markers=True)
    st.plotly_chart(fig_chasing)
with g2:
    defending_wins = df[(df['winner'] == team) & (df['toss_decision'] == 'bat')].groupby('year').size().reset_index(name='Wins')
    fig_defending = px.line(defending_wins, x='year', y='Wins', title=f'{team} Wins While Defending', markers=True)
    st.plotly_chart(fig_defending)


st.write("## Number of Matches Played in Each City")
matches_per_city = df['city'].value_counts().reset_index()
matches_per_city.columns = ['City', 'Matches']
fig = px.pie(matches_per_city, names='City', values='Matches', title='Number of Matches Played in Each City')
st.plotly_chart(fig)