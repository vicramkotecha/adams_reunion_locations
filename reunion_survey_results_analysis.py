import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    # Load the survey results from a CSV file
    survey_data = pd.read_excel(r"C:\Users\micro\Downloads\Adams Family Reunion 2028_ Questionnaire (Responses) after reopen 2.xlsx")

    # Display the first few rows of the survey data
    print(survey_data.head())
    print(survey_data.columns)
    """
    Index(['Timestamp', 'Your name (optional) ', 'Home Airport Code (optional) ',
       'How many people in the clan are you representing with this response, including children and yourself? Include names if desired.',
       'What's most important to you? 1=Don't Care; 5=Most Important [Common Room]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Walkable Resort]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Stage]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Exclusively Ours]',
       'What's most important to you? 1=Don't Care; 5=Most Important [AV Setup]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Banquet Area]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Kitchens in Units]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Catered Meals]',
       'What's most important to you? 1=Don't Care; 5=Most Important [BBQ Facilities]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Picnic Area]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Campfire Pits]',
       'What's most important to you? 1=Don't Care; 5=Most Important [A/C]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Disabled Access]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Limited Hills]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Lower Elevation]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Quiet Hours]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Low Rain Averages]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Low Tick Risk]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Low Mosquitos/Bugs]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Low Heat/Humidity]',
       'What's most important to you? 1=Don't Care; 5=Most Important [RV Parking]',
       'What's most important to you? 1=Don't Care; 5=Most Important [EV Charging]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Reliable Wifi]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Cell Coverage]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Direct Flight]',
       'What's most important to you? 1=Don't Care; 5=Most Important [1 Plane Transfer]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Driveable from Home]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Town: walkable]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Town: <15min]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Mini mart]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Swimming Pool]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Beach]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Lake]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Boating]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Playground]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Game Room]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Tennis]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Spa]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Theme Parks]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Museums]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Horse Riding]',
       'What's most important to you? 1=Don't Care; 5=Most Important [City Attractions]',
       'What's most important to you? 1=Don't Care; 5=Most Important [National Parks]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Golf]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Hiking]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Shopping]',
       'Cabins or Hotel?', 'How much does cabins/hotel matter?',
       'Secluded vs Attractions Availability',
       'How much does secluded vs attractions matter?',
       'Setting (call 3 suburban)',
       'How much does rural/suburban/city matter?',
       'What regions would you prefer? [HI]',
       'What regions would you prefer? [AK]',
       'What regions would you prefer? [West Coast]',
       'What regions would you prefer? [Rockies]',
       'What regions would you prefer? [TX]',
       'What regions would you prefer? [Great Plains]',
       'What regions would you prefer? [Southwest]',
       'What regions would you prefer? [Southeast]',
       'What regions would you prefer? [Midwest]',
       'What regions would you prefer? [Northeast]', 'Deal-Breakers',
       'Volunteers requested!',
       'Volunteering details: What states/regions would you cover?',
       'Email address and/or phone if you're volunteering',
       'Nominations: any places you'd recommend?',
       'Further comments, concerns or questions?',
       'Ideal lodging budget/day per bedroom',
       'Maximum lodging budget/day per bedroom',
       'Preference for unit capacity?', 'Column 75',
       'What's most important to you? 1=Don't Care; 5=Most Important [Pet friendly]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Laundry facilities]',
       'Any activities you'd really like on site?',
       'What's most important to you? 1=Don't Care; 5=Most Important [Near Grocery Store]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Near Restaurants]',
       'What's most important to you? 1=Don't Care; 5=Most Important [Row 47]'],
      dtype='str')
    """
    # Analyze the importance ratings for each feature
    importance_columns = [col for col in survey_data.columns if "What's most important to you?" in col]
    importance_data = survey_data[importance_columns]
    # rename columns to just the feature name
    importance_data.rename(columns=lambda x: x.split('[')[-1].rstrip(']') if "What's most important to you?" in x else x, inplace=True)
    # remove "Row 47" column if it exists
    if 'Row 47' in importance_data.columns:
        importance_data.drop(columns=['Row 47'], inplace=True)

    # Calculate the average importance rating for each feature
    average_importance = importance_data.mean()
    # Plot the average importance ratings
    plt.figure(figsize=(12, 8))
    average_importance.sort_values(ascending=True).plot(kind='barh')
    plt.title('Average Importance Ratings for Reunion Features')
    plt.xlabel('Average Rating (1-5)')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig('average_importance_ratings.png')
    plt.close()
    # write the base data to csv
    average_importance.to_csv('average_importance_ratings.csv')

    # scale by total of response's preferences to get a sense of distribution
    importance_data_scaled = importance_data.div(importance_data.sum(axis=1), axis=0)
    average_importance_scaled = importance_data_scaled.mean()
    plt.figure(figsize=(12, 8))
    average_importance_scaled.sort_values(ascending=True).plot(kind='barh')
    plt.title('Average Importance Ratings for Reunion Features (Scaled)')
    plt.xlabel('Average Scaled Rating')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig('average_importance_ratings_scaled.png')
    plt.close()
    # write the base data to csv
    average_importance_scaled.to_csv('average_importance_ratings_scaled.csv')


    # mulitply scaled importance data by number of people represented to get a sense of total importance across the clan
    importance_data_weighted = importance_data_scaled.mul(survey_data['How many people in the clan are you representing with this response, including children and yourself? Include names if desired.'], axis=0)
    average_importance_weighted = importance_data_weighted.mean()
    plt.figure(figsize=(12, 8))
    average_importance_weighted.sort_values(ascending=True).plot(kind='barh')
    plt.title('Average Importance Ratings for Reunion Features (Weighted by Number of People Represented)')
    plt.xlabel('Average Weighted Rating')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig('average_importance_ratings_weighted.png')
    plt.close()
    # write the base data to csv
    average_importance_weighted.to_csv('average_importance_ratings_weighted.csv')

    # Analyze the preferred regions
    region_columns = [col for col in survey_data.columns if "What regions would you prefer?" in col]
    region_data = survey_data[region_columns]
    # these are strings - find values
    region_preferences = region_data.apply(pd.Series.value_counts).fillna(0)
    # Plot the region preferences
    plt.figure(figsize=(12, 8))
    region_preferences.T.plot(kind='bar', stacked=True)
    plt.title('Preferred Regions for Reunion')
    plt.xlabel('Regions')
    plt.ylabel('Number of Responses')
    plt.legend(title='Preference', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig('preferred_regions.png')
    plt.close()
    # print distinct values
    distinct_values = region_data.apply(lambda x: x.unique())
    print(distinct_values)
    """
    What regions would you prefer? [HI]              [Neutral, Rather not, Love it, Like it, nan, I...
What regions would you prefer? [AK]              [Love it, Neutral, Like it, Rather not, I won'...
What regions would you prefer? [West Coast]                       [Like it, Neutral, Love it, nan]
What regions would you prefer? [Rockies]                          [Love it, Like it, nan, Neutral]
What regions would you prefer? [TX]              [Rather not, Like it, Neutral, I won't go here...
What regions would you prefer? [Great Plains]         [Rather not, Neutral, Like it, nan, Love it]
What regions would you prefer? [Southwest]            [Neutral, Like it, nan, Love it, Rather not]
What regions would you prefer? [Southeast]       [Neutral, Rather not, Like it, I won't go here...
What regions would you prefer? [Midwest]              [Rather not, Neutral, Like it, Love it, nan]
What regions would you prefer? [Northeast]            [Rather not, Like it, Love it, Neutral, nan]
"""
    region_preferences_values = {
        'Rather not': 1,
        'Neutral': 2,
        'Like it': 3,
        'Love it': 4,
        "I won't go here": 0
    }
    region_preferences_numeric = region_data.replace(region_preferences_values)
    region_preferences_numeric = region_preferences_numeric.apply(pd.to_numeric, errors='coerce')
    average_region_preferences = region_preferences_numeric.mean()
    plt.figure(figsize=(12, 8))
    average_region_preferences.sort_values(ascending=True).plot(kind='barh')
    plt.title('Average Region Preferences for Reunion')
    plt.xlabel('Average Preference (0-4)')
    plt.ylabel('Regions')
    plt.tight_layout()
    plt.savefig('average_region_preferences.png')
    plt.close()
    # write the base data to csv
    average_region_preferences.to_csv('average_region_preferences.csv')


    i_wont_go_here_counts = region_data.apply(lambda x: (x == "I won't go here").sum())
    plt.figure(figsize=(12, 8))
    i_wont_go_here_counts.sort_values(ascending=True).plot(kind='barh')
    plt.title("Number of 'I won't go here' Responses by Region")
    plt.xlabel("Number of 'I won't go here' Responses")
    plt.ylabel('Regions')
    plt.tight_layout()
    plt.savefig("i_wont_go_here_counts.png")
    plt.close()
    # write the base data to csv
    i_wont_go_here_counts.to_csv('i_wont_go_here_counts.csv')


    rather_not_counts = region_data.apply(lambda x: (x == "Rather not").sum())
    plt.figure(figsize=(12, 8))
    rather_not_counts.sort_values(ascending=True).plot(kind='barh')
    plt.title("Number of 'Rather not' Responses by Region")
    plt.xlabel("Number of 'Rather not' Responses")
    plt.ylabel('Regions')
    plt.tight_layout()
    plt.savefig("rather_not_counts.png")
    plt.close()
    # write the base data to csv
    rather_not_counts.to_csv('rather_not_counts.csv')

    # budgets
    plt.figure(figsize=(12, 8))
    survey_data['Ideal lodging budget/day per bedroom'] = pd.to_numeric(survey_data['Ideal lodging budget/day per bedroom'], errors='coerce')
    survey_data['Maximum lodging budget/day per bedroom'] = pd.to_numeric(survey_data['Maximum lodging budget/day per bedroom'], errors='coerce')
    survey_data['Ideal lodging budget/day per bedroom'].plot(kind='hist', bins=20, alpha=0.5, label='Ideal Budget')
    survey_data['Maximum lodging budget/day per bedroom'].plot(kind='hist', bins=20, alpha=0.5, label='Maximum Budget')
    plt.title('Distribution of Lodging Budgets per Bedroom')
    plt.xlabel('Budget ($/day/bedroom)')
    plt.ylabel('Number of Responses')
    plt.legend()
    plt.tight_layout()
    plt.savefig('lodging_budget_distribution.png')
    plt.close()
    # write the base data to csv
    survey_data[['Ideal lodging budget/day per bedroom', 'Maximum lodging budget/day per bedroom']].to_csv('lodging_budgets.csv', index=False)
    # summarize means, mins, maxes, etc into a table
    budget_summary = survey_data[['Ideal lodging budget/day per bedroom', 'Maximum lodging budget/day per bedroom']].describe()
    budget_summary.to_csv('lodging_budget_summary.csv')


    average_max_budget = survey_data['Maximum lodging budget/day per bedroom'].mean()
    average_ideal_budget = survey_data['Ideal lodging budget/day per bedroom'].mean()
    min_max_budget = survey_data['Maximum lodging budget/day per bedroom'].min()
    max_max_budget = survey_data['Maximum lodging budget/day per bedroom'].max()
    print(f"Average Ideal Lodging Budget per Bedroom: ${average_ideal_budget:.2f}")
    print(f"Average Maximum Lodging Budget per Bedroom: ${average_max_budget:.2f}")
    print(f"Minimum Maximum Lodging Budget per Bedroom: ${min_max_budget:.2f}")
    print(f"Maximum Maximum Lodging Budget per Bedroom: ${max_max_budget:.2f}")

    # States and areas suggested
    nominations = """Canada
Big city
NC
AK
ME
TN
CO
AR
TX
PA
MT
OR
MI
MN
KY
OH
CA
FL
ID
WI
""".splitlines()
    
    investigation_states = """IL
IA
WI
MN
PA
NY
OH
KY
CA
KS
MO
MD
PA
WF
NC
DE
MO
AR
TN
IA
IL
IN
KY
WI
MN
PA
KS
OR
CA
OR
WA
CA""".splitlines()
    
    coordinator_available_states = """OR
WA
ID
NJ
PA
MN
WI
TX
CO
OK
LA
OH
KY
IN
ME
NH
CT
MA
VT
RI""".splitlines()
    nominations = [state.strip() for state in nominations if state.strip()]
    investigation_states = [state.strip() for state in investigation_states if state.strip()]
    coordinator_available_states = [state.strip() for state in coordinator_available_states if state.strip()]
    nominations_with_coordinator = set(nominations) & set(coordinator_available_states)
    nominations = list(sorted(set(nominations)))
    investigation_states = list(sorted(set(investigation_states)))
    coordinator_available_states = list(sorted(set(coordinator_available_states)))
    nominations_with_coordinator = list(sorted(nominations_with_coordinator))
    print(f"States/areas nominated: {nominations}")
    print(f"States/areas with volunteers available: {coordinator_available_states}")
    print(f"States/areas nominated with volunteers available: {nominations_with_coordinator}")

    # write the base data to csv. States on the rows, columns for nominated, coordinator available, both
    states_df = pd.DataFrame({
        'State/Area': sorted(set(nominations + investigation_states + coordinator_available_states)),
        'Nominated': [state in nominations for state in sorted(set(nominations + investigation_states + coordinator_available_states))],
        'Investigation Interest': [state in investigation_states for state in sorted(set(nominations + investigation_states + coordinator_available_states))],
        'Coordinator Available': [state in coordinator_available_states for state in sorted(set(nominations + investigation_states + coordinator_available_states))],
    })
    states_df.to_csv('states_summary.csv', index=False)