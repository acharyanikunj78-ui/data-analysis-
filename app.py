"""
Formula 1 Race Intelligence - Streamlit app
Python version of the Tableau dashboards (3 persona tabs).

Run:
    pip install streamlit pandas plotly openpyxl
    streamlit run app.py

Expected files (change the paths below if yours differ):
    data/race_results.xlsx         one row per driver per race
    data/driver_nationality.xlsx   optional: driver, nationality
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

RESULTS_FILE = Path("data/race_results.xlsx")
NATIONALITY_FILE = Path("data/driver_nationality.xlsx")

# Columns used in the Tableau workbook
REQUIRED = ["season", "race_id", "driver", "team", "finish_position", "points", "dnf"]

st.set_page_config(page_title="F1 Race Intelligence", page_icon="🏎️", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(RESULTS_FILE)
    df.columns = [c.strip() for c in df.columns]
    if "nationality" not in df.columns and NATIONALITY_FILE.exists():
        nat = pd.read_excel(NATIONALITY_FILE)
        nat.columns = [c.strip() for c in nat.columns]
        df = df.merge(nat, on="driver", how="left")
    # Same calculated fields as the Tableau workbook
    df["podium"] = (df["finish_position"] <= 3).astype(int)
    df["win"] = (df["finish_position"] == 1).astype(int)
    df["dnf"] = df["dnf"].astype(int)
    return df


def has(df: pd.DataFrame, *cols: str) -> bool:
    return all(c in df.columns for c in cols)


def reliability(df: pd.DataFrame) -> float:
    return (1 - df["dnf"].sum() / max(len(df), 1)) * 100


# ---------------------------------------------------------------- load
if not RESULTS_FILE.exists():
    st.error(f"Data file not found: {RESULTS_FILE}. Put race_results.xlsx in the data folder.")
    st.stop()

data = load_data()
missing = [c for c in REQUIRED if c not in data.columns]
if missing:
    st.error(f"Missing columns in the data: {missing}")
    st.stop()

# ---------------------------------------------------------------- sidebar
st.sidebar.header("Filters")
seasons = sorted(data["season"].unique())
season_range = st.sidebar.select_slider(
    "Season range", options=seasons, value=(seasons[0], seasons[-1])
)
teams = sorted(data["team"].dropna().unique())
selected_teams = st.sidebar.multiselect("Teams", teams, default=[])
your_team = st.sidebar.selectbox("Your team (benchmark)", teams)

df = data[data["season"].between(*season_range)]
if selected_teams:
    df = df[df["team"].isin(selected_teams)]

# ---------------------------------------------------------------- header
st.title("🏎️ Formula 1 Race Intelligence")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Race records", f"{len(df):,}")
c2.metric("Races", f"{df['race_id'].nunique():,}")
c3.metric("Podiums", f"{int(df['podium'].sum()):,}")
c4.metric("Reliability", f"{reliability(df):.1f}%")

tab1, tab2, tab3, tab4 = st.tabs(
    ["Team Strategist", "Broadcast Analyst", "Regulation Analyst", "Data"]
)

# ---------------------------------------------------------------- tab 1
with tab1:
    st.subheader("Team Championship Trajectory")
    focus = ["Red Bull Racing", "Mercedes", your_team]
    traj = (
        data[data["season"].between(*season_range) & data["team"].isin(focus)]
        .groupby(["season", "team"], as_index=False)["points"].sum()
    )
    fig = px.line(traj, x="season", y="points", color="team", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Season-by-season points for Red Bull Racing, Mercedes, and your selected team.")

    left, right = st.columns(2)
    with left:
        st.subheader("Tyre Strategy")
        if has(df, "starting_compound", "circuit_type"):
            tyre_df = df
            if "is_wet_race" in df.columns:
                wet = st.radio("Race condition", ["All", "Dry", "Wet"], horizontal=True)
                if wet != "All":
                    tyre_df = df[df["is_wet_race"].astype(int) == (1 if wet == "Wet" else 0)]
            tyre = tyre_df.groupby(["circuit_type", "starting_compound"], as_index=False)["points"].mean()
            fig = px.density_heatmap(
                tyre, x="circuit_type", y="starting_compound", z="points",
                histfunc="avg", color_continuous_scale="Reds",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Average points by starting compound and circuit type.")
        else:
            st.info("starting_compound / circuit_type columns not found.")
    with right:
        st.subheader("Talent Pools")
        if "nationality" in df.columns:
            tal = (
                df.groupby("nationality", as_index=False)
                .agg(points=("points", "sum"), podiums=("podium", "sum"))
                .sort_values("points", ascending=False).head(15)
            )
            fig = px.bar(tal, x="points", y="nationality", color="podiums", orientation="h")
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Points and podiums by driver nationality (top 15).")
        else:
            st.info("nationality column not found.")

# ---------------------------------------------------------------- tab 2
with tab2:
    top_n = st.slider("Number of drivers", 5, 30, 15)
    left, right = st.columns(2)
    with left:
        st.subheader("Driver Leaderboard")
        lead = df.groupby("driver", as_index=False)["points"].sum().nlargest(top_n, "points")
        fig = px.bar(lead, x="points", y="driver", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Cumulative points per driver for the selected seasons.")
    with right:
        st.subheader("Podiums by Driver")
        pod = df.groupby("driver", as_index=False)["podium"].sum().nlargest(top_n, "podium")
        fig = px.bar(pod, x="podium", y="driver", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Top-three finishes per driver.")

    left, right = st.columns(2)
    with left:
        st.subheader("Podiums by Team")
        team_pod = df.groupby("team", as_index=False)["podium"].sum().sort_values("podium", ascending=False)
        fig = px.bar(team_pod, x="team", y="podium")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Top-three finishes per constructor.")
    with right:
        st.subheader("GP Host Countries")
        if "country" in df.columns:
            host = df.groupby("country", as_index=False)["race_id"].nunique()
            host.columns = ["country", "races"]
            fig = px.choropleth(host, locations="country", locationmode="country names",
                                color="races", color_continuous_scale="Blues")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Countries that hosted Grand Prix rounds (darker = more races).")
        else:
            st.info("Add a country column (or merge the circuits table) to show the map.")

# ---------------------------------------------------------------- tab 3
with tab3:
    st.subheader("Reliability Trend by Season")
    rel = (
        df.groupby("season")
        .apply(reliability, include_groups=False)
        .reset_index(name="reliability_pct")
    )
    fig = px.line(rel, x="season", y="reliability_pct", markers=True)
    fig.update_yaxes(title="Reliability %")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Share of entries that finished the race, by season.")

    if "dnf_reason" in df.columns:
        dnf = df[df["dnf"] == 1]
        reasons = sorted(dnf["dnf_reason"].dropna().unique())
        chosen = st.multiselect("DNF reason", reasons, default=reasons)
        dnf = dnf[dnf["dnf_reason"].isin(chosen)]

        left, right = st.columns(2)
        with left:
            st.subheader("Failure Type by Team")
            by_team = dnf.groupby(["team", "dnf_reason"], as_index=False).size()
            fig = px.bar(by_team, x="team", y="size", color="dnf_reason")
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Retirements by team, split by cause.")
        with right:
            if "circuit_type" in dnf.columns:
                st.subheader("Failure Type by Circuit Type")
                by_circuit = dnf.groupby(["circuit_type", "dnf_reason"], as_index=False).size()
                fig = px.bar(by_circuit, x="circuit_type", y="size", color="dnf_reason")
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Retirements by circuit type, split by cause.")

        st.subheader("DNF by Driver")
        by_driver = dnf.groupby("driver", as_index=False).size().nlargest(15, "size")
        fig = px.bar(by_driver, x="size", y="driver", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Drivers with the most retirements.")
    else:
        st.info("dnf_reason column not found.")

# ---------------------------------------------------------------- tab 4
with tab4:
    st.subheader("Filtered data")
    st.dataframe(df, use_container_width=True)
    st.download_button("Download CSV", df.to_csv(index=False), "f1_filtered.csv", "text/csv")
