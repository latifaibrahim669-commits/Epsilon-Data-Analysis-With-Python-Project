%%writefile app.py
import streamlit as st
import pandas as pd
import plotly.express as px
# 1. Page Configuration
st.set_page_config(
    page_title="Riyadh Cardiorespiratory Dashboard",
    page_icon="🏥",
    layout="wide"
)
st.markdown("<h1 style='text-align: center; color: white;'>This is a centered Text by HTML</h1>", unsafe_allow_html= True)

st.title("Riyadh Cardiorespiratory Dashboard")

# 2. Custom CSS to style the Sidebar with the Ministry of Health Green Color
st.markdown("""
    <style>
        /* تلوين الشريط الجانبي باللون الأخضر المستوحى من الشعار */
        [data-testid="stSidebar"] {
            background-color: #038C4C;
        }
        
        /* جعل جميع النصوص والعناوين داخل الشريط الجانبي باللون الأبيض لضمان الوضوح */
        [data-testid="stSidebar"] h1, 
        [data-testid="stSidebar"] h2, 
        [data-testid="stSidebar"] h3, 
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] span {
            color: #FFFFFF !important;
        }
        
        /* تعديل ألوان عناصر الإدخال والفلاتر لتناسب الخلفية الخضراء */
        [data-testid="stSidebar"] .stMultiSelect div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Official Color Palette & Variables
PRIMARY_GREEN = "#038C4C"
GOLD_ACCENT = "#A69563"
LIGHT_GREEN = "#49A684"

CONDITION_COLORS = {
    'Asthma': '#49A684',
    'COPD': '#A69563',
    'Heart Attack': '#038C4C',
    'Other Respiratory Issues': '#3366CC'
}

# 4. Load and preprocess data
@st.cache_data
def load_data():
    file_path = r"C:\Users\Latif\Desktop\Epsilon Data Analysis With Python Project\Cleaned Riyadh Cardiorespiratory Hospital Admissions.csv"
    df = pd.read_csv(file_path)
    df['admission_date'] = pd.to_datetime(df['admission_date'])
    df['daily_medication_dosage'] = df['daily_medication_dosage'].round(2)
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset file or incorrect path. Details: {e}")
    st.stop()
# 5. Sidebar Navigation, Logo, and Global Filters
 
st.image("d391a6caec964af6.jpeg", use_container_width=True)
st.sidebar.image("MOH-1.png", use_container_width=True)
st.sidebar.title( "Dashboard Navigation")

page = st.sidebar.radio("Select Page:", [
    "📊 Overview & KPIs", 
    "📈 Temporal & Seasonal Analysis", 
    "🏥 Hospital & Emergency Analysis", 
    "👥 Patient Demographics & Severity",
    "🔍 Outliers Analysis"
])

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Global Data Filters")

all_hospitals = df['hospital_name'].unique()
selected_hospital = st.sidebar.multiselect("Select Hospital:", options=all_hospitals, default=all_hospitals)

all_conditions = df['condition_type'].unique()
selected_condition = st.sidebar.multiselect("Select Condition Type:", options=all_conditions, default=all_conditions)

filtered_df = df[
    (df['hospital_name'].isin(selected_hospital)) & 
    (df['condition_type'].isin(selected_condition))
]

if filtered_df.empty:
    st.warning("⚠️ No data matches the current filter selection. Please adjust the filters in the sidebar.")
    st.stop()

# ==========================================
# Page 1: Overview & KPIs
# ==========================================
if page == "📊 Overview & KPIs":
    st.markdown(f"<h1 style='color: {PRIMARY_GREEN};'>📊 Overview & Key Performance Indicators</h1>", unsafe_allow_html=True)
    st.markdown("An interactive dashboard summarizing cardiorespiratory hospital admissions in Riyadh.")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Admissions", f"{filtered_df['admission_count'].sum():,}")
    col2.metric("Avg Length of Stay (Days)", f"{filtered_df['length_of_stay_avg'].mean():.1f}")
    col3.metric("Total Readmissions", f"{filtered_df['readmission_count'].sum():,}")
    col4.metric("Active Hospitals", len(filtered_df['hospital_name'].unique()))
    
    st.markdown("---")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(
            filtered_df, names='condition_type', values='admission_count', 
            title="Admissions Distribution by Condition Type", hole=0.4,
            color='condition_type', color_discrete_map=CONDITION_COLORS
        )
        fig_pie.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        hosp_grouped = filtered_df.groupby('hospital_name')['admission_count'].sum().reset_index()
        fig_bar = px.bar(
            hosp_grouped, x='hospital_name', y='admission_count', 
            title="Total Admissions per Hospital", color='hospital_name', text_auto=True,
            color_discrete_sequence=[PRIMARY_GREEN, LIGHT_GREEN, GOLD_ACCENT]
        )
        fig_bar.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_bar, use_container_width=True)

# ==========================================
# Page 2: Temporal & Seasonal Analysis
# ==========================================
elif page == "📈 Temporal & Seasonal Analysis":
    st.markdown(f"<h1 style='color: {PRIMARY_GREEN};'>📈 Temporal & Seasonal Admissions Analysis</h1>", unsafe_allow_html=True)
    st.markdown("Track hospital admission trends across years, months, hours, and seasons.")
    
    if 'Year' not in filtered_df.columns:
        filtered_df['Year'] = filtered_df['admission_date'].dt.year
    yearly_trend = filtered_df.groupby('Year')[['admission_count', 'emergency_visit_count']].sum().reset_index()
    
    fig_pattern = px.line(
        yearly_trend, x='Year', y=['admission_count', 'emergency_visit_count'], 
        color_discrete_sequence=[PRIMARY_GREEN, GOLD_ACCENT], markers=True,
        title="Yearly Trend of Admissions and Emergency Visits"
    )
    fig_pattern.update_layout(xaxis=dict(tickmode='linear', dtick=1), plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_pattern, use_container_width=True)
    
    if 'seasonal_indicator' in filtered_df.columns:
        fig_season = px.bar(
            filtered_df, x='seasonal_indicator', y='admission_count', color='condition_type',
            barmode='group', title="Respiratory & Cardiovascular Admissions Across Seasons",
            color_discrete_map=CONDITION_COLORS
        )
        fig_season.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_season, use_container_width=True)
    
    c1, c2 = st.columns(2)
    with c1:
        filtered_df['Month'] = filtered_df['admission_date'].dt.month_name()
        monthly_pattern = filtered_df.groupby('Month')['admission_count'].mean().reset_index()
        fig_month = px.line(
            monthly_pattern, x='Month', y='admission_count', 
            title="Admission Monthly Pattern (Average)", color_discrete_sequence=[GOLD_ACCENT], markers=True
        )
        fig_month.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_month, use_container_width=True)
        
    with c2:
        if 'admission_hour' in filtered_df.columns:
            hourly_pattern = filtered_df.groupby('admission_hour')['admission_count'].mean().reset_index()
            fig_hour = px.line(
                hourly_pattern, x='admission_hour', y='admission_count', 
                title="Admission Hourly Pattern (Average)", color_discrete_sequence=[GOLD_ACCENT], markers=True
            )
            fig_hour.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_hour, use_container_width=True)

# ==========================================
# Page 3: Hospital & Emergency Analysis
# ==========================================
elif page == "🏥 Hospital & Emergency Analysis":
    st.markdown(f"<h1 style='color: {PRIMARY_GREEN};'>🏥 Hospital Performance & Emergency Visits</h1>", unsafe_allow_html=True)
    st.markdown("Detailed comparison of admissions, emergency visits, and length of stay across hospitals.")
    
    hospital_summary = filtered_df.groupby('hospital_name')[['admission_count', 'emergency_visit_count', 'length_of_stay_avg']].mean().reset_index()
    
    fig_hosp = px.bar(
        hospital_summary, x='hospital_name', y=['admission_count', 'emergency_visit_count'],
        barmode='group', color_discrete_sequence=[PRIMARY_GREEN, GOLD_ACCENT],
        title="Total Admissions and Emergency Visits by Hospital"
    )
    fig_hosp.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_hosp, use_container_width=True)
    
    fig_hosp_len = px.bar(
        hospital_summary, x='hospital_name', y='length_of_stay_avg',
        color_discrete_sequence=[LIGHT_GREEN],
        title="Average Length of Admission Days by Hospital"
    )
    fig_hosp_len.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_hosp_len, use_container_width=True)

# ==========================================
# Page 4: Patient Demographics & Severity
# ==========================================
elif page == "👥 Patient Demographics & Severity":
    st.markdown(f"<h1 style='color: {PRIMARY_GREEN};'>👥 Patient Demographics & Epidemiological Insights</h1>", unsafe_allow_html=True)
    st.markdown("Explore patient age groups, gender breakdowns, and condition severity levels.")
    
    if 'patient_age_group' in filtered_df.columns and 'severity_level' in filtered_df.columns:
        fig_severity = px.bar(
            filtered_df, x='patient_age_group', y='admission_count', color='severity_level',
            facet_col='condition_type', facet_row='patient_gender', barmode='group',
            title="Admissions by Age Group, Severity, Condition Type, and Gender",
            color_discrete_sequence=[PRIMARY_GREEN, GOLD_ACCENT, LIGHT_GREEN]
        )
        fig_severity.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_severity, use_container_width=True)
    else:
        c1, c2 = st.columns(2)
        with c1:
            fig_age = px.histogram(filtered_df, x='age', nbins=20, title="Patient Age Distribution", color_discrete_sequence=[PRIMARY_GREEN])
            fig_age.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_age, use_container_width=True)
        with c2:
            fig_dose = px.box(filtered_df, x='condition_type', y='daily_medication_dosage', title="Medication Dosage by Condition", color='condition_type', color_discrete_map=CONDITION_COLORS)
            fig_dose.update_layout(plot_bgcolor='white', paper_bgcolor='white')
            st.plotly_chart(fig_dose, use_container_width=True)

# ==========================================
# Page 5: Outliers Analysis
# ==========================================
elif page == "🔍 Outliers Analysis":
    st.markdown(f"<h1 style='color: {PRIMARY_GREEN};'>🔍 Outliers Analysis</h1>", unsafe_allow_html=True)
    st.markdown("Identify extreme values and outliers in admissions, readmissions, and length of stay variables.")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_box1 = px.box(
            filtered_df, y="admission_count", 
            title="Outliers Check: Admission Count", color_discrete_sequence=[LIGHT_GREEN]
        )
        fig_box1.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_box1, use_container_width=True)
        
    with c2:
        fig_box2 = px.box(
            filtered_df, y="readmission_count", 
            title="Outliers Check: Readmission Count", color_discrete_sequence=[LIGHT_GREEN]
        )
        fig_box2.update_layout(plot_bgcolor='white', paper_bgcolor='white')
        st.plotly_chart(fig_box2, use_container_width=True)
        
    fig_box3 = px.box(
        filtered_df, x="hospital_name", y="length_of_stay_avg", color="hospital_name",
        title="Average Length of Stay Distribution per Hospital and Outlier Detection",
        color_discrete_sequence=[PRIMARY_GREEN, GOLD_ACCENT, LIGHT_GREEN]
    )
    fig_box3.update_layout(plot_bgcolor='white', paper_bgcolor='white')
    st.plotly_chart(fig_box3, use_container_width=True)
