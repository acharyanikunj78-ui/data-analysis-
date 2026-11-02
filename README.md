# 🏎️ Formula 1 Race Intelligence – Tableau Project

An interactive Tableau analysis of Formula 1 race data: **6,464 race records across 17 seasons**, covering driver performance, constructor championship trajectories, tyre strategy, Grand Prix hosts, podium achievements, and reliability (DNF) patterns.

🔗 **Live Dashboard (Tableau Public):** <PASTE-TABLEAU-PUBLIC-LINK-HERE>
🎥 **Demo Video:** <PASTE-VIDEO-LINK-HERE>

![Dashboard preview](screenshots/dashboard.png)

---

## 📌 Problem Statement
Teams, broadcasters, and regulators all need quick, visual answers from race data. This project turns raw race records into dashboards and a story that serve three audiences.

## 👥 Scenarios
| # | Persona | Goal |
|---|---------|------|
| 1 | **F1 Team Performance Strategist** | Benchmark the team's points trajectory against Red Bull Racing and Mercedes, compare tyre strategies by circuit type, and find the strongest driver talent pools. |
| 2 | **Motorsport Broadcast Analyst** | Pull the driver leaderboard, Grand Prix host countries, and podium distributions for on-screen graphics. |
| 3 | **FIA Technical Regulation Analyst** | Study DNF causes by team and circuit type and check whether reliability has improved over the seasons. |

## 📊 Project Contents
**Worksheets**
- Team Championship Trajectory
- Tyre Strategy
- Talent Pools
- Driver Leaderboard
- GP Host Countries
- Podiums by Driver
- Podiums by Team
- Reliability Trend by Season
- Failure Type by Team and Circuit Type
- DNF by Driver and Race

**Dashboards:** one per persona (strategist, broadcast analyst, regulation analyst)
**Story:** intro, one scene per persona, and conclusion

**Calculated fields**
| Field | Logic |
|-------|-------|
| Podium | `IF [finish_position] <= 3 THEN 1 ELSE 0 END` |
| Win | `IF [finish_position] = 1 THEN 1 ELSE 0 END` |
| DNF Rate | `SUM([dnf]) / COUNT([driver])` |
| Reliability % | `(1 - SUM([dnf]) / COUNT([driver])) * 100` |
| Your Team | Groups teams into Red Bull, Mercedes, your team, and Others |
| Races | `COUNTD([race_id])` |

## 🗂️ Repository Structure
```
├── README.md
├── data/            # dataset (Excel/CSV)
├── workbook/        # F1_Race_Intelligence.twbx (packaged Tableau workbook)
├── screenshots/     # dashboard and story images
├── documentation/   # project documentation (PDF/Word)
└── .gitignore
```

## ▶️ How to Open
1. Install the free [Tableau Public Desktop](https://public.tableau.com/en-us/s/download).
2. Download `workbook/F1_Race_Intelligence.twbx`.
3. Open it in Tableau Public Desktop (the data is packaged inside).
Or view it online using the Tableau Public link above.

## 🛠️ Tools Used
- Tableau Public Desktop
- Microsoft Excel (data source)

## 📸 Screenshots
| Dashboard 1 | Dashboard 2 | Dashboard 3 |
|---|---|---|
| ![](screenshots/dashboard1.png) | ![](screenshots/dashboard2.png) | ![](screenshots/dashboard3.png) |

## 👤 Author
<YOUR-NAME> · <LINKEDIN-OR-EMAIL>

## 📄 License
Add a license (for example MIT) if you want others to reuse the work.
