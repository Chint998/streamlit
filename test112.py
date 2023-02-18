
import streamlit as st
import pandas as pd
from datetime import timedelta
from dateutil.relativedelta import relativedelta 
from datetime import datetime
import matplotlib.pyplot as plt
from PIL import Image
import base64
# Set page title and icon
st.set_page_config(page_title="NRE Estimate", page_icon=":money_with_wings:")

# Define title and image
st.title("NRE Estimate")
img = Image.open("C:\\Users\\cchau\\OneDrive\\Pictures\\Odds Logo.jpg")
st.image(img, width=100)
# Create a divider line
st.markdown("---")
# Add some explanatory text
st.write("Please upload a file in .csv format to perform an NRE estimate.")
# Define background color for the main page
main_bg = "lightgray"



st.set_option('deprecation.showPyplotGlobalUse', False)
mdays = int(28)

@st.cache_data
def read_input_file(file):
    df = pd.read_csv(file, parse_dates=["start_date","milestone1","milestone2","milestone3","end_date"])
    return df
def calculate_values(row):
    row["milestone1"] = row["milestone1"].strftime('%Y-%m')
    row["milestone2"] = row["milestone2"].strftime('%Y-%m')
    row["milestone3"] = row["milestone3"].strftime('%Y-%m')
    
    m1 = datetime.strptime(row["milestone1"], '%Y-%m').date()
    m2 = datetime.strptime(row["milestone2"], '%Y-%m').date()
    m3 = datetime.strptime(row["milestone3"], '%Y-%m').date()  
    
    if row["Effort Type"] == "leadsp":
        start_date = m1 - relativedelta(months=9)
        end_date = m3 + relativedelta(months=9)
        
    elif row["Effort Type"] == "upgrade":
        #print ("oh its Upgrade SP")
        start_date = m1 - relativedelta(months=6)
        end_date = m3 + relativedelta(months=6)

    else:
        #print ("oh its Normal IOT SP")
        start_date = m1 - relativedelta(months=3)
        end_date = m3 + relativedelta(months=6)
        #print("\nstart date is:",start_date)
     
    #Update Peak HC
    TeamName = row["Team Name"]
    #print("start_date is :",start_date)
    #print("end_date is :",end_date)

    
    
    peak = row["peak"]

    Multiply_values = pd.read_excel("D:\Copy of master.xlsx", sheet_name = None)
    if row["Team Name"] not in Multiply_values:
        #print("Not in Master sheet and taking default")
        TeamName = "default"
    else:
        #print("Found in Master sheet and taking respective team")
        TeamName = row["Team Name"]

    value = []
    evalue = []
    for i in range(15):
        value.append(Multiply_values[TeamName].iloc[i,1:i+2].tolist())
    for i in range(20,34):
        evalue.append(Multiply_values[TeamName].iloc[i,1:i+2].tolist())
    #print(value)

    # create a dictionary to store the values for each team
    values = {}
    current_date = start_date
    #print("\nCurrent date is :",current_date)
    diff = (m1.year - current_date.year) * 12 + (m1.month  - current_date.month )
    #print("\n Difference in start and m1 date is:",diff)
    while current_date <= end_date:
        if current_date < m1:
            #print("\nCurrent date in if loop :",current_date)
            for i in range(0,diff):
                values[current_date] = value[diff-1][i] * peak
                current_date += relativedelta(months=1)
                   
        elif (current_date >= m1 and current_date < m2):
           #print("\n in m3 loop")
            values[current_date] = 0.8 * peak
        
        elif (current_date >=m2 and current_date <= m3):
            #print("\n in m3 loop")
            values[current_date] = peak
        
        else:
            diff = (end_date.year - current_date.year) * 12 + (end_date.month  - current_date.month )
            diff+=1
            #print("\n Difference in M3 and end date is:",diff)
            if diff < 12:
                for i in range(0,diff):
                    values[current_date] = evalue[diff-1][i] * peak
                    current_date += relativedelta(months=1)
            else:
                print ("in else.. loop")
                values[current_date] = 0.1 * peak
        current_date += relativedelta(months=1)
    return values
file_upload_bg = "white"
# Set page config
st.markdown(f"""<style>
                div.stFileUploader {{
                    background-color: {file_upload_bg};
                }}
                </style>
             """, unsafe_allow_html=True)
def app():
   # Set page config
    st.markdown(f"""<style>
                .reportview-container {{
                    background: {main_bg};
                }}
                </style>
             """, unsafe_allow_html=True) 
    

    # create a file uploader to upload the input file
    file = st.file_uploader("Upload file", type="csv",)
    
    
    if file is not None:
        # read in the input file
        df = read_input_file(file)
        st.success("File uploaded successfully!")
        # apply the calculate_values function to the dataframe
        df["values"] = df.apply(calculate_values, axis=1)

        # create a new dataframe with the date as the index and team name as columns
        results_df = pd.DataFrame(columns=df["Team Name"])
        for i, row in df.iterrows():
            for date, value in row["values"].items():
                results_df.at[date.strftime("%m-%Y"), row["Team Name"]] = value


        results_df.sort_values(by ='Team Name', axis=1)
        #print (results_df)

        results_df.index = pd.to_datetime(results_df.index, format='%m-%Y')
        results_df = results_df.sort_index()
        results_df.index = results_df.index.strftime('%Y-%m')

        results_ouput = results_df.copy()
        results_ouput = results_ouput.sort_index()
        st.header('Estimated results')
        st.write(results_ouput)
            # Add an option to download the output
        if st.download_button(
        label="Download results as CSV",
        data=results_ouput.to_csv().encode('utf-8'),
        file_name='nre_estimate_results.csv',
        mime='text/csv'
    ):
            st.success("You have downloaded the NRE Estimate.")
    


if __name__ == "__main__":
        app()