import plotly.express as px
import pandas as pd
import calendar

def generate_visualization(fig1_data : pd.DataFrame, fig2_data : pd.DataFrame, fig3_data):
    ######################################################################################
    # create a pie chart
    fig_pie = px.pie(fig1_data, values="count", 
                names="procedure_name", 
                hole=0.5)
    
    fig_pie.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',)

    ######################################################################################
    # create a bubble chart
    fig2_data['months'] = fig2_data['months'].apply(lambda x: calendar.month_name[int(x)])

    # convert the months to string
    fig_bubble = px.bar(fig2_data, x='revenue', y='months', orientation='h', 
                color='procedure')
             
    fig_bubble.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',)
    
    ######################################################################################
    # create a bar chart
    # sort the months
    fig3_data = fig3_data.sort_values('months')
    fig3_data['months'] = fig3_data['months'].apply(lambda x: calendar.month_name[int(x)])
    fig_bar = px.bar(fig3_data, x='months', y='revenue', 
             color='revenue')

    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',)
    
    return fig_pie, fig_bubble, fig_bar