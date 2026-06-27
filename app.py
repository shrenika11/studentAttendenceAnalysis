import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import datetime

# ----------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# ----------------------------------------------------
st.set_page_config(page_title="College Student Analytics", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #1E3A8A; margin-bottom: 20px; }
    .metric-box { background-color: #F3F4F6; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. MOCK DATA GENERATION ENGINE
# ----------------------------------------------------
@st.cache_data
def generate_student_data():
    np.random.seed(42)
    departments = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil']
    subjects = {
        'Computer Science': ['Java', 'Operating Systems', 'Cybersecurity', 'Data Structures'],
        'Information Technology': ['Web Dev', 'Cloud Computing', 'Database Systems', 'Java'],
        'Electronics': ['Microprocessors', 'Signal Processing', 'VLSI', 'Embedded Systems'],
        'Mechanical': ['Thermodynamics', 'Fluid Mechanics', 'CAD/CAM', 'Kinematics'],
        'Civil': ['Structural Analysis', 'Surveying', 'Geotech', 'Concrete Tech']
    }
    months = ['January', 'February', 'March', 'April', 'May']
    
    data_list = []
    student_id_counter = 1001
    
    for dept in departments:
        for i in range(1, 21): # 20 students per department = 100 students total
            student_name = f"Student {student_id_counter}"
            
            for month in months:
                for sub in subjects[dept]:
                    # Generate a realistic random attendance percentage between 50% and 100%
                    base_attendance = np.random.randint(65, 100)
                    # Introduce some random low-attendance outliers
                    if np.random.rand() < 0.08:
                        base_attendance = np.random.randint(35, 64)
                        
                    data_list.append({
                        "Student ID": student_id_counter,
                        "Student Name": student_name,
                        "Department": dept,
                        "Subject": sub,
                        "Month": month,
                        "Attendance %": base_attendance
                    })
            student_id_counter += 1
            
    return pd.DataFrame(data_list)

df = generate_student_data()

# ----------------------------------------------------
# 3. SIDEBAR NAVIGATION & FILTERS
# ----------------------------------------------------
st.sidebar.title("Navigation & Filters")
page = st.sidebar.radio("Go to:", ["Dashboard Overview", "Student-Wise Analysis", "Raw Data Explorer"])

# Global Filters
selected_dept = st.sidebar.selectbox("Filter by Department:", ["All"] + list(df['Department'].unique()))
selected_month = st.sidebar.selectbox("Filter by Month:", ["All"] + list(df['Month'].unique()))

# Filter the dataframe based on selections
filtered_df = df.copy()
if selected_dept != "All":
    filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
if selected_month != "All":
    filtered_df = filtered_df[filtered_df['Month'] == selected_month]

# ----------------------------------------------------
# 4. PAGE 1: MAIN DASHBOARD OVERVIEW
# ----------------------------------------------------
if page == "Dashboard Overview":
    st.markdown('<div class="main-title">College Attendance Analytics Dashboard</div>', unsafe_allow_html=True)
    
    # KPI Top Metrics Row
    avg_attendance = filtered_df['Attendance %'].mean()
    total_students = filtered_df['Student ID'].nunique()
    defaulters_df = filtered_df.groupby('Student Name')['Attendance %'].mean().reset_index()
    low_attendance_count = len(defaulters_df[defaulters_df['Attendance %'] < 75])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f'<div class="metric-box"><h3>Average Attendance</h3><h2 style="color:#10B981;">{avg_attendance:.2f}%</h2></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-box"><h3>Students Tracked</h3><h2 style="color:#3B82F6;">{total_students}</h2></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-box"><h3>Students below 75%</h3><h2 style="color:#EF4444;">{low_attendance_count}</h2></div>', unsafe_allow_html=True)
        
    st.write("---")
    
    # Visualizations Grid
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("🏫 Department-Wise Average Attendance")
        dept_anal = filtered_df.groupby('Department')['Attendance %'].mean().reset_index()
        fig_dept = px.bar(dept_anal, x='Department', y='Attendance %', 
                          color='Attendance %', color_continuous_scale='Blues',
                          range_y=[0, 100], text_auto='.1f')
        fig_dept.add_hline(y=75, line_dash="dash", line_color="red", annotation_text="75% Criteria")
        st.plotly_chart(fig_dept, use_container_width=True)

    with chart_col2:
        st.subheader("📚 Subject-Wise Average Attendance")
        sub_anal = filtered_df.groupby('Subject')['Attendance %'].mean().reset_index().sort_values(by='Attendance %', ascending=False)
        fig_sub = px.bar(sub_anal, x='Attendance %', y='Subject', orientation='h',
                         color='Attendance %', color_continuous_scale='Viridis', range_x=[0, 100])
        st.plotly_chart(fig_sub, use_container_width=True)

    st.write("---")
    
    # Monthly Attendance Report Section
    st.subheader("📅 Monthly Attendance Trend Report")
    month_order = ['January', 'February', 'March', 'April', 'May']
    monthly_anal = filtered_df.groupby('Month')['Attendance %'].mean().reindex(month_order).reset_index().dropna()
    
    fig_month = px.line(monthly_anal, x='Month', y='Attendance %', markers=True, range_y=[50, 100],
                        title="Overall Attendance Trend Across Semesters")
    st.plotly_chart(fig_month, use_container_width=True)

# ----------------------------------------------------
# 5. PAGE 2: INDIVIDUAL STUDENT ANALYSIS
# ----------------------------------------------------
elif page == "Student-Wise Analysis":
    st.markdown('<div class="main-title">Individual Student Performance Lookup</div>', unsafe_allow_html=True)
    
    # Filter student names dynamically based on selected department
    available_students = filtered_df['Student Name'].unique()
    selected_student = st.selectbox("Select a Student:", available_students)
    
    student_data = filtered_df[filtered_df['Student Name'] == selected_student]
    
    overall_stud_avg = student_data['Attendance %'].mean()
    st.metric(label=f"Overall Attendance for {selected_student}", value=f"{overall_stud_avg:.2f}%")
    
    if overall_stud_avg < 75:
        st.error("⚠️ This student is below the mandatory 75% attendance criteria.")
    else:
        st.success("✅ Attendance criteria fulfilled.")
        
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.subheader("Subject Performance")
        stud_sub = student_data.groupby('Subject')['Attendance %'].mean().reset_index()
        fig_stud_sub = px.bar(stud_sub, x='Subject', y='Attendance %', range_y=[0, 100], text_auto='.0f', color='Attendance %')
        st.plotly_chart(fig_stud_sub, use_container_width=True)
        
    with col_s2:
        st.subheader("Monthly Breakdown")
        stud_month = student_data.groupby('Month')['Attendance %'].mean().reindex(['January', 'February', 'March', 'April', 'May']).reset_index().dropna()
        fig_stud_month = px.line(stud_month, x='Month', y='Attendance %', markers=True, range_y=[0, 100])
        st.plotly_chart(fig_stud_month, use_container_width=True)

# ----------------------------------------------------
# 6. PAGE 3: RAW DATA EXPLORER
# ----------------------------------------------------
elif page == "Raw Data Explorer":
    st.markdown('<div class="main-title">Data Records Engine</div>', unsafe_allow_html=True)
    st.write("Below is the underlying processed transactional database filtered by your sidebar settings.")
    
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download Button for the report
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Attendance Report as CSV",
        data=csv,
        file_name="college_attendance_report.csv",
        mime="text/csv"
    )