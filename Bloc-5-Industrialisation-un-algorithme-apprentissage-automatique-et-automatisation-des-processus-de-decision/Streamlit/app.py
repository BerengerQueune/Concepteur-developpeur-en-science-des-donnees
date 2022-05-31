import streamlit as st

import pandas as pd
pd.options.mode.chained_assignment = None
import numpy as np

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


### Config
st.set_page_config(
    page_title="GetAround",
    page_icon=":red_car:",
    layout="wide"
)

# Importing Dataset
@st.cache
def load_data_pricing():
  data_pricing =  pd.read_csv("get_around_pricing_project.csv")
  return data_pricing

@st.cache
def load_data_delay():
  data_delay = pd.read_excel("get_around_delay_analysis.xlsx")
  return data_delay


data_pricing = load_data_pricing()
data_delay = load_data_delay()


# Findind number of unique cars
number_of_cars = len(data_delay['car_id'].unique())

# Finding average rental price
car_average_rental_price_per_day = round(data_pricing["rental_price_per_day"].mean())

# Finding number of rentals
number_of_rentals = data_delay.shape[0]

# Removing NaN values about late checkout from the dataset
data_delay_without_nan = data_delay[data_delay["delay_at_checkout_in_minutes"].isna() == False]

print (f"There are {data_delay_without_nan.shape[0]} rentals in the dataset 'data_delay_without_nan'")

def check_if_late(late):
    if late > 0:
        return "late"
    else:
        return "not late"

# Creating a new column to categorize lateness
data_delay_without_nan["delay"] = data_delay_without_nan["delay_at_checkout_in_minutes"].apply(check_if_late)

# Creating a new DataFrame with values counts for the lateness category
new_df = (data_delay_without_nan['delay'].value_counts(normalize=True)*100).rename_axis('delay').reset_index(name='counts')

# Creating a new DataFrame with values counts for the state category
df_rental_state = (data_delay['state'].value_counts(normalize=True)*100).rename_axis('state').reset_index(name='counts')

# Making a list of all the previous_ended_rental_id
lst_previous_rental_id = data_delay["previous_ended_rental_id"]

# Removing all NaN values from this list
lst_previous_rental_id = [x for x in lst_previous_rental_id if np.isnan(x) == False]

# Creating a new df with all the rental id found in my previous list to see if they were late or not
df_previous_rental_id = data_delay[data_delay["rental_id"].isin(lst_previous_rental_id)]

# Merging the two df to have a the same row both the previous rental id and the following rental id
df_merged = df_previous_rental_id.merge(data_delay, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')

# Removing useless columns
df_merged.drop(['state_x', 'previous_ended_rental_id_y','previous_ended_rental_id_x', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)
print (f"After cleaning the dataset, there are {df_merged.shape[0]} rows left to use from {len(data_delay)} rows originally.")

# Creating a new DataFrame when checkout was late
df_merged_and_late = df_merged[df_merged["delay_at_checkout_in_minutes_x"] > 0]

# Creating a new DataFrame when checkout was done on time
df_merged_and_not_late = df_merged[df_merged["delay_at_checkout_in_minutes_x"] <= 0]

# Creating a new DataFrame with values counts of state for late checkout
df_merged_and_late_value_counts = (df_merged_and_late['state_y'].value_counts(normalize=True)*100).rename_axis('state_y').reset_index(name='counts')

# Creating a new DataFrame with values counts of state for checkout on time
df_merged_and_not_late_value_counts = (df_merged_and_not_late['state_y'].value_counts(normalize=True)*100).rename_axis('state_y').reset_index(name='counts')

# Creating a new column to find if the checkout of the previous rental happened after the start of the following rental
df_merged_and_late["wait_time_in_minutes"] = df_merged_and_late["delay_at_checkout_in_minutes_x"] - df_merged_and_late["time_delta_with_previous_rental_in_minutes_y"]

# Keeping only cases when the checkout of the previous rental happened after the start of the following rental
df_merged_way_too_late = df_merged_and_late[df_merged_and_late["wait_time_in_minutes"] > 0]

# Creating a new DataFrame with values counts of state when the checkout of the previous rental happened after the start of the following rental
df_merged_way_too_late2 = (df_merged_way_too_late['state_y'].value_counts(normalize=True)*100).rename_axis('state_y').reset_index(name='counts')

# Checking if there is a difference in cancelation rate between mobile and connect checking type
df_merged_and_late_mobile = df_merged_and_late[df_merged_and_late["checkin_type_x"] == "mobile"]
df_merged_and_late_connect = df_merged_and_late[df_merged_and_late["checkin_type_x"] == "connect"]


def main():

    pages = {
        'Project': project,
        'GetAround Analysis': analysis,
        'Try your own variables': variables,
        }

    if "page" not in st.session_state:
        st.session_state.update({
        # Default page
        'page': 'Project'
        })

    with st.sidebar:
        page = st.selectbox("Make your choice", tuple(pages.keys()))

    pages[page]()
    
def project():
    
    st.markdown("<h1 style='text-align: center;'>GetAround project</h1>", unsafe_allow_html=True)
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    
    "For this case study, we suggest that you put yourselves in our shoes, and run an analysis we made back in 2017 🔮."
    
    "When using Getaround, drivers book cars for a specific time period, from an hour to a few days long. They are supposed to bring back the car on time, but it happens from time to time that drivers are late for the checkout."
    
    "Late returns at checkout can generate high friction for the next driver if the car was supposed to be rented again on the same day : Customer service often reports users unsatisfied because they had to wait for the car to come back from the previous rental or users that even had to cancel their rental because the car wasn’t returned on time."
    
    "In order to mitigate those issues we’ve decided to implement a minimum delay between two rentals. A car won’t be displayed in the search results if the requested checkin or checkout times are too close from an already booked rental."
    
    "It solves the late checkout issue but also potentially hurts Getaround/owners revenues: we need to find the right trade off."

    "* threshold: how long should the minimum delay be?"
    "* scope: should we enable the feature for all cars? only Connect cars?"

    "In order to help them make the right decision, they are asking you for some data insights. Here are the first analyses they could think of, to kickstart the discussion. Don’t hesitate to perform additional analysis that you find relevant."

    "* Which share of our owner’s revenue would potentially be affected by the feature How many rentals would be affected by the feature depending on the threshold and scope we choose?"
    "* How often are drivers late for the next check-in? How does it impact the next driver?"
    "* How many problematic cases will it solve depending on the chosen threshold and scope?"

    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    
    'Made by Bérenger Queune.'

def analysis():


    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START
    ################################################################ EXPLORATION AND VISUALISATION START

    st.markdown("<h1 style='text-align: center;'>Data exploration and visualisation</h1>", unsafe_allow_html=True)
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    
    st.write (f"There are {number_of_cars} different cars in the dataset.")
    st.write (f"The average rental price of a car per day is {car_average_rental_price_per_day}$.")
    st.write (f"There are {number_of_rentals} rentals in the dataset.")

    # Bar chart - lateness on whole dataset after removal of NaN
    fig = px.bar(new_df, 
                x="delay", 
                y="counts", 
                color="delay", 
                title="----------", 
                color_discrete_sequence=['royalblue', '#880808'],
                text="counts",
                width=1000, height=500,)
    fig.update_traces(texttemplate='%{text:.2f}' + "%", textposition='outside')
    fig.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Proportion of lateness - Whole Dataset after removal of NaN", template='plotly_dark', xaxis_title='', showlegend=False)
    st.plotly_chart(fig)

    # Bar chart - state on Whole dataset
    fig = px.bar(df_rental_state, 
                x="state", 
                y="counts", 
                color="state", 
                title="----------", 
                color_discrete_sequence=['#03c04A', '#80471C'],
                text="counts",
                width=1000, height=500,)
    fig.update_traces(texttemplate='%{text:.2f}' + "%", textposition='outside')
    fig.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Proportion of rentals per state - Whole Dataset", template='plotly_dark', xaxis_title='', showlegend=False)
    st.plotly_chart(fig)

    st.write("Now I clean my dataset to keep only rows where I can find what the previous rental ID was to determine if the previous checkout was late or not.")

    # Bar chart - state for late checkout
    fig = px.bar(df_merged_and_late_value_counts, 
                x="state_y", 
                y="counts", 
                color="state_y", 
                title="----------", 
                color_discrete_sequence=['#03c04A', '#80471C'],
                text="counts",
                width=1000, height=500,)
    fig.update_traces(texttemplate='%{text:.2f}' + "%", textposition='outside')
    fig.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Cancelation rate after late checkout", template='plotly_dark', xaxis_title='', showlegend=False)
    st.plotly_chart(fig)

    # Bar chart - state for checkout on time
    fig2 = px.bar(df_merged_and_not_late_value_counts, 
                x="state_y", 
                y="counts", 
                color="state_y", 
                title="----------", 
                color_discrete_sequence=['#03c04A', '#80471C'],
                text="counts",
                width=1000, height=500,)
    fig2.update_traces(texttemplate='%{text:.2f}' + "%", textposition='outside')
    fig2.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Cancelation rate if checkout was not late", template='plotly_dark', xaxis_title='', showlegend=False)
    st.plotly_chart(fig2)

    st.write (f"{df_merged_way_too_late['state_y'].value_counts()[0]} ended rentals left when the checkout happened after the start of the following rental")
    st.write (f"{df_merged_way_too_late['state_y'].value_counts()[1]} canceled rentals left when the checkout happened after the start of the following rental")

    # Bar chart
    fig = px.bar(df_merged_way_too_late2, 
                x="state_y", 
                y="counts", 
                color="state_y", 
                title="----------", 
                color_discrete_sequence=['#03c04A', '#80471C'],
                text="counts",
                width=1000, height=500,)
                
    fig.update_traces(texttemplate='%{text:.2f}' + "%", textposition='outside')
    fig.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Proportion of state when checkout happened after the expected start of the following rental", template='plotly_dark', xaxis_title='', showlegend=False)
    st.plotly_chart(fig)

    st.write (f"Connect checkin has a {round((df_merged_and_late_connect['state_y'].value_counts(normalize=True)*100)[1],2)}% cancelation rate")
    st.write (f"Mobile checkin has a {round((df_merged_and_late_mobile['state_y'].value_counts(normalize=True)*100)[1],2)}% cancelation rate")

    st.markdown("<h2 style='text-align: center;'>Conclusion from visualisations and data exploration</h2>", unsafe_allow_html=True)

    st.write('\n')
    st.write('\n')
    st.write('\n')

    """
    * 21310 rentals
    * 57,53% have a late checkout after removing NaN from this column (16346 rentals left)
    * 1841 rentals left usable after merging lateness on previous rental with its following rental
    * 12,14% cancelation if previous checkout was late
    * 11,68% cancelation if previous checkout was not late
    * 16,97% cancelation if previous checkout was so late it happened after the start of the next rental
    * In case of lateness, we have 18.73% cancelation rate for Connect checkin versus 8.71% cancelation rate for Mobile checkin
    """

    "Lateness have an impact on the cancelation rate but it is lower that what I would have expected before checking the value. It's safe to assume this is not the main cause for cancelation. Given the amount of missing values, I am going to use proportion to find how much rentals would have avoided cancelation and how much rentals would not have been taken if we had set a minimum delta time between rentals. I am also going to check specifically the difference it would make if the feature was applied only on Connect checkin type."

    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END
    ################################################################ EXPLORATION AND VISUALISATION END

def variables():
    st.markdown("<h1 style='text-align: center;'>Try your own variables</h1>", unsafe_allow_html=True)

    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    st.write('\n')
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START
    ################################################################ TEST YOUR OWN VARIABLES START

    ################################################################ USER INPUT
    data_pricing = load_data_pricing()
    data_delay = load_data_delay()

    checkin_type = st.radio(
     "Chose a Check-in Type",
     ('connect', 'mobile', 'both'))

    new_delta = st.slider('Chose a minimum delta time', 0, 500, 30)

    ################################################################ DATA MANIPULATION

    # Finding average rental price
    car_average_rental_price_per_day = round(data_pricing["rental_price_per_day"].mean())

    # Making a list of all the previous_ended_rental_id
    lst_previous_rental_id = data_delay["previous_ended_rental_id"]

    # Removing all NaN values from this list
    lst_previous_rental_id = [x for x in lst_previous_rental_id if np.isnan(x) == False]

    # Creating a new df with all the rental id found in my previous list to see if they were late or not
    df_previous_rental_id = data_delay[data_delay["rental_id"].isin(lst_previous_rental_id)]

    # Merging the two df to have a the same row both the previous rental id and the following rental id
    df_merged = df_previous_rental_id.merge(data_delay, how='inner', left_on='rental_id', right_on='previous_ended_rental_id')

    # Removing useless columns
    df_merged.drop(['state_x', 'previous_ended_rental_id_y','previous_ended_rental_id_x', 'time_delta_with_previous_rental_in_minutes_x', 'car_id_y', 'delay_at_checkout_in_minutes_y'], axis=1, inplace=True)

    # Creating a new DataFrame when checkout was late
    df_merged_and_late = df_merged[df_merged["delay_at_checkout_in_minutes_x"] > 0]

    # Creating a new column to find if the checkout of the previous rental happened after the start of the following rental
    df_merged_and_late["wait_time_in_minutes"] = df_merged_and_late["delay_at_checkout_in_minutes_x"] - df_merged_and_late["time_delta_with_previous_rental_in_minutes_y"]

    # Creating a new DataFrame with only ended state
    df_true_good_cases = data_delay[data_delay["state"] == "ended"]

    # Creating a new DataFrame with all the cases having the data I need
    df_good_cases = df_merged.copy()
    df_good_cases = df_good_cases[df_good_cases["state_y"] == "ended"]

    # If checkin_type is not both, I filter the two previous DataFrames
    if checkin_type != 'both':
        df_good_cases = df_good_cases[df_good_cases["checkin_type_x"] == checkin_type]
        df_true_good_cases = df_true_good_cases[df_true_good_cases["checkin_type"] == checkin_type]

    # I keep only the rows where the time delta is higher or equal than the new time delta
    df_new_time_delta_good_cases = df_good_cases[df_good_cases["time_delta_with_previous_rental_in_minutes_y"] >= new_delta]

    # Creating a money lost variable
    money_lost = round(round((len(df_good_cases) - len(df_new_time_delta_good_cases))/len(df_good_cases)*100, 2) * len(df_true_good_cases) / 100) * car_average_rental_price_per_day

    # Creating a new DataFrame with only canceled state
    df_canceled_cases = df_merged[df_merged["state_y"] == "canceled"]

    # If checkin_type is not both, I filter my previous DataFrames
    if checkin_type != "both":
        df_canceled_cases = df_canceled_cases[df_canceled_cases["checkin_type_x"] == checkin_type]
        df_merged = df_merged[df_merged["checkin_type_x"] == checkin_type]
        data_delay = data_delay[data_delay["checkin_type"] == checkin_type]

    # Finding amount of rows having all the data I need
    row_all_data = len(df_merged)

    # Creating a new DataFrame with canceled and late cases
    df_canceled_and_late_cases = df_canceled_cases[df_canceled_cases["delay_at_checkout_in_minutes_x"] > 0]

    # Creating a new delay column to find out if the next rental owner had to wait or not
    df_canceled_and_late_cases["delay"] = df_canceled_and_late_cases["delay_at_checkout_in_minutes_x"] - df_canceled_and_late_cases["time_delta_with_previous_rental_in_minutes_y"]

    # I keep only cases where the next owner had to wait
    df_canceled_and_late_cases = df_canceled_and_late_cases[df_canceled_and_late_cases["delay"] > 0]

    # I find the percentage of cases where the next owner had to wait
    rate_too_late_canceled_case = len(df_canceled_and_late_cases) * 100 / row_all_data

    # Creating a new DataFrame with cases where the next owner had to wait
    df_new_time_delta_bad_cases = df_canceled_and_late_cases[df_canceled_and_late_cases["delay"] > new_delta]

    # Finding number of cancelation prevented
    cancelation_prevented = len(df_canceled_and_late_cases) - len(df_new_time_delta_bad_cases)
    
    # Finding percentage of cancelation prevented
    rate_cancelation_prevented = (cancelation_prevented) * 100 / len(df_canceled_and_late_cases)

    cancelation_prevented = len(df_canceled_and_late_cases) - len(df_new_time_delta_bad_cases)

    total_estimated_cancelation_prevented = len(data_delay) * (rate_too_late_canceled_case/100)
    money_saved = round(total_estimated_cancelation_prevented * ((rate_cancelation_prevented)/100) * car_average_rental_price_per_day)

    data = {"Check-in type: " + checkin_type:['Lost', 'Saved'], 
            'Amount':[money_lost, money_saved]}

    df = pd.DataFrame(data)

    ################################################################ DATA VISUALISATION

    fig5 = px.bar(df, 
                x="Check-in type: " + checkin_type, 
                y="Amount", 
                color="Check-in type: " + checkin_type, 
                title="----------", 
                color_discrete_sequence=['#FF0000', '#FFD700'],
                text="Amount",
                width=1000, height=750)
                
    fig5.update_traces(texttemplate='%{text:.0f}' + " $", textposition='outside')
    fig5.update_layout(title_x=0.5, yaxis={'visible': False}, xaxis={'visible': True}, legend_title="", title_text="Effect on money with a minimum time delta of " + str(new_delta) + " with " + checkin_type + " check-in type.", template='plotly_dark', xaxis_title='', showlegend=False)
    fig5.update_yaxes(range=[0,1800000])
    st.plotly_chart(fig5)

################################################################ RESULT EXPLANATION

    st.markdown("<h2 style='text-align: center;'>Explanation for this result</h2>", unsafe_allow_html=True)

    st.write('\n')
    st.write('\n')
    st.write('\n')

    st.write (f"Check-in type: {checkin_type} = {len(data_delay)} cases")
    st.write (f"Cleaning phase: I keep only rentals where we can see the previous rental id and if it was late or not, there are {df_merged.shape[0]} cases left.")
    st.write('\n')
    st.write('\n')
    st.markdown("<h5 style='text-align: left;'>Ended cases</h5>", unsafe_allow_html=True)
    st.write('\n')
    st.write (f"Keeping only ended cases we have {len(df_good_cases)} cases left.")
    st.write(f"With a minimum time delta of {new_delta} minutes we have {len(df_new_time_delta_good_cases)} cases left. We lost {len(df_good_cases) - len(df_new_time_delta_good_cases)} cases from our {len(df_good_cases)} cases.")
    st.write (f"{len(df_good_cases) - len(df_new_time_delta_good_cases)} represents {round((len(df_good_cases) - len(df_new_time_delta_good_cases))/len(df_good_cases)*100, 2)}% of the whole left cases.")
    st.write (f"If we try to apply these cleaning steps to our whole data set. We would be left with {len(df_true_good_cases)} cases")
    st.write (f"{round((len(df_good_cases) - len(df_new_time_delta_good_cases))/len(df_good_cases)*100, 2)}% would be a loss of {round(round((len(df_good_cases) - len(df_new_time_delta_good_cases))/len(df_good_cases)*100, 2) * len(df_true_good_cases) / 100)} rentals for {money_lost}$.")
    st.write('\n')
    st.write('\n')
    st.markdown("<h5 style='text-align: left;'>Canceled cases</h5>", unsafe_allow_html=True)
    st.write('\n')
    st.write (f"Keeping only canceled cases we have {len(df_canceled_cases)} cases left.")
    st.write (f"{len(df_canceled_and_late_cases)} of these cases where late and the next owner did not have the car on time.")
    st.write (f"With a minimum time delta of {new_delta} minutes we have {len(df_new_time_delta_bad_cases)} cases left. We saved {cancelation_prevented} cases from our {len(df_canceled_and_late_cases)} cases. ")
    st.write (f"{cancelation_prevented} represents {round(rate_cancelation_prevented,2)}% of these {len(df_canceled_and_late_cases)} cases.")
    st.write (f"If we try to apply these cleaning steps to our whole data set. We would be left with {round(total_estimated_cancelation_prevented)} cases of check-in type '{checkin_type}' that were canceled and the previous owner was so late that the checkout happened after the expected start of the next rental.")
    st.write (f"If we decide to consider that a cancelation due to lateness happens only when the new car owner has to wait, {round(rate_cancelation_prevented,2)}% would represents {round(round(total_estimated_cancelation_prevented) * (round(rate_cancelation_prevented)/100), 0)} rentals saved for {money_saved}$.")
    st.write (f"With {checkin_type} check-in type and a delta of {new_delta} we saved {money_saved} dollars but we lost {money_lost} dollars.")

    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END
    ################################################################ TEST YOUR OWN VARIABLES END

if __name__ == "__main__":
    main()












