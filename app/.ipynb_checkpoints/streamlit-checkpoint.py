import streamlit as st
import pandas as pd
import time
import base64
import os
import numpy as np
import re
import replicate  # Make sure you have this installed
import openai
from datetime import datetime

st.set_page_config(layout = "wide")
def clean_room_name(name):
    cleaned_name = re.sub(r'\W+', '_', name)  # replaces non-alphanumeric characters with underscore
    return cleaned_name.lower()

def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')

def get_room_description(room_name, file):
    client = replicate.Client(api_token='r8_D6GiXv5agc4w6ujK5vx7NenLGZ2Gg6O37fvtQ')  # Add your actual API key here
    encoded_image = base64.b64encode(file.read()).decode()  # Encode image to base64
    result = client.run(
        "daanelson/minigpt-4:b96a2f33cc8e4b0aa23eacfce731b9c41a7d9466d9ed4e167375587b54db9423",
        input={
            "image": f"data:image/jpeg;base64,{encoded_image}",
            "prompt": f'This is a {room_name}. Describe it like a realtor would for a listing description. As a rule, do not mention things that do not stay with a home when it is typically sold, like beds, fans, TVs, chairs/barstools, and couches etc. Focus on the {room_name} and house itself.',
            "temperature": 2
        }
    )
    return result 
def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
openai.api_key = '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'
def summarize(text):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=500,
    temperature=2,
    top_p=0.9,
    frequency_penalty=0.5,
    messages=[
        {
          "role": "system",
          "content": "You are a helpful assistant for text summarization for listing descriptions for a realtor. As a rule, focus on the space and house itself. Do not mention things that do not stay with a home when it is typically sold, like beds, TVs, chairs/barstools, and couches.",
        },
        {
          "role": "user",
          "content": f"Summarize this description of this house like you would a real estate listing. Focus on the more important aspects like the master bedroom/bathroom, kitchen, and the overall appearance. As a rule, focus on the space and house itself. Do not mention things that do not stay with a home when it is typically sold, like beds, TVs, chairs/barstools, and couches. Here is the description: {text}",
        },
    ],)
    return response.choices[0].message['content']


def summarize_all(text):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens=500,
    temperature=1.5,
    top_p=0.9,
    frequency_penalty=0.5,
    messages=[
        {
          "role": "system",
          "content": "You are a helpful assistant for text summarization for listing descriptions for a realtor.",
        },
        {
          "role": "user",
          "content": f"Summarize these summaries of this house like you would a real estate listing for a realtor. Focus on the more important aspects like the master bedroom/bathroom, kitchen, and the overall appearance. As a rule, focus on the space and house itself. Do not mention things that do not stay with a home when it is typically sold, like beds, TVs, chairs/barstools, and couches. Another rule, do not mention anything about house placement or roofs. Here are the descriptions: {text}",
        },
    ],)
    return response.choices[0].message['content']

def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def main():
    st.markdown("# Realtor Listing Description Generator")

    # Add sections for property details
    st.markdown("## Property Details")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        address = st.text_input('Address')
    with col2:
        beds = st.number_input('Number of Beds', min_value=0, step=1)
    with col3:
        baths = st.number_input('Number of Baths', min_value=0, step=1)
    with col4:
        misc_rooms = st.number_input('Miscellaneous Rooms', min_value=0, step=1)
    with col5:
        sqft = st.number_input('Square Feet', min_value=0, step=1)

    st.markdown("## Add Rooms")
    room_names_input = st.text_input('Enter room names you want to be described separated by commas')
    room_names = [name.strip() for name in room_names_input.split(',')] if room_names_input else []

    images = []
    upload_rooms = []
    for room_name in room_names:
        upload_rooms.append(room_name)
        if len(upload_rooms) == 4 or room_name == room_names[-1]:
            cols = st.columns(len(upload_rooms))
            for i, room_name in enumerate(upload_rooms):
                with cols[i]:
                    room_file = st.file_uploader(f"Upload image for {room_name}", type=['png', 'jpg', 'jpeg'])
                    if room_file:
                        st.image(room_file.read())
                        room_file.seek(0)  # Resets the file cursor back to the start
                    images.append(room_file)
            upload_rooms = []

    if room_names and all(images):
        if st.button('Generate Descriptions', key='generate'):
            output_dataframe = pd.DataFrame(columns=['DateTime', 'Address', 'Beds', 'Baths', 'Misc Rooms', 'Sqft', 'Room Name', 'Description', 'Time Taken', 'Summaries', 'Summary2', 'Summary3', 'Overall Summary'])
            house_details = f'House details: {beds}, {baths}, {sqft}. House Description: '
            task = 'The following is a description of a house. Summarize it like you would if you were a realtor making a listing description. Do not mention things that do not stay with a home when it is typically sold, like TVs, chairs/barstools, and couches. Another rule, do not mention anything about house placement or roofs. Here are the details:' 
            prompt = task + house_details  # initialize 'prompt' here
            for room_name, room_file in zip(room_names, images):
                start_time = time.time()
                room_description = get_room_description(room_name.strip(), room_file)
                end_time = time.time()

                time_taken = end_time - start_time
                st.write(f'Done generating description for {room_name} in {np.round(time_taken,2)} seconds')

                # Add each room description to the summary prompt
                prompt += ' ' + room_description

            st.write('Generating overall summaries...')
            start_time_summary = time.time()
            summary = summarize(prompt)
            summary2 = summarize(prompt)
            summary3= summarize(prompt)
            summaries = summary+summary2+summary3
            summary_all = summarize_all(task+summaries)
            end_time_summary = time.time()
            time_taken_summary = end_time_summary - start_time_summary
            st.write(f'Done generating summary in {np.round(time_taken_summary,2)} seconds')

            # Prepare row data
            row_data = {
                'DateTime': datetime.now(),
                'Address': address,
                'Beds': beds,
                'Baths': baths,
                'Misc Rooms': misc_rooms,
                'Sqft': sqft,
                'Room Name': room_name,
                'Description': room_description,
                'Time Taken': time_taken,
                'Summaries': summary,
                'Summary2': summary2,
                'Summary3': summary3,
                'Overall Summary': summary_all
            }
            output_dataframe.loc[len(output_dataframe)] = row_data

            with st.expander("See Summaries"):
                st.markdown("## Summaries")
                st.markdown("### Choose Between 3 Generated Summaries")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(summary)
                with col2:
                    st.write(summary2)
                with col3:
                    st.write(summary3)
            with st.expander("See Overall Summary"):
                st.markdown("## Summary")
                st.write(summary_all)
                
            # Add a download link
            csv = convert_df(output_dataframe)
            st.download_button(
           "Press to Download",
           csv,
           f"{address}.csv",
           "text/csv",
           key='download-csv'
        )
        else:
            st.write('Please upload an image for each room.')
    else:
        st.write('Please enter at least one room name and upload images.')

if __name__ == "__main__":
    main()