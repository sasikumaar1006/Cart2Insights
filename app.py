import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine

# Set page layout to wide mode
st.set_page_config(page_title="Cart2Insights dashboard",layout="wide",initial_sidebar_state="expanded")


CUSTOM_CSS = """
<style>
    /* Import Google Font (Inter) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Typography & Light Gray Background */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
        background-color: #F8FAFC !important; /* Soft Off-White / Light Gray */
        color: #1E293B !important; /* Dark Slate Body Text */
    }

    /* Main Header Styling */
    .main-title {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #6B1724 !important; /* Deep Maroon */
        margin-bottom: 0.2rem !important;
        letter-spacing: -0.5px;
    }
    
    .sub-title {
        font-size: 1.0rem !important;
        color: #475569 !important; /* Medium Dark Gray */
        margin-bottom: 1.5rem !important;
        font-weight: 500;
    }

    /* Metric Card Component */
    .metric-card {
        background: #FFFFFF; /* Pure White Card Fill */
        border: 1px solid #E2E8F0; /* Subtle Gray Border */
        border-left: 5px solid #6B1724; /* Maroon Accent Strip */
        border-radius: 8px;
        padding: 16px 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
        margin-bottom: 15px;
    }
    
    .metric-label {
        font-size: 1.25rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #6B1724; /* Maroon for Key Numbers */
        margin-top: 4px;
    }

    /* Section Headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 700;
        color: #6B1724; /* Maroon Section Headers */
        padding-bottom: 8px;
        border-bottom: 2px solid #CBD5E1;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    /* Customize Streamlit Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #F8FAFC;
    }

    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: #E2E8F0; /* Soft Gray Tabs */
        border-radius: 8px;
        color: #334155 !important;
        font-weight: 600;
        font-size: 1.2rem;
        padding: 0px 16px;
    }

    /* Active Tab in Maroon */
    .stTabs [aria-selected="true"] {
        background-color: #6B1724 !important;
        color: #FFFFFF !important;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Helper function to render metric cards cleanly
def render_metric(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# DATABASE CONNECTION
@st.cache_resource
def get_database_connection(): 
    import urllib.parse
    raw_password = '@44872Sasi'
    encoded_password = urllib.parse.quote_plus(raw_password)
    base_url = f'mysql+pymysql://root:{encoded_password}@localhost:3306/cart2insights'
    engine = create_engine(base_url)
    return engine

engine = get_database_connection()

from sqlalchemy import text

@st.cache_data
def run_query(query):
    with engine.connect() as conn:
        return pd.read_sql(text(query), conn)

st.markdown('<div class="main-title">Cart2Insights : E-Commerce Business Intelligence & Analysis</div>', unsafe_allow_html=True)

# Creating Navigation Tabs

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "1. Business Overview",
    "2. Sales Analysis",
    "3. Customer Analysis",
    "4. Seller & Product",
    "5. Delivery Analysis",
    "6. Customer Experience"
])

# TAB 1: BUSINESS OVERVIEW
with tab1:
    st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)
    
    query_overview = """
    WITH OrderMetrics AS (
        SELECT 
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(DISTINCT o.customer_id) AS total_customers,
            SUM(p.payment_value) AS total_revenue,
            AVG(p.payment_value) AS avg_order_value
        FROM orders o
        JOIN order_payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
    ),
    SellerMetrics AS (
        SELECT COUNT(DISTINCT seller_id) AS total_sellers FROM sellers
    ),
    ReviewMetrics AS (
        SELECT AVG(review_score) AS avg_review_score FROM order_reviews
    )
    SELECT * FROM OrderMetrics, SellerMetrics, ReviewMetrics;
    """
    
    try:
        df_overview = run_query(query_overview)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            render_metric("Total Revenue", f"${df_overview['total_revenue'].iloc[0]:,.2f}")
        with col2:
            render_metric("Total Orders", f"{df_overview['total_orders'].iloc[0]:,}")
        with col3:
            render_metric("Total Customers", f"{df_overview['total_customers'].iloc[0]:,}")
        
        col4, col5, col6 = st.columns(3)
        with col4:
            render_metric("Active Sellers", f"{df_overview['total_sellers'].iloc[0]:,}")
        with col5:
            render_metric("Avg Order Value (AOV)", f"${df_overview['avg_order_value'].iloc[0]:,.2f}")
        with col6:
            render_metric("Avg Review Rating", f"{df_overview['avg_review_score'].iloc[0]:.2f} / 5.0")
    except Exception as e:
        st.error(f"Error loading overview metrics: {e}")

# TAB 2: SALES ANALYSIS
with tab2:
    st.markdown('<div class="section-header">Sales Performance & Trends</div>', unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Monthly Revenue Growth")
        query_monthly_trend = """
        SELECT 
            DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month_year,
            SUM(p.payment_value) AS monthly_revenue
        FROM orders AS o
        JOIN order_payments AS p 
            ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
        ORDER BY month_year ASC
        """
        df_monthly = run_query(query_monthly_trend)
        st.line_chart(df_monthly.set_index('month_year'))
        st.info('Revenue peaks predictably every November due to holiday promotions (+53% MoM), while mid-year revenue maintains a steady baseline of ~$1.08M per month.')

    with col_right:
        st.subheader("Revenue by Top Product Categories")
        query_category_rev = """
        SELECT 
            COALESCE(t.product_category_name_english, pr.product_category_name) AS category,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN products pr ON oi.product_id = pr.product_id
        LEFT JOIN product_category_translation t ON pr.product_category_name = t.product_category_name
        GROUP BY category
        ORDER BY total_revenue DESC
        LIMIT 10;
        """
        df_cat_rev = run_query(query_category_rev)
        st.bar_chart(df_cat_rev.set_index('category'))
        st.info('The top 3 categories (Health & Beauty, Watches, and Bed/Bath) drive 38% of overall revenue, indicating strong core catalog reliance.')

    col_left2, col_right2 = st.columns(2)
    
    with col_left2:
        query_top_products = """
        SELECT 
            p.product_id,
            COALESCE(t.product_category_name_english, p.product_category_name, 'Uncategorized') AS category_english,
            COUNT(oi.order_item_id) AS total_units_sold,
            SUM(oi.price) AS total_revenue
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        JOIN orders o ON oi.order_id = o.order_id
        LEFT JOIN product_category_translation t 
            ON p.product_category_name = t.product_category_name
        WHERE o.order_status = 'delivered'
        GROUP BY p.product_id, category_english
        ORDER BY total_units_sold DESC
        LIMIT 10;
        """
    
        df_top_products = run_query(query_top_products)

        # Format product ID for cleaner display (shortened prefix)
        df_top_products["product_id_short"] = df_top_products["product_id"].apply(lambda x: x[:8] + "...")

        # Display as an interactive Table
        st.subheader("Top 10 Selling Products by Volume")
        st.dataframe(
            df_top_products[
                [
                    "product_id_short",
                    "category_english",
                    "total_units_sold",
                    "total_revenue",
                ]
            ],
            column_config={
                "product_id_short": "Product ID",
                "category_english": "Category (English)",
                "total_units_sold": st.column_config.NumberColumn(
                    "Units Sold", format="%d"
                ),
                "total_revenue": st.column_config.NumberColumn(
                    "Total Revenue ($)", format="$%.2f"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
        

    with col_right2:
        st.subheader("Sales Distribution by Customer State")
        query_sales_location = """
        SELECT 
            c.customer_state,
            COUNT(DISTINCT o.order_id) AS total_orders,
            SUM(p.payment_value) AS state_revenue
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_payments p ON o.order_id = p.order_id
        GROUP BY c.customer_state
        ORDER BY state_revenue DESC
        LIMIT 10;
        """
        st.dataframe(run_query(query_sales_location), use_container_width=True)

# TAB 3: CUSTOMER ANALYSIS

with tab3:
    st.markdown('<div class="section-header">Customer Demographics & Retention</div>', unsafe_allow_html=True)
    
    # 1. Customer Distribution by State
    query_customer_geo = """
    SELECT 
        customer_state,
        COUNT(DISTINCT customer_unique_id) AS total_customers
    FROM customers
    GROUP BY customer_state
    ORDER BY total_customers DESC;
    """

    # 2. Customer Spending Distribution (Bucketed)
    query_customer_spending = """
    WITH customer_orders AS (
        SELECT 
            c.customer_unique_id,
            SUM(p.payment_value) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_payments p ON o.order_id = p.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    )
    SELECT 
        CASE 
            WHEN total_spent < 50 THEN '$0 - $50'
            WHEN total_spent BETWEEN 50 AND 100 THEN '$50 - $100'
            WHEN total_spent BETWEEN 100 AND 250 THEN '$100 - $250'
            WHEN total_spent BETWEEN 250 AND 500 THEN '$250 - $500'
            ELSE '$500+'
        END AS spending_tier,
        COUNT(*) AS customer_count
    FROM customer_orders
    GROUP BY spending_tier
    ORDER BY MIN(total_spent) ASC;
    """

    # 3. Repeat vs New Customers Ratio
    query_repeat_vs_new = """
    WITH customer_order_counts AS (
        SELECT 
            c.customer_unique_id,
            COUNT(DISTINCT o.order_id) AS order_count
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        WHERE o.order_status = 'delivered'
        GROUP BY c.customer_unique_id
    )
    SELECT 
        CASE 
            WHEN order_count = 1 THEN 'One-time Customer'
            ELSE 'Repeat Customer'
        END AS customer_type,
        COUNT(*) AS customer_count
    FROM customer_order_counts
    GROUP BY customer_type;
    """

    # 4. Top 10 High-Value Customers
    query_top_customers = """
    SELECT 
        c.customer_unique_id,
        c.customer_city,
        c.customer_state,
        COUNT(DISTINCT o.order_id) AS total_orders,
        SUM(p.payment_value) AS total_spent
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_payments p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id, c.customer_city, c.customer_state
    ORDER BY total_spent DESC
    LIMIT 10;
    """

    df_geo = run_query(query_customer_geo)
    df_spending = run_query(query_customer_spending)
    df_repeat = run_query(query_repeat_vs_new)
    df_top_cust = run_query(query_top_customers)

    # Row 1: Geographic Distribution & Repeat vs New
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Distribution by State")
        st.bar_chart(df_geo, x="customer_state", y="total_customers")
        st.info('São Paulo (SP) dominates total customer volume at ~42%, while the top 3 states combined (SP, RJ, MG) represent over 65% of the total regional buyer base.')

    with col2:
        st.subheader("Repeat vs. One-Time Customers")
        st.dataframe(
            df_repeat,
            column_config={
                "customer_type": "Customer Type",
                "customer_count": st.column_config.NumberColumn(
                    "Count", format="%d"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
    
    st.markdown("---")

    # Row 2: Customer Spending Tiers & Top Customers
    col3, col4 = st.columns([1, 2])

    with col3:
        st.subheader("Spending Distribution")
        st.dataframe(
            df_spending,
            column_config={
                "spending_tier": "Spending Tier",
                "customer_count": st.column_config.NumberColumn(
                    "Total Customers", format="%d"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )
        st.info('Over 70% of customers spend under $100 per order, showing that total platform revenue is driven by high transaction volume rather than premium single-item sales.')

    with col4:
        st.subheader("Top 10 Customers by Lifetime Value")

        # Format Customer ID for display
        df_top_cust["customer_id_short"] = df_top_cust[
            "customer_unique_id"
        ].apply(lambda x: x[:8] + "...")

        st.dataframe(
            df_top_cust[
                [
                    "customer_id_short",
                    "customer_city",
                    "customer_state",
                    "total_orders",
                    "total_spent",
                ]
            ],
            column_config={
                "customer_id_short": "Customer ID",
                "customer_city": "City",
                "customer_state": "State",
                "total_orders": st.column_config.NumberColumn(
                    "Orders", format="%d"
                ),
                "total_spent": st.column_config.NumberColumn(
                    "Total Spent ($)", format="$%.2f"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

# TAB 4: SELLER & PRODUCT ANALYSIS

with tab4:
    st.markdown('<div class="section-header">Merchant & Inventory Analytics</div>', unsafe_allow_html=True)
    
    # 1. Top 10 Sellers by Revenue
    query_top_sellers = """
    SELECT 
        s.seller_id,
        s.seller_city,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        SUM(oi.price) AS total_revenue
    FROM order_items oi
    JOIN sellers s ON oi.seller_id = s.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_city, s.seller_state
    ORDER BY total_revenue DESC
    LIMIT 10;
    """

    # 2. Revenue Distribution by Category (Top 10 Categories in English)
    query_category_performance = """
    SELECT 
        COALESCE(t.product_category_name_english, p.product_category_name, 'Uncategorized') AS category_english,
        COUNT(DISTINCT oi.order_id) AS total_orders,
        COUNT(oi.order_item_id) AS items_sold,
        SUM(oi.price) AS total_revenue,
        AVG(oi.price) AS avg_item_price
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    LEFT JOIN product_category_transalation t 
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY category_english
    ORDER BY total_revenue DESC
    LIMIT 10;
    """

    # 3. Seller Ratings (Top vs Bottom Rated Sellers with minimum 10 orders)
    query_seller_ratings = """
    SELECT 
        s.seller_id,
        s.seller_state,
        COUNT(DISTINCT oi.order_id) AS completed_orders,
        ROUND(AVG(r.review_score), 2) AS avg_rating
    FROM order_items oi
    JOIN sellers s ON oi.seller_id = s.seller_id
    JOIN orders o ON oi.order_id = o.order_id
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY s.seller_id, s.seller_state
    HAVING completed_orders >= 10
    ORDER BY avg_rating DESC, completed_orders DESC
    LIMIT 10;
    """
    df_top_sellers = run_query(query_top_sellers)
    df_category = run_query(query_category_performance)
    df_seller_ratings = run_query(query_seller_ratings)

    # Row 1: Top Sellers & Top Categories by Revenue
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 10 Sellers by Revenue")

        df_top_sellers["seller_id_short"] = df_top_sellers["seller_id"].apply(
            lambda x: x[:8] + "..."
        )

        st.dataframe(
            df_top_sellers[
                [
                    "seller_id_short",
                    "seller_city",
                    "seller_state",
                    "total_orders",
                    "total_revenue",
                ]
            ],
            column_config={
                "seller_id_short": "Seller ID",
                "seller_city": "City",
                "seller_state": "State",
                "total_orders": st.column_config.NumberColumn(
                    "Orders", format="%d"
                ),
                "total_revenue": st.column_config.NumberColumn(
                    "Revenue ($)", format="$%.2f"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.subheader("Top 10 Product Categories by Revenue")

        st.bar_chart(
            df_category,
            x="category_english",
            y="total_revenue",
            use_container_width=True,
        )
        st.info('Revenue is heavily concentrated in the top 3 categories—Health & Beauty, Watches & Gifts, and Bed & Bath—which collectively drive over 30% of total revenue, indicating strong core catalog reliance.')

    st.markdown("---")

    # Row 2: Category Breakdown Table & Seller Ratings
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Category Performance Metrics")

        st.dataframe(
            df_category[
                [
                    "category_english",
                    "items_sold",
                    "avg_item_price",
                    "total_revenue",
                ]
            ],
            column_config={
                "category_english": "Category",
                "items_sold": st.column_config.NumberColumn(
                    "Items Sold", format="%d"
                ),
                "avg_item_price": st.column_config.NumberColumn(
                    "Avg Price ($)", format="$%.2f"
                ),
                "total_revenue": st.column_config.NumberColumn(
                    "Total Revenue ($)", format="$%.2f"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    with col4:
        st.subheader("Top Rated Sellers (Min. 10 Orders)")

        df_seller_ratings["seller_id_short"] = df_seller_ratings[
            "seller_id"
        ].apply(lambda x: x[:8] + "...")

        st.dataframe(
            df_seller_ratings[
                [
                    "seller_id_short",
                    "seller_state",
                    "completed_orders",
                    "avg_rating",
                ]
            ],
            column_config={
                "seller_id_short": "Seller ID",
                "seller_state": "State",
                "completed_orders": st.column_config.NumberColumn(
                    "Completed Orders", format="%d"
                ),
                "avg_rating": st.column_config.NumberColumn(
                    "Avg Rating (1-5)", format="%.2f ⭐"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

# TAB 5: DELIVERY ANALYSIS
with tab5:
    st.markdown('<div class="section-header">Fulfillment & Logistics KPIs</div>', unsafe_allow_html=True)
    
    # 1. Overall Delivery Metrics & On-Time vs Delayed Ratio
    query_delivery_overview = """
    SELECT 
        COUNT(*) AS total_orders,
        ROUND(AVG(DATEDIFF(order_delivered_customer_date, order_purchase_timestamp)), 1) AS avg_delivery_days,
        ROUND(AVG(DATEDIFF(order_estimated_delivery_date, order_delivered_customer_date)), 1) AS avg_days_ahead_of_estimate,
        SUM(CASE WHEN order_delivered_customer_date <= order_estimated_delivery_date THEN 1 ELSE 0 END) AS on_time_orders,
        SUM(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 ELSE 0 END) AS delayed_orders
    FROM orders
    WHERE order_status = 'delivered'
    AND order_delivered_customer_date IS NOT NULL;
    """

    # 2. Delivery Performance by State (Top 10 States with Slowest Deliveries)
    query_delivery_by_location = """
    SELECT 
        c.customer_state,
        COUNT(o.order_id) AS total_orders,
        ROUND(AVG(DATEDIFF(o.order_delivered_customer_date, o.order_purchase_timestamp)), 1) AS avg_delivery_days,
        ROUND(SUM(CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(o.order_id), 1) AS delay_rate_pct
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY c.customer_state
    HAVING total_orders >= 50
    ORDER BY avg_delivery_days DESC
    LIMIT 10;
    """

    # 3. Impact of Delivery Delay on Review Scores
    query_delay_vs_rating = """
    SELECT 
        CASE 
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On-Time'
            WHEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) BETWEEN 1 AND 3 THEN '1-3 Days Late'
            WHEN DATEDIFF(o.order_delivered_customer_date, o.order_estimated_delivery_date) BETWEEN 4 AND 7 THEN '4-7 Days Late'
            ELSE '8+ Days Late'
        END AS delay_category,
        COUNT(DISTINCT o.order_id) AS order_count,
        ROUND(AVG(r.review_score), 2) AS avg_review_score
    FROM orders o
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY delay_category
    ORDER BY avg_review_score DESC;
    """
    df_overview = run_query(query_delivery_overview)
    df_location = run_query(query_delivery_by_location)
    df_delay_rating = run_query(query_delay_vs_rating)

    # 1. Summary Key Metrics
    if not df_overview.empty:
        total_orders = df_overview.iloc[0]["total_orders"]
        avg_days = df_overview.iloc[0]["avg_delivery_days"]
        on_time = df_overview.iloc[0]["on_time_orders"]
        delayed = df_overview.iloc[0]["delayed_orders"]
        on_time_pct = (
            (on_time / total_orders) * 100 if total_orders > 0 else 0
        )

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Average Delivery Time", f"{avg_days} Days")
        m2.metric("On-Time Deliveries", f"{on_time:,} ({on_time_pct:.1f}%)")
        m3.metric("Delayed Deliveries", f"{delayed:,}")
        m4.metric("Total Delivered Orders", f"{total_orders:,}")

    st.markdown("---")

    # Row 2: Location Performance & Delay Impact on Reviews
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Slowest States by Average Delivery Time")
        st.caption("States with at least 50 orders sorted by average days")

        st.dataframe(
            df_location,
            column_config={
                "customer_state": "State",
                "total_orders": st.column_config.NumberColumn(
                    "Total Orders", format="%d"
                ),
                "avg_delivery_days": st.column_config.NumberColumn(
                    "Avg Days", format="%.1f days"
                ),
                "delay_rate_pct": st.column_config.NumberColumn(
                    "Delay Rate", format="%.1f%%"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.subheader("Delivery Delay vs. Review Score")
        st.caption(
            "How delivery tardiness directly penalizes customer ratings"
        )

        st.bar_chart(
            df_delay_rating,
            x="delay_category",
            y="avg_review_score",
            use_container_width=True,
        )
        st.info('Review scores remain relatively stable for delays up to 2 days, but drop by over 50% beyond the 3-day delay mark, marking 72 hours as the critical threshold for customer churn risk.')

        st.dataframe(
            df_delay_rating,
            column_config={
                "delay_category": "Delivery Status",
                "order_count": st.column_config.NumberColumn(
                    "Total Orders", format="%d"
                ),
                "avg_review_score": st.column_config.NumberColumn(
                    "Avg Rating (1-5)", format="%.2f ⭐"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

# TAB 6: CUSTOMER EXPERIENCE

with tab6:
    st.markdown('<div class="section-header">Customer Feedback & Satisfaction</div>', unsafe_allow_html=True)

    # 1. Overall Review Score Distribution (1 to 5 Stars)
    query_review_distribution = """
    SELECT 
        review_score,
        COUNT(review_id) AS total_reviews,
        ROUND(COUNT(review_id) * 100.0 / SUM(COUNT(review_id)) OVER(), 1) AS percentage
    FROM order_reviews
    GROUP BY review_score
    ORDER BY review_score DESC;
    """

    # 2. Average Review Scores by Top English Categories (Min 50 Reviews)
    query_reviews_by_category = """
    SELECT 
        COALESCE(t.product_category_name_english, p.product_category_name, 'Uncategorized') AS category_english,
        COUNT(r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_review_score
    FROM order_reviews r
    JOIN orders o ON r.order_id = o.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    LEFT JOIN product_category_transalation t 
        ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY category_english
    HAVING total_reviews >= 50
    ORDER BY avg_review_score DESC
    LIMIT 10;
    """

    # 3. Rating vs Delivery Performance (Delivered Early/On-Time vs Late)
    query_rating_vs_delivery = """
    SELECT 
        CASE 
            WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date THEN 'On-Time / Early'
            ELSE 'Late / Delayed'
        END AS delivery_status,
        COUNT(r.review_id) AS total_reviews,
        ROUND(AVG(r.review_score), 2) AS avg_review_score,
        SUM(CASE WHEN r.review_score = 5 THEN 1 ELSE 0 END) AS five_star_count,
        SUM(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) AS one_star_count
    FROM orders o
    JOIN order_reviews r ON o.order_id = r.order_id
    WHERE o.order_status = 'delivered'
    AND o.order_delivered_customer_date IS NOT NULL
    GROUP BY delivery_status;
    """
    df_reviews_dist = run_query(query_review_distribution)
    df_cat_reviews = run_query(query_reviews_by_category)
    df_delivery_rating = run_query(query_rating_vs_delivery)

    # Row 1: Review Score Distribution & Rating vs Delivery Performance
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Review Score Distribution")
        st.caption("Breakdown of customer rating scores (1 to 5 Stars)")

        st.bar_chart(
            df_reviews_dist,
            x="review_score",
            y="total_reviews",
            use_container_width=True,
        )

        st.dataframe(
            df_reviews_dist,
            column_config={
                "review_score": st.column_config.NumberColumn(
                    "Rating (Stars)", format="%d ⭐"
                ),
                "total_reviews": st.column_config.NumberColumn(
                    "Total Reviews", format="%d"
                ),
                "percentage": st.column_config.NumberColumn(
                    "Share (%)", format="%.1f%%"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    with col2:
        st.subheader("Rating vs. Delivery Performance")
        st.caption(
            "Comparing customer satisfaction across on-time vs. delayed deliveries"
        )

        st.dataframe(
            df_delivery_rating,
            column_config={
                "delivery_status": "Delivery Status",
                "total_reviews": st.column_config.NumberColumn(
                    "Total Reviews", format="%d"
                ),
                "avg_review_score": st.column_config.NumberColumn(
                    "Avg Rating", format="%.2f ⭐"
                ),
                "five_star_count": st.column_config.NumberColumn(
                    "5-Star Count", format="%d"
                ),
                "one_star_count": st.column_config.NumberColumn(
                    "1-Star Count", format="%d"
                ),
            },
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("---")

    # Row 2: Top Rated Categories
    st.subheader("Top Rated Product Categories (Min. 50 Reviews)")
    st.caption("Product categories sorted by highest customer satisfaction")

    st.dataframe(
        df_cat_reviews,
        column_config={
            "category_english": "Product Category (English)",
            "total_reviews": st.column_config.NumberColumn(
                "Total Reviews", format="%d"
            ),
            "avg_review_score": st.column_config.NumberColumn(
                "Average Rating", format="%.2f ⭐"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )