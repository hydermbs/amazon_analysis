# Amazon Scraping and Analytics App

This is a Streamlit-based web application designed to scrape and analyze product data from Amazon. The app provides insights into product ratings, reviews, pricing, discounts, and supplier information. It also includes visualizations to help users identify trends, popular products, and value-for-money deals.

---

## Features

1. **Basic Insights**:
   - Total number of products.
   - Average product rating.
   - Total number of reviews.

2. **Price vs. Rating Analysis**:
   - Interactive scatter plot to compare product prices and ratings.
   - Identify value-for-money and overpriced products.

3. **Discount Analysis**:
   - Distribution of discount ranges (0-10%, 10-20%, 20-30%, 30%+).
   - Highlight products with the highest discounts.

4. **Popularity Analysis**:
   - Top 20 most popular products based on a combined metric of ratings and reviews.

5. **Supplier Analysis**:
   - Top 5 suppliers by the number of products.
   - Top 5 suppliers by the highest-rated products.

6. **Keyword Analysis**:
   - Word cloud of frequently mentioned keywords in product features.
   - Correlation between keywords and product ratings.

7. **Reviews vs. Ratings Analysis**:
   - Identify hidden gems (few reviews but high ratings).
   - Flag overrated products (many reviews but low ratings).

---

## Technologies Used

- **Python**: Primary programming language.
- **Streamlit**: For building the web app interface.
- **Pandas**: For data manipulation and analysis.
- **Matplotlib & Seaborn**: For static visualizations.
- **Plotly**: For interactive visualizations.
- **NLTK**: For natural language processing (keyword extraction).
- **WordCloud**: For generating word clouds.
- **Web Scraping**: Custom scraper (`scraper.py`) to extract data from Amazon.

---

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/hydermbs/amazon-scraping-analytics.git
   cd amazon-scraping-analytics
   ```

2. **Set Up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK Data**:
   ```python
   python -c "import nltk; nltk.download('stopwords')"
   ```

5. **Run the App**:
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. Enter a keyword (e.g., "Men Watches") in the sidebar to search for products.
2. The app will display scraped data and provide insights through interactive visualizations.
3. Explore different sections like price vs. rating, discounts, popularity, and keyword analysis.

---



## Data Source

The app uses a custom web scraper (`scraper.py`) to extract product data from Amazon. The scraped data is saved in a CSV file (`Amazon_data.csv`) for analysis.

---

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes.
4. Submit a pull request.

---



## Acknowledgments

- Streamlit for the amazing framework to build data apps.
- Pandas, Matplotlib, Seaborn, and Plotly for data manipulation and visualization.
- NLTK for natural language processing.

---

## Contact

For questions or feedback, feel free to reach out:

- **Your Name**: [email me:](mailto:hyderraza26@gmail.com)
- **GitHub**: [Your GitHub Profile](https://github.com/hydermbs)

---

Enjoy exploring the Amazon Scraping and Analytics App! 🚀
