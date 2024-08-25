import datetime
import pandas as pd
import streamlit as st
#from streamlit_datetime_range_picker import datetime_range_picker
from streamlit_date_picker import date_range_picker, PickerType
import plotly.express as px
import plotly.graph_objects as go

def main():
    st.set_page_config(
        page_title="Customer Complaints",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://www.extremelycoolapp.com/help',
            'Report a bug': "https://www.extremelycoolapp.com/bug",
            'About': "# This is a header. This is an *extremely* cool app!"
        }
    )
    
    uploaded_file = st.file_uploader("Choose a file") 
    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
    else:
        return
        #data = pd.read_csv('./Financial Consumer Complaints_new.csv')


    css = '''
    <style>
        .stApp {
        background-color: lightBlue;
        }
    </style>
    '''

    st.markdown(css, unsafe_allow_html=True)

    st.header('Financial consumer complaints dashboard')
    st.write('About project: For any organization which deals in transactions it is really important to build trust for their consumers, Consumers should really feel that their amount is in safe hands. This dashboard would enable companies to analyze the consumer complaints regarding financial transactions. This data is being taken from data.world open source website.')
    # st.write(data)
    
    # Create Filter Panel
    st.sidebar.write('Filter by')
    product_list = sorted(data['Product'].unique())
    #with st.sidebar.expander('View'):
    #    options = st.multiselect(
    #    "Products",
    #    product_list,
    #    product_list
    #    )

    #st.sidebar.slider('Date submited') 

    # Use datetime_range_picker to create a datetime range picker
    with st.sidebar: 
        #st.write(data.dtypes)
        data['Date Sumbited'] = pd.to_datetime(data['Date Sumbited'])
        min_date, max_date = str(data['Date Sumbited'].min().date()), str(data['Date Sumbited'].max().date())

        min_date = datetime.datetime.strptime(min_date, '%Y-%m-%d')
        max_date = datetime.datetime.strptime(max_date, '%Y-%m-%d')

        #date_range_string = date_range_picker(picker_type=PickerType.date,
        #                                            start=min_date, end=max_date,
        #                                            key='date_range_picker'
        #                                                            )
        
    
    # Reset button
    if "reset" not in st.session_state:
        st.session_state.reset = False

    with st.sidebar:
        inp1 = min_date if st.session_state.reset else st.session_state.get('inp1', min_date) # get -> dictionary cua session_state - inp1:min_date
        inp2 = max_date if st.session_state.reset else st.session_state.get('inp2', max_date)

        start_date, end_date = date_range_picker(picker_type=PickerType.date,
                                                        start=inp1, end=inp2,
                                                        key='date_range_picker'
                                                                        )
        st.session_state.inp1, st.session_state.inp2 = datetime.datetime.strptime(start_date, '%Y-%m-%d'), \
                                                        datetime.datetime.strptime(end_date, '%Y-%m-%d')   
        
    with st.sidebar.expander('View'):
        inp3 = product_list if st.session_state.reset else st.session_state.get('inp3', product_list)
        st.session_state.inp3 = st.multiselect("Products", product_list,)
            

    # Reset button
    if st.sidebar.button("Reset values"):
        st.session_state.reset = True  # Mark reset as True if button is pressed
        st.rerun()  # Rerun the script
    else:
        st.session_state.reset = False  # Reset the reset flag

    # Interactive Dashboard
    #start_date, end_date = date_range_string
    data = data[(data['Date Sumbited'] >= start_date) & (data['Date Sumbited'] <= end_date)]
    data = data[data['Product'].isin(st.session_state.inp3)]
    if data.empty:
        st.write('No data available')
        return
    
    # Create columns for KPIs cards
    col1, col2 = st.columns(2)
    with col1:
        st.write('###### TOTAL COMPLAINTS')
        st.write(f"### {data['Complaint ID'].nunique()}")
    

    with col2:
        st.write('###### TIMELY RESPONSE')
        timely_reponse_rate = round(data[data['Timely response?']=='Yes'].shape[0] / data.shape[0] * 100, 2)
        st.write(f"### {str(timely_reponse_rate)}%")

    # Create columns for bar char & heatmap
    col1, col2 = st.columns(2)
    with col1:
        fig = show_complaint_by_category(data, 'Issue', 'Issue')
        st.plotly_chart(fig)
    

    with col2:
        fig = show_complaint_by_state(data)
        st.plotly_chart(fig)
        
    # Create detailed charts
    col1, col2, col3 = st.columns(3)
    with col1:
        fig = show_complaint_by_category(data, 'Submitted via', 'Media')
        st.plotly_chart(fig)
    

    with col2:
        fig = show_complaint_by_category(data, 'Product', 'Product')
        st.plotly_chart(fig)
    
    with col3:
        fig = show_complaint_by_dispute(data)
        st.plotly_chart(fig)


          

def show_complaint_by_issue(data):
    data_bar = data.groupby('Issue')['Complaint ID'].count().reset_index().sort_values('Complaint ID', ascending=True).head(10)
    fig = px.bar(data_bar, x = 'Complaint ID' , y = 'Issue', orientation='h', text_auto=True)
    fig.update_layout(title_text='<i>Total Complaints</i> by <i>Issue</i>', title_x=0.5)
    fig.update_xaxes(title='', showticklabels=False, showgrid=False)
    fig.update_yaxes(title='')
    # fig.update_traces(marker_color=['#071633', '#0DEFFF'])
    fig.update_layout( plot_bgcolor='white' )
    return fig

def show_complaint_by_state(data):
    data_heatmap = data['State'].value_counts()
    fig = px.choropleth(locations=data_heatmap.index, locationmode="USA-states", color=data_heatmap.values, scope="usa")
    return fig


def show_complaint_by_category(data, category, title):
    data_bar = data[category].value_counts().sort_values().iloc[:10]

    fig = px.bar(x = data_bar.values , y = data_bar.index , orientation='h', text_auto=True)
    fig.update_layout(title_text=f'Total Complaints by {title}') #title_x=0.5)
    fig.update_xaxes(title='', showticklabels=False, showgrid=False)
    fig.update_yaxes(title='')
    # fig.update_traces(marker_color=['#071633', '#0DEFFF'])
    fig.update_layout( plot_bgcolor='white' )
    return fig


def show_complaint_by_dispute(data):
    data_donut = data['Consumer disputed?'].value_counts(dropna=False).sort_values()

    labels = data_donut.index
    values = data_donut.values
    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.7, direction ='clockwise', sort=True)])
    return fig


if __name__ == '__main__':
    main()
    
    

    