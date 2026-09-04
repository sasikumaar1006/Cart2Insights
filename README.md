# Cart2Insights
### Overview
  An end-to-end e-commerce analytics project built using the Olist Brazilian E-Commerce Dataset. The project covers the complete data analytics workflow, including data cleaning and preprocessing, feature engineering, exploratory data analysis (EDA), SQL integration, and interactive dashboard development.
  The goal is to transform raw e-commerce transaction data into actionable business insights related to sales, customers, products, sellers, payments, delivery performance, and customer reviews.
  
### Datasets Covered
The analysis processes 9 core relational datasets:  
1. customers_df : Customer ID and location mapping.
2. orders_df : Order status, purchase, and delivery timestamps.
3. products_df : Product dimensions, weights, and categories.
4. sellers_df : Seller identification and locations.
5. order_payments_df : Payment types, installments, and values.
6. order_reviews_df : Customer ratings, review comments, and timestamps.
7. order_items_df : Item pricing, freight costs, and seller associations.
8. product_category_translation_df : Portuguese to English category mappings.
9. geolocation_df : Zip code coordinates and geographic metrics.
   
### End to End Pipeline:

**1. Data Processing & Feature Engineering**
  - Cleaning raw datasets and handling data quality issues
  - Missing-value imputation and treatment
  - Data type corrections and duplicat-e handling
  - Feature creation for deeper business analysis
  - Dataset integration using relational keys
    
**2. Exploratory Data Analysis & Business Insights**
  - Sales and revenue trend analysis
  - Product and category performance analysis
  - Customer behavior and retention analysis
  - Seller performance evaluation
  - Payment method and installment analysis
  - Delivery performance and logistics analysis
  - Customer review and satisfaction analysis
  - Correlation analysis between operational metrics and review scores
    
**3. Database Integration**
  - Structured data storage using SQL
  - Backend integration for efficient data management
  - Analytical queries for business reporting

**4. Interactive Dashboard** - 
    A Streamlit dashboard providing dynamic visualizations and business insights across key e-commerce areas, including:
  - Business Overview
  - Sales Analysis
  - Customer Analysis
  - Seller & Product Analysis
  - Delivery Analysis
  - Customer Experience

### Key Objective:
  The primary objective of Cart2Insights is to demonstrate how raw relational e-commerce data can be transformed into meaningful insights through a complete analytics workflow, from data preprocessing and engineering to database integration and interactive business intelligence dashboards.
  The project is designed to showcase practical skills in Python, SQL, data analysis, feature engineering, exploratory data analysis, and data visualization.
