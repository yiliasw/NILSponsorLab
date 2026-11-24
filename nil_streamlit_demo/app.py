import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='NIL Sponsor Manager', page_icon='🏅', layout='wide')
DB = Path(__file__).with_name('nil_demo.db')

def connect():
    conn = sqlite3.connect(DB)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def initialize():
    with connect() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS BUSINESS (
            Business_ID TEXT PRIMARY KEY,
            Business_Name TEXT NOT NULL,
            Industry TEXT NOT NULL,
            City TEXT NOT NULL
        )''')

        conn.execute('''CREATE TABLE IF NOT EXISTS NIL_AGREEMENT (
            Agreement_ID TEXT PRIMARY KEY,
            Business_ID TEXT NOT NULL,
            Athlete_Name TEXT NOT NULL,
            Compensation_Amount REAL NOT NULL,
            FOREIGN KEY (Business_ID) REFERENCES BUSINESS(Business_ID)
        )''')

        count = conn.execute('SELECT COUNT(*) FROM BUSINESS').fetchone()[0]
        if count == 0:
            conn.executemany('INSERT INTO BUSINESS VALUES (?, ?, ?, ?)', [
                ('B01','Peachtree Sportswear','Apparel','Atlanta'),
                ('B02','Metro Fitness','Fitness','Decatur'),
                ('B03','Southern Tech Solutions','Technology','Atlanta'),
                ('B04','Campus Café','Food & Beverage','Atlanta'),
                ('B05','Victory Media','Media','Marietta'),
            ])

        agreement_count = conn.execute(
        'SELECT COUNT(*) FROM NIL_AGREEMENT').fetchone()[0]
        if agreement_count == 0:
            conn.executemany(
            'INSERT INTO NIL_AGREEMENT VALUES (?, ?, ?, ?)',
            [('A01', 'B01', 'Jordan Lee', 1200.00),
            ('A02', 'B02', 'Taylor Green', 850.00),
            ('A03', 'B01', 'Morgan Hill', 500.00)]
            )

def load_data():
    with connect() as conn:
        return pd.read_sql_query('SELECT Business_ID, Business_Name, Industry, City FROM BUSINESS ORDER BY City, Business_Name', conn)

initialize()
st.title('College NIL Business Directory')
st.caption('A classroom demonstration of Streamlit + Python + SQLite. Fictional businesses only.')

data = load_data()
a, b, c = st.columns(3)
a.metric('Businesses', len(data))
b.metric('Industries', data['Industry'].nunique())
c.metric('Cities', data['City'].nunique())
st.sidebar.title("Navigation")
menu = st.sidebar.radio(
    "Select an option",
    ["Home", "Business Directory", "NIL Agreements", "Reports"]
)

if menu == "Home":
    st.header("Welcome")
    st.write("Welcome to the NIL Sponsor Manager. This is a simple directory of information on the active NIL sponsor deals. choose business directory to search, add, sort, and delte businesses. choose NIL agreements to look at specific agreements and the total compensation amount.")
elif menu == "Business Directory":
    st.header("Business Directory")
    conn = connect()
    industries = pd.read_sql_query(
        "SELECT DISTINCT Industry FROM BUSINESS ORDER BY Industry",
        conn
    )
    choice = st.selectbox(
        "Select an industry",
        ["All Industries"] + industries["Industry"].tolist()
    )
    if choice == "All Industries":
        query = """
            SELECT Business_Name, Industry, City FROM BUSINESS
            ORDER BY City, Business_Name
        """
        df = pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT Business_Name, Industry, City FROM BUSINESS
            WHERE Industry = ? ORDER BY City, Business_Name
        """
        df = pd.read_sql_query(query, conn, params=(choice,))
    st.dataframe(df)
    st.write("Number of businesses:", len(df))
    conn.close()


    tab1, tab2, tab3 = st.tabs(['📋 Directory', '➕ Add Business', '✏️ Edit / Delete'])
    with tab1:
        query = st.text_input('Search by name, industry, or city')
        shown = data[data.astype(str).apply(lambda s: s.str.contains(query, case=False, regex=False)).any(axis=1)] if query else data
        st.dataframe(shown, use_container_width=True, hide_index=True)
        st.subheader('Businesses by industry')
        st.bar_chart(data['Industry'].value_counts())
    with tab2:
        with st.form('add_business', clear_on_submit=True):
            business_id = st.text_input('Business ID (e.g., B06)')
            business_name = st.text_input('Business name')
            industry = st.text_input('Industry')
            city = st.text_input('City')
            submitted = st.form_submit_button('Add business', type='primary')
        if submitted:
            vals = [v.strip() for v in (business_id, business_name, industry, city)]
            if not all(vals):
                st.error('All four fields are required.')
            else:
                try:
                    with connect() as conn:
                        conn.execute('INSERT INTO BUSINESS VALUES (?, ?, ?, ?)', vals)
                    st.success('Business added. Open Directory to view it.')
                except sqlite3.IntegrityError:
                    st.error('That Business ID already exists. Choose another.')
    with tab3:
        ids = data['Business_ID'].tolist()
        selected = st.selectbox('Choose a business', ids, format_func=lambda x: f"{x} — {data.loc[data.Business_ID == x, 'Business_Name'].iloc[0]}")
        current = data[data.Business_ID == selected].iloc[0]
        with st.form('edit_business'):
            new_name = st.text_input('Business name', value=current.Business_Name)
            new_industry = st.text_input('Industry', value=current.Industry)
            new_city = st.text_input('City', value=current.City)
            update = st.form_submit_button('Save changes')
        if update:
            if not all(x.strip() for x in (new_name, new_industry, new_city)):
                st.error('Fields cannot be blank.')
            else:
                with connect() as conn:
                    conn.execute('UPDATE BUSINESS SET Business_Name=?, Industry=?, City=? WHERE Business_ID=?',
                                 (new_name.strip(), new_industry.strip(), new_city.strip(), selected))
                st.success('Updated successfully.')
                st.rerun()
        st.warning('Deleting a business is permanent in this local demo.')
        confirm = st.checkbox('I understand and want to delete the selected business')
        if st.button('Delete selected business', disabled=not confirm):
            with connect() as conn:
                conn.execute('DELETE FROM BUSINESS WHERE Business_ID=?', (selected,))
            st.success('Deleted.')
            st.rerun()
elif menu == "NIL Agreements":
    st.header("NIL Agreements")
    conn = connect()
    query = """
        SELECT B.Business_Name, N.Athlete_Name,
               N.Compensation_Amount
        FROM BUSINESS AS B
        INNER JOIN NIL_AGREEMENT AS N
            ON B.Business_ID = N.Business_ID
        ORDER BY B.Business_Name
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    st.dataframe(df, use_container_width=True, hide_index=True)
    st.metric(
    "Total Compensation",
    f"${df['Compensation_Amount'].sum():,.2f}"
    )

elif menu == "Reports":
    st.header("Business Summary Report")
    conn = connect()
    query = """
        SELECT B.Business_Name,
               COUNT(N.Agreement_ID) AS Agreement_Count,
               TOTAL (N.Compensation_Amount)
                   AS Total_Compensation
        FROM BUSINESS AS B
        LEFT JOIN NIL_AGREEMENT AS N
            ON B.Business_ID = N.Business_ID
        GROUP BY B.Business_ID, B.Business_Name
        ORDER BY Total_Compensation DESC
    """
    df = pd.read_sql_query(query, conn)
    st.dataframe(df)
    st.subheader("Total Compensation by Business")
    st.bar_chart(df.set_index("Business_Name")["Total_Compensation"])
    st.subheader("Agreements per Business")
    st.bar_chart(df.set_index("Business_Name")["Agreement_Count"])
    conn.close()


st.divider()
st.caption('Teaching note: Streamlit Community Cloud storage is ephemeral; records may reset after restart/redeployment. This demo uses a simplified BUSINESS table, not the full course NIL schema.')
