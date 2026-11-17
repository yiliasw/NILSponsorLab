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
        count = conn.execute('SELECT COUNT(*) FROM BUSINESS').fetchone()[0]
        if count == 0:
            conn.executemany('INSERT INTO BUSINESS VALUES (?, ?, ?, ?)', [
                ('B01','Peachtree Sportswear','Apparel','Atlanta'),
                ('B02','Metro Fitness','Fitness','Decatur'),
                ('B03','Southern Tech Solutions','Technology','Atlanta'),
                ('B04','Campus Café','Food & Beverage','Atlanta'),
                ('B05','Victory Media','Media','Marietta'),
            ])

def load_data():
    with connect() as conn:
        return pd.read_sql_query('SELECT Business_ID, Business_Name, Industry, City FROM BUSINESS ORDER BY Business_Name', conn)

initialize()
st.title('🏅 NIL Sponsor Manager')
st.caption('A classroom demonstration of Streamlit + Python + SQLite. Fictional businesses only.')

data = load_data()
a, b, c = st.columns(3)
a.metric('Businesses', len(data))
b.metric('Industries', data['Industry'].nunique())
c.metric('Cities', data['City'].nunique())

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

st.divider()
st.caption('Teaching note: Streamlit Community Cloud storage is ephemeral; records may reset after restart/redeployment. This demo uses a simplified BUSINESS table, not the full course NIL schema.')
