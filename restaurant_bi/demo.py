"""
Demo script showcasing Restaurant Market Analysis capabilities
"""
from .market_analysis_agent import RestaurantMarketAnalysisAgent
import json
import streamlit as st

def run_market_analysis_demo():
    """Run an interactive demo of the market analysis system"""
    st.title("Restaurant Market Analysis Demo")
    
    # Initialize agent
    try:
        agent = RestaurantMarketAnalysisAgent()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please ensure all required environment variables are set.")
        return
    
    # Location input
    st.header("Location Settings")
    col1, col2 = st.columns(2)
    with col1:
        latitude = st.number_input("Latitude", value=51.5074, format="%.4f")
    with col2:
        longitude = st.number_input("Longitude", value=-0.1278, format="%.4f")
    
    radius = st.slider("Search Radius (meters)", 1000, 10000, 5000, step=500)
    
    # Optional cuisine type
    cuisine_type = st.text_input("Cuisine Type (optional)", "")
    
    if st.button("Analyze Market"):
        with st.spinner("Analyzing market data..."):
            # Get market insights
            insights = agent.get_market_insights(
                location={'lat': latitude, 'lng': longitude},
                radius=radius,
                cuisine_type=cuisine_type if cuisine_type else None
            )
            
            # Display results
            st.header("Market Analysis Results")
            
            # Market Overview
            st.subheader("Market Overview")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Restaurants", 
                    insights['market_data']['total_restaurants'])
            with col2:
                st.metric("Avg Rating", 
                    round(insights['market_data']['avg_rating'], 2))
            with col3:
                st.metric("Market Saturation", 
                    f"{round(insights['market_saturation_score'], 1)}%")
            
            # Price Level Distribution
            st.subheader("Price Level Distribution")
            price_dist = insights['market_data']['price_level_distribution']
            st.bar_chart(price_dist)
            
            # Cuisine Analysis
            st.subheader("Cuisine Analysis")
            cuisine_data = insights['market_data']['cuisine_analysis']
            st.write(f"Total Cuisine Types: {cuisine_data['total_cuisines']}")
            st.write("Top Cuisines:")
            st.json(cuisine_data['top_cuisines'])
            
            # Cuisine-specific insights if provided
            if cuisine_type and insights.get('cuisine_specific_insights'):
                st.subheader(f"{cuisine_type} Restaurant Insights")
                cuisine_insights = insights['cuisine_specific_insights']
                st.write(f"Matching Restaurants: {cuisine_insights['matching_restaurants']}")
                if cuisine_insights['avg_rating']:
                    st.write(f"Average Rating: {round(cuisine_insights['avg_rating'], 2)}")
            
            # Success Examples
            if insights.get('similar_successful_venues'):
                st.subheader("Successful Venues in Area")
                for venue in insights['similar_successful_venues']:
                    with st.expander(f"{venue['name']} ({venue['rating']}⭐)"):
                        st.write("Categories:", ", ".join(venue['categories']))
                        st.write("Price Level:", "💰" * venue.get('price_level', 1))
            
            # Recommendations
            st.subheader("Market Recommendations")
            for rec in insights['recommendations']:
                st.info(rec)
            
            # Display map
            st.header("Restaurant Heatmap")
            map_data = agent.generate_heatmap(
                location={'lat': latitude, 'lng': longitude},
                radius=radius
            )
            map_html = map_data._repr_html_()
            st.components.v1.html(map_html, height=600)

if __name__ == "__main__":
    run_market_analysis_demo()