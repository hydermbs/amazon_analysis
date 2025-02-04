import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns
from collections import Counter
import nltk
from nltk.corpus import stopwords
import string
from wordcloud import WordCloud
import streamlit as st
import plotly.express as px
from scraper import extract_data


# Inject custom CSS
st.markdown("""
    <style>
    /* General body styling */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f4f4f9;
        color: #333;
        margin: 0;
        padding: 0;
    }

    /* Title styling */
    .stApp h1 {
        color: #2c3e50;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    /* Sidebar styling */
    .stSidebar {
        background-color: #2c3e50;
        color: #ffffff;  /* Sidebar text color set to white */
        padding: 1rem;
    }

    .stSidebar * {
        color: #dcdcdc !important;  /* Light gray text for sidebar elements */
    }

    .stSidebar .stTextInput input {
        background-color: #34495e;
        color: #ecf0f1;
        border: 1px solid #34495e;
    }

    .stSidebar .stTextInput input:focus {
        border-color: #3498db;
    }

    /* Column styling */
    .stColumn {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .stColumn h3 {
        color: #2c3e50;
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
    }

    /* Table styling */
    .stDataFrame {
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Button styling */
    .stButton button {
        background-color: #3498db;
        color: #ffffff;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        cursor: pointer;
    }

    .stButton button:hover {
        background-color: #2980b9;
    }

    /* Plot styling */
    .stPlotlyChart, .stPyplot {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }

    /* Custom container styling */
    .stContainer {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    /* Custom header styling */
    .stHeader {
        color: #2c3e50;
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }

    /* Custom subheader styling */
    .stSubheader {
        color: #3498db;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.75rem;
    }

    /* Custom text styling */
    .stText {
        color: #333;
        font-size: 1rem;
        line-height: 1.5;
    }

    /* Custom divider styling */
    .stDivider {
        border-top: 2px solid #3498db;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
#Streamlit App

def basic_insights(df):
    # Columns for Basic Insights
    total_products = df['ASIN'].nunique()
    average_ratings = df['Rating'].mean().round(2)
    total_reviews = df['Reviews'].sum()
    product,rating,reviews = st.columns(3,border=True)
    product.subheader(f'Total Products: {total_products}')
    rating.subheader(f'Average Rating: {average_ratings}')
    reviews.subheader(f'Total Reviews: {total_reviews}')

def popularity(df):
    df['Popularity'] = df['Rating']*df['Reviews']
    popularity = df.nlargest(20,'Popularity')
    fig,ax = plt.subplots(figsize=(10,6))
    ax.bar(popularity['ASIN'],popularity['Popularity'],color='skyblue')
    ax.set_title('Top 10 Popular Products')
    ax.set_xlabel('Product ASIN')
    ax.set_ylabel('Popularity')
    ax.set_xticks(range(len(popularity['ASIN'])))
    ax.set_xticklabels(popularity['ASIN'], rotation=45, ha='right')
    ax.grid(axis='y',linestyle='--',alpha=0.7)
    pop_graph, pop_data = st.columns(2,border=True)
    pop_data.write(popularity)
    pop_graph.pyplot(fig)

def price_comparison(df):
    low_price_threshold = df['Price'].quantile(0.25)
    high_price_threshold = df['Price'].quantile(0.75)
    low_rating_threshold = df['Rating'].quantile(0.25)
    high_rating_threshold = df['Rating'].quantile(0.75)
    value_for_money = df[(df['Price']<low_price_threshold) & (df['Rating']>high_rating_threshold)]
    overpriced = df[(df['Price']>high_price_threshold) & (df['Rating']<low_rating_threshold)]
    value_for_money_col, overpriced_col = st.columns(2,border=True)
    value_for_money_col.subheader('Value For Money Products:')
    value_for_money_col.write(value_for_money)
    overpriced_col.subheader('Over Priced Products:')
    overpriced_col.write(overpriced)
    with st.container():
        # Create an interactive scatter plot
        fig = px.scatter(df, x='Price', y='Rating', color='ASIN', hover_name='ASIN',
                        title='Price vs. Rating: Identifying Value-for-Money and Overpriced Products',
                        labels={'Price': 'Price', 'Rating': 'Rating'})

        # Add threshold lines
        fig.add_hline(y=low_rating_threshold, line_dash="dash", line_color="red", annotation_text="Low Rating Threshold")
        fig.add_hline(y=high_rating_threshold, line_dash="dash", line_color="green", annotation_text="High Rating Threshold")
        fig.add_vline(x=low_price_threshold, line_dash="dash", line_color="blue", annotation_text="Low Price Threshold")
        fig.add_vline(x=high_price_threshold, line_dash="dash", line_color="orange", annotation_text="High Price Threshold")
        st.plotly_chart(fig, use_container_width=True)

def discount_analysis(df):
    df['Discount %'] = ((df['List Price']- df['Price'])/df['List Price'])*100
    bins = [0, 10, 20, 30, 100]  # Discount Ranges (last bin is 30%+)
    labels = ['0-10%', '10-20%', '20-30%', '30%+']
    df['Discount Range'] = pd.cut(df['Discount %'], bins=bins, labels=labels)
    discount_counts = df['Discount Range'].value_counts().sort_index()
    st.subheader('Discounted Product Data')
    disc_graph,disc_data = st.columns(2,border=True)
    fig, ax = plt.subplots()
    ax.pie(discount_counts, labels=discount_counts.index, autopct='%1.1f%%', 
        colors=['lightblue', 'lightgreen', 'orange', 'red'], startangle=140)
    ax.set_title("Distribution of Discount Ranges")
    disc_graph.pyplot(fig)
    disc_data.write(df.nlargest(20,'Discount %'))
    
def top_supplier_num_of_product(df):
    product_counts = df['Supplier'].value_counts().reset_index()
    product_counts.columns = ['Supplier','num_products']
    top_5_products = product_counts.sort_values(by='num_products',ascending=False).head(5)
    supplier_product, supplier_rating= st.columns(2,border=True)
    sns.set(style="whitegrid")

    fig_1 = plt.figure(figsize=(10, 6))
    ax = sns.barplot(x='num_products', y='Supplier', data=top_5_products, palette='viridis')

    for p in ax.patches:
        width = p.get_width()
        plt.text(width + 0.1, 
                p.get_y() + p.get_height() / 2, 
                f'{int(width)}',
                va='center')  

    plt.xlabel('Number of Products')
    plt.ylabel('Supplier')
    supplier_product.subheader('Top 5 Suppliers By Number Of Product:')
    supplier_product.pyplot(fig_1)
    max_rating = df.groupby('Supplier')['Rating'].max().reset_index()
    top_5_by_rating = max_rating.sort_values(by='Rating',ascending=False).head(5)
    sns.set(style='whitegrid')
    fig_2 = plt.figure(figsize=(10,6))
    ax = sns.barplot(x='Rating',y='Supplier',data=top_5_by_rating,palette='viridis')
    for p in ax.patches:
        width = p.get_width()
        plt.text(width+0.1,
                p.get_y()+p.get_height()/2,
                f'{float(width)}',
                va='center')
    
    plt.xlabel('Maximum Rating')
    plt.ylabel('Supplier')
    supplier_rating.subheader('Top 5 Suppliers By Highest Rated Products')
    supplier_rating.pyplot(fig_2)  

def most_used_keywords(df):
    st.subheader('Frequently Mentioned Keyword in Features')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))
    def extract_words(text):
        text = text.translate(str.maketrans("","",string.punctuation)).lower()
        words = text.split()
        words = [word for word in words if word not in stop_words]
        return words
    all_keyword = []
    for feature in df['Features']:
        all_keyword.extend(extract_words(feature))
    keyword_freq = Counter(all_keyword)
    keyword_df = pd.DataFrame(keyword_freq.most_common(),columns=['Keywords','Frequency']).head(50)
    keyword_graph, keyword_data = st.columns(2,border=True)
    keyword_data.write(keyword_df)
    word_cloud = WordCloud(width=800,height=400,background_color='white').generate_from_frequencies(keyword_freq)
    word_fig=plt.figure(figsize=(10,5))
    plt.imshow(word_cloud,interpolation='bilinear')
    plt.axis('off')
    keyword_graph.pyplot(word_fig)
    keyword_df = keyword_df.head(25)
    new_df = df
    for keyword in keyword_df['Keywords']:
        new_df[keyword] = new_df['Features'].apply(lambda x: 1 if keyword in x.lower() else 0)
    numeric_df = new_df.drop(columns=['ASIN','Name','Price','Features','Image','Supplier','Supplier_url','Discount Range'])
    correlation_df = numeric_df.corr()['Rating'].drop('Rating').reset_index()
    correlation_df.columns = ['Keyword','Correlation']
    correlation_df['Abs_Correlation'] = correlation_df['Correlation'].abs()
    correlation_df = correlation_df.sort_values(by='Abs_Correlation',ascending=False)
    feature_rating_graph, feature_rating_data = st.columns(2,border=True)
    feature_rating_data.write(correlation_df)
    corre_fig = plt.figure(figsize=(10,6))
    sns.barplot(x='Correlation',y='Keyword',data=correlation_df,palette='coolwarm')
    plt.title('Correlation Between Features and Rating')
    plt.xlabel('Correlation')
    plt.ylabel('Keyword')
    feature_rating_graph.pyplot(corre_fig)

def reviews_vs_rating(df):
    # Calculate thresholds
    few_reviews_threshold = df['Reviews'].quantile(0.25)
    high_rating_threshold = df['Rating'].quantile(0.75)
    high_review_threshold = df['Reviews'].quantile(0.75)
    low_rating_threshold = df['Rating'].quantile(0.25)

    # Identify products
    hidden_gem = df[(df['Reviews'] < few_reviews_threshold) & (df['Rating'] > high_rating_threshold)]
    dissatisfied_products = df[(df['Reviews'] > high_review_threshold) & (df['Rating'] < low_rating_threshold)]

    # Create Streamlit columns
    dissatisfied_products_data, satisfied_product_data = st.columns(2)

    # Display data tables
    satisfied_product_data.subheader('✅ Hidden Gems: Few Reviews & High Rating')
    satisfied_product_data.write(hidden_gem)

    dissatisfied_products_data.subheader('⚠️ Overrated: Many Reviews & Low Rating')
    dissatisfied_products_data.write(dissatisfied_products)

    # Plot in Streamlit
    st.subheader('📊 Reviews vs. Ratings Scatter Plot')
    fig, ax = plt.subplots(figsize=(10, 6))
    
    sns.scatterplot(x='Reviews', y='Rating', data=df, hue=df['ASIN'], s=100, palette='viridis', alpha=0.7, ax=ax, legend=False)
    
    # Add threshold lines
    ax.axhline(y=low_rating_threshold, color='red', linestyle='--', label='Low Rating Threshold')
    ax.axhline(y=high_rating_threshold, color='green', linestyle='--', label='High Rating Threshold')
    ax.axvline(x=high_review_threshold, color='orange', linestyle='--', label='High Review Threshold')
    ax.axvline(x=few_reviews_threshold, color='purple', linestyle='--', label='Few Review Threshold')

    ax.set_title('Review Trends: Reviews vs. Ratings')
    ax.set_xlabel('Number of Reviews')
    ax.set_ylabel('Rating')
    plt.legend()
    plt.tight_layout()

    # Show plot in Streamlit
    st.pyplot(fig)
    


container = st.container()
container.title('Amazon Scraping and Analytics App')
with st.sidebar:
    keyword = st.text_input("Enter Keyword to Search ie: Men Watches")

if keyword:
    st.write(f"Showing result for {keyword}")
    df = extract_data(keyword)
    if not df.empty:
        df['List Price'] = df['List Price'].fillna(0)
        df['List Price'] = df['List Price'].str.replace('$','').str.strip().astype(float)
        df['Reviews'] = df['Reviews'].str.replace(',','').str.replace(' rating','').str.strip().astype(int)
        df['Price'] = df['Price'].str.replace('$','').str.strip().astype(float)
        basic_insights(df)
        st.subheader('Price V/S Rating:')
        price_comparison(df)
        discount_analysis(df)
        st.subheader('Here You can see the details about most popular products:')
        popularity(df)
        top_supplier_num_of_product(df)
        most_used_keywords(df)
        reviews_vs_rating(df)

        st.write("### Scraped Data:")
        st.write(df)
    else:
        st.subheader('No Data Found. Please Check your Internet Connection')
else:
    st.title('Please Search the Product to get the data and to know the analytics')

   




