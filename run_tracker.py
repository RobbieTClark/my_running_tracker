import pandas as pd
import requests
import urllib3
from datetime import date
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_ytd_run_dist(auth_url, athlete_url, payload):
    
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    header = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}
    my_dataset = requests.get(athlete_url, headers=header, params=param).json()

    id_ = my_dataset['id']
    stats_url = f"https://www.strava.com/api/v3/athletes/{id_}/stats"

    activity_stats = requests.get(stats_url, headers=header, params=param).json()

    ytd_run_totals = activity_stats['ytd_run_totals']
    ytd_run_dist = ytd_run_totals['distance']/1000

    return ytd_run_dist

def get_num_days_passed():
    
    year = date.today().year
    month = date.today().month
    day = date.today().day

    num_days_passed = date(year,month,day) - date(year,1,1)
    num_days_passed = num_days_passed.days + 1

    return num_days_passed


if __name__ == "__main__":
    
    user_info_file = 'my_info.csv'

    try: my_info = pd.read_csv(user_info_file)  # Get my user info for payload, this is a csv table containing column headers client_id, client_secret, and refresh token
    except OSError: 
        print(f'Could not open {user_info_file} required to access client_id, client_secret, and refresh token')
        exit()

    auth_url = "https://www.strava.com/oauth/token"
    athlete_url = "https://www.strava.com/api/v3/athlete"


    payload = {
    'client_id': my_info['client_id'][0],
    'client_secret': my_info['client_secret'][0],
    'refresh_token': my_info['refresh_token'][0],
    'grant_type': "refresh_token",
    'f': 'json'
    }

    ytd_run_dist = get_ytd_run_dist(auth_url, athlete_url, payload)
    num_days_passed = get_num_days_passed()

    year_goal = 1600 # 1600 km = 1000 miles
    avg_dist_required = round(year_goal/365,3) # Average distance per day to meet goal

    avg_dist_current = round(ytd_run_dist/num_days_passed,3)

    print('') # Making some space

    print(f'Your goal is {year_goal} km for the year')

    behind = False

    print('You are: ', end = '')
    if avg_dist_current == avg_dist_required:
        print('On track')
    elif avg_dist_current > avg_dist_required:
        print('Ahead')
    else:
        behind = True
        print('Behind')

    print(f'Current average distance per day: {avg_dist_current} km, resulting in {round(avg_dist_current*365)} km')
    print(f'Required average distance per day: {avg_dist_required} km')

    if behind:
        user_choice = input('Do you want to catch-up? y/n\n').upper()
        while user_choice != 'Y' and user_choice != 'N':
            user_choice = input('Unknown input, please input "y" for Yes of "n" for No\n').upper()
        if user_choice == 'Y':
            catchup_time = int(input('How many days do you need to catch-up?\n'))
            days_inc_catchup = num_days_passed + catchup_time
            required_catchup_dist = round(catchup_time*avg_dist_required + (avg_dist_required - avg_dist_current)*num_days_passed)
            print(f'To get back on track you need to run {required_catchup_dist} km in the next {catchup_time} days')
            print(f'That works out at {round(required_catchup_dist/catchup_time, 2)} km a day')
    

