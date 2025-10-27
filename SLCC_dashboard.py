import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Page config
st.set_page_config(
    page_title="SLCC 2021 Graduation Dashboard",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    students = pd.read_csv('Students.csv')
    graduation = pd.read_csv('Graduations.csv')
    
    # Date conversions
    graduation['GRADUATION_DATE'] = pd.to_datetime(graduation['GRADUATION_DATE'])
    graduation['GRAD_APPL_DATE'] = pd.to_datetime(graduation['GRAD_APPL_DATE'])
    
    # Merge data
    dashboard_data = graduation.merge(students, on="STUDENT_ID", how='left')
    
    # Create quality columns
    dashboard_data['ILLOGICAL_DATES'] = dashboard_data['GRAD_APPL_DATE'] > dashboard_data['GRADUATION_DATE']
    dashboard_data['BELOW_CREDITS'] = dashboard_data['TOTAL_CREDITS'] < dashboard_data['REQUIRED_HOURS']
    dashboard_data['MISSING_STUDENT_INFO'] = dashboard_data['STUDENT_ID'].isnull()
    dashboard_data['UNKNOWN_DEPARTMENT'] = dashboard_data['DEPARTMENT'] == 'Unknown'
    dashboard_data['UNKNOWN_COLLEGE'] = dashboard_data['COLLEGE'] == 'Unknown'
    dashboard_data['HAS_UNKNOWN_VALUES'] = dashboard_data['UNKNOWN_DEPARTMENT'] | dashboard_data['UNKNOWN_COLLEGE']
    
    # Check for duplicates and unmatched students
    grad_duplicates = graduation[graduation.duplicated(keep=False)]
    grad_duplicate_student_ids = graduation[graduation['STUDENT_ID'].duplicated(keep=False)]
    student_duplicates = students[students.duplicated(keep=False)]
    student_duplicate_ids = students[students['STUDENT_ID'].duplicated(keep=False)]
    
    # Find students in graduation table but not in students table
    unmatched_students = graduation[~graduation['STUDENT_ID'].isin(students['STUDENT_ID'])]
    
    # Add semester
    dashboard_data['SEMESTER'] = dashboard_data['GRADUATION_DATE'].dt.month.apply(
        lambda x: 'Spring 2021' if x == 5 else 'Summer 2021' if x == 8 else 'Other'
    )
    
    return students, graduation, dashboard_data, grad_duplicates, grad_duplicate_student_ids, student_duplicates, student_duplicate_ids, unmatched_students


students, graduation, dashboard_data, grad_duplicates, grad_duplicate_student_ids, student_duplicates, student_duplicate_ids, unmatched_students = load_data()

# Title
st.title("Spring/Summer 2021 Graduation Overview")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")

# Semester filter
semesters = ['All'] + list(dashboard_data['SEMESTER'].dropna().unique())
selected_semester = st.sidebar.selectbox("Select Semester", semesters)

# Filter data
filtered_data = dashboard_data.copy()
if selected_semester != 'All':
    filtered_data = filtered_data[filtered_data['SEMESTER'] == selected_semester]


# Key metrics
col1, col2, col3 = st.columns(3)

with col1:
    total_apps = len(filtered_data)
    st.metric("Total Applications", f"{total_apps:,}")

with col2:
    graduated_count = filtered_data[filtered_data['GRADUATED_IND'] == 'Y'].shape[0]
    graduated_pct = (graduated_count / total_apps * 100)
    st.metric("Graduated", f"{graduated_pct:.2f}%", help=f"{graduated_count:,} students")

with col3:
    not_graduated_count = filtered_data[filtered_data['GRADUATED_IND'] == 'N'].shape[0]
    not_graduated_pct = (not_graduated_count / total_apps * 100)
    st.metric("Not Graduated", f"{not_graduated_pct:.2f}%", help=f"{not_graduated_count:,} students")

st.markdown("---")


# Main analytics 

st.header("Graduation Analytics")

# Degree Types and Top 10 Majors side by side
col1, col2 = st.columns(2)

with col1:
    st.subheader("Degree Types")
    
    # Prepare degree type data
    degree_summary = filtered_data.groupby(['DEGREE_TYPE', 'GRADUATED_IND']).size().reset_index(name='count')
    
    # Create grouped bar chart showing degree types
    fig = px.bar(
        degree_summary,
        x='DEGREE_TYPE',
        y='count',
        color='GRADUATED_IND',
        barmode='group',
        title='Applications by Degree Type and Graduation Status',
        labels={'count': 'Number of Students', 'DEGREE_TYPE': 'Degree Type', 'GRADUATED_IND': 'Graduated'},
        color_discrete_map={'Y': '#1f77b4', 'N': '#ff7f0e'},
        height=400
    )
    fig.update_layout(
        legend=dict(title="Graduated", orientation="h"),
        xaxis={'categoryorder': 'total descending'}
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 10 Majors")
    
    # Get top 10 majors
    top_majors = filtered_data['MAJOR'].value_counts().head(10)
    
    # Get graduation status breakdown for top majors
    major_grad_data = filtered_data[filtered_data['MAJOR'].isin(top_majors.index)].groupby(['MAJOR', 'GRADUATED_IND']).size().reset_index(name='count')
    
    fig = px.bar(
        major_grad_data,
        x='count',
        y='MAJOR',
        color='GRADUATED_IND',
        orientation='h',
        title='Top 10 Majors by Graduation Status',
        labels={'count': 'Number of Students', 'MAJOR': 'Major'},
        color_discrete_map={'Y': '#1f77b4', 'N': '#ff7f0e'},
        height=400
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        legend=dict(title="Graduated", orientation="h")
    )
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Semester Breakdown
st.subheader("Semester Distribution")

col1, col2 = st.columns([2, 1])

with col1:
    semester_grad = filtered_data.groupby(['SEMESTER', 'GRADUATED_IND']).size().reset_index(name='count')
    
    fig = px.bar(
        semester_grad,
        x='SEMESTER',
        y='count',
        color='GRADUATED_IND',
        title='Applications by Semester and Graduation Status',
        labels={'count': 'Number of Students', 'SEMESTER': 'Semester'},
        color_discrete_map={'Y': '#1f77b4', 'N': '#ff7f0e'},
        barmode='group'
    )
    fig.update_layout(legend=dict(title="Graduated"))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    semester_counts = filtered_data['SEMESTER'].value_counts()
    st.dataframe(
        pd.DataFrame({
            'Semester': semester_counts.index,
            'Total': semester_counts.values,
            '% of Total': (semester_counts.values / semester_counts.sum() * 100).round(1)
        }),
        use_container_width=True,
        height=250
    )

st.markdown("---")

# Department and College Overview
st.subheader("Departments & Colleges")

col1, col2 = st.columns(2)

with col1:
    # Top departments
    dept_counts = filtered_data['DEPARTMENT'].value_counts().head(10)
    
    fig = px.bar(
        x=dept_counts.values,
        y=dept_counts.index,
        orientation='h',
        title='Top 10 Departments',
        labels={'x': 'Number of Students', 'y': 'Department'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Top colleges
    college_counts = filtered_data['COLLEGE'].value_counts().head(10)
    
    fig = px.bar(
        x=college_counts.values,
        y=college_counts.index,
        orientation='h',
        title='Top 10 Colleges',
        labels={'x': 'Number of Students', 'y': 'College'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# GPA and Credits 
st.subheader("Academic Performance")

col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        filtered_data,
        x='OVERALL_GPA',
        nbins=30,
        title='GPA Distribution',
        labels={'OVERALL_GPA': 'Overall GPA', 'count': 'Number of Students'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    avg_gpa = filtered_data['OVERALL_GPA'].mean()
    st.metric("Average GPA", f"{avg_gpa:.2f}")

with col2:
    fig = px.histogram(
        filtered_data,
        x='TOTAL_CREDITS',
        nbins=30,
        title='Total Credits Distribution',
        labels={'TOTAL_CREDITS': 'Total Credits', 'count': 'Number of Students'},
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    avg_credits = filtered_data['TOTAL_CREDITS'].mean()
    st.metric("Average Credits", f"{avg_credits:.1f}")

st.markdown("---")


# Data Quality issues section

st.header("Data Quality Issues")

# Issues summary metrics 
col1, col2, col3, col4 = st.columns(4)

with col1:
    illogical_count = filtered_data['ILLOGICAL_DATES'].sum()
    st.metric(
        "Illogical Dates",
        int(illogical_count),
        help="Application date after graduation date"
    )
    if illogical_count > 0:
        with st.expander("View Records"):
            st.dataframe(
                filtered_data[filtered_data['ILLOGICAL_DATES'] == True][
                    ['STUDENT_ID', 'GRAD_APPL_DATE', 'GRADUATION_DATE']
                ],
                use_container_width=True
            )

with col2:
    below_credits_count = filtered_data['BELOW_CREDITS'].sum()
    st.metric(
        "Below Required Credits",
        int(below_credits_count),
        help="Graduated with credits below requirement"
    )
    if below_credits_count > 0:
        with st.expander("View Records"):
            st.dataframe(
                filtered_data[filtered_data['BELOW_CREDITS'] == True][
                    ['STUDENT_ID', 'TOTAL_CREDITS', 'REQUIRED_HOURS', 'GRADUATED_IND']
                ],
                use_container_width=True
            )

with col3:
    missing_count = filtered_data['MISSING_STUDENT_INFO'].sum()
    st.metric(
        "Missing Student Info",
        int(missing_count),
        help="Records with missing student information"
    )
    if missing_count > 0:
        with st.expander("View Records"):
            st.dataframe(
                filtered_data[filtered_data['MISSING_STUDENT_INFO'] == True][
                    ['STUDENT_ID', 'GRADUATION_DATE']
                ],
                use_container_width=True
            )

with col4:
    unknown_count = filtered_data['HAS_UNKNOWN_VALUES'].sum()
    st.metric(
        "Unknown Dept/College",
        int(unknown_count),
        help="Records with 'Unknown' department or college"
    )
    if unknown_count > 0:
        with st.expander("View Records"):
            st.dataframe(
                filtered_data[filtered_data['HAS_UNKNOWN_VALUES'] == True][
                    ['STUDENT_ID', 'MAJOR', 'DEPARTMENT', 'COLLEGE']
                ],
                use_container_width=True
            )

# Issue summary metrics 2
st.markdown("###")
col1, col2, col3 = st.columns(3)

with col1:
    total_duplicates = len(grad_duplicate_student_ids) + len(student_duplicate_ids)
    st.metric(
        "Duplicate Student IDs",
        int(total_duplicates),
        help="Student IDs that appear multiple times across both tables"
    )
    if total_duplicates > 0:
        with st.expander("View Summary"):
            st.write(f"**Graduation Table:** {len(grad_duplicate_student_ids)} duplicate IDs")
            st.write(f"**Student Table:** {len(student_duplicate_ids)} duplicate IDs")

with col2:
    st.metric(
        "Unmatched Students",
        len(unmatched_students),
        help="Students in graduation table without student records"
    )
    if len(unmatched_students) > 0:
        with st.expander("View Records"):
            st.dataframe(
                unmatched_students[['STUDENT_ID', 'GRADUATION_DATE', 'DEGREE_TYPE', 'MAJOR']].head(10),
                use_container_width=True
            )

with col3:
    total_grad_dup_rows = len(grad_duplicates)
    total_student_dup_rows = len(student_duplicates)
    total_dup_rows = total_grad_dup_rows + total_student_dup_rows
    st.metric(
        "Duplicate Rows",
        int(total_dup_rows),
        help="Completely identical rows across both tables"
    )
    if total_dup_rows > 0:
        with st.expander("View Summary"):
            st.write(f"**Graduation Table:** {total_grad_dup_rows} duplicate rows")
            st.write(f"**Student Table:** {total_student_dup_rows} duplicate rows")

st.markdown("---")

# Breakdown of unknown values
st.subheader("Unknown Values Breakdown")

col1, col2 = st.columns(2)

with col1:
    unknown_dept_count = filtered_data['UNKNOWN_DEPARTMENT'].sum()
    unknown_dept_pct = (unknown_dept_count/len(filtered_data)*100)
    
    st.metric(
        "Unknown Department",
        int(unknown_dept_count),
        help=f"{unknown_dept_pct:.1f}% of records"
    )
    
    # Show majors with unknown departments
    if unknown_dept_count > 0:
        unknown_dept_majors = filtered_data[filtered_data['UNKNOWN_DEPARTMENT'] == True]['MAJOR'].value_counts()
        st.write("**Top Majors with Unknown Department:**")
        st.dataframe(
            pd.DataFrame({
                'Major': unknown_dept_majors.head(10).index,
                'Count': unknown_dept_majors.head(10).values
            }),
            use_container_width=True
        )

with col2:
    unknown_college_count = filtered_data['UNKNOWN_COLLEGE'].sum()
    unknown_college_pct = (unknown_college_count/len(filtered_data)*100)
    
    st.metric(
        "Unknown College",
        int(unknown_college_count),
        help=f"{unknown_college_pct:.1f}% of records"
    )
    
    # Show majors with unknown colleges
    if unknown_college_count > 0:
        unknown_college_majors = filtered_data[filtered_data['UNKNOWN_COLLEGE'] == True]['MAJOR'].value_counts()
        st.write("**Top Majors with Unknown College:**")
        st.dataframe(
            pd.DataFrame({
                'Major': unknown_college_majors.head(10).index,
                'Count': unknown_college_majors.head(10).values
            }),
            use_container_width=True
        )

# Visualization of Unknown values by Major
if unknown_count > 0:
    st.write("**Unknown Values Distribution by Major**")
    unknown_data = filtered_data[filtered_data['HAS_UNKNOWN_VALUES'] == True]
    major_unknown_counts = unknown_data.groupby('MAJOR').size().sort_values(ascending=False).head(15)
    
    fig = px.bar(
        x=major_unknown_counts.values,
        y=major_unknown_counts.index,
        orientation='h',
        title='Top 15 Majors with Unknown Department/College',
        labels={'x': 'Number of Records', 'y': 'Major'},
        color_discrete_sequence=['#ff7f0e']
    )
    fig.update_layout(height=500, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Missing Values Analysis
st.header("Missing Values Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Graduation Dataset")
    grad_nulls = graduation.isnull().sum()
    grad_nulls_df = pd.DataFrame({
        'Column': grad_nulls.index,
        'Missing Count': grad_nulls.values,
        'Missing %': (grad_nulls.values / len(graduation) * 100).round(2)
    })
    grad_nulls_df = grad_nulls_df[grad_nulls_df['Missing Count'] > 0]
    
    if len(grad_nulls_df) > 0:
        st.dataframe(grad_nulls_df, use_container_width=True)
    else:
        st.success("No missing values in graduation dataset!")

with col2:
    st.subheader("Student Dataset")
    student_nulls = students.isnull().sum()
    student_nulls_df = pd.DataFrame({
        'Column': student_nulls.index,
        'Missing Count': student_nulls.values,
        'Missing %': (student_nulls.values / len(students) * 100).round(2)
    })
    student_nulls_df = student_nulls_df[student_nulls_df['Missing Count'] > 0]
    
    if len(student_nulls_df) > 0:
        st.dataframe(student_nulls_df, use_container_width=True)
    else:
        st.success("No missing values in student dataset!")

st.markdown("---")

# Duplicates and Data Integrity
st.header("Duplicates & Data Integrity")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Duplicate Records")
    
    # Graduation table duplicates
    st.write("**Graduation Table:**")
    dup_col1, dup_col2 = st.columns(2)
    
    with dup_col1:
        st.metric(
            "Duplicate Rows",
            len(grad_duplicates),
            help="Completely duplicate records (all columns identical)"
        )
        if len(grad_duplicates) > 0:
            with st.expander("View Duplicate Rows"):
                st.dataframe(
                    grad_duplicates.sort_values('STUDENT_ID'),
                    use_container_width=True
                )
    
    with dup_col2:
        st.metric(
            "Duplicate Student IDs",
            len(grad_duplicate_student_ids),
            help="Records with duplicate Student IDs (may have different data)"
        )
        if len(grad_duplicate_student_ids) > 0:
            with st.expander("View Duplicate Student IDs"):
                st.dataframe(
                    grad_duplicate_student_ids.sort_values('STUDENT_ID')[['STUDENT_ID', 'GRADUATION_DATE', 'DEGREE_TYPE', 'MAJOR']],
                    use_container_width=True
                )
    
    # Student table duplicates
    st.write("**Student Table:**")
    stu_col1, stu_col2 = st.columns(2)
    
    with stu_col1:
        st.metric(
            "Duplicate Rows",
            len(student_duplicates),
            help="Completely duplicate records (all columns identical)"
        )
        if len(student_duplicates) > 0:
            with st.expander("View Duplicate Rows"):
                st.dataframe(
                    student_duplicates.sort_values('STUDENT_ID'),
                    use_container_width=True
                )
    
    with stu_col2:
        st.metric(
            "Duplicate Student IDs",
            len(student_duplicate_ids),
            help="Records with duplicate Student IDs"
        )
        if len(student_duplicate_ids) > 0:
            with st.expander("View Duplicate Student IDs"):
                st.dataframe(
                    student_duplicate_ids.sort_values('STUDENT_ID'),
                    use_container_width=True
                )

with col2:
    st.subheader("Unmatched Student IDs")
    
    unmatched_count = len(unmatched_students)
    unmatched_pct = (unmatched_count / len(graduation) * 100) if len(graduation) > 0 else 0
    
    st.metric(
        "Students in Graduation but not in Students Table",
        unmatched_count,
        help=f"{unmatched_pct:.1f}% of graduation records"
    )
    
        
    with st.expander("View Unmatched Students"):
        st.dataframe(
            unmatched_students[['STUDENT_ID', 'GRADUATION_DATE', 'DEGREE_TYPE', 'MAJOR', 'GRADUATED_IND']],
            use_container_width=True
        )
        
        # Show breakdown by graduation status
        if unmatched_count > 0:
            st.write("**Breakdown by Graduation Status:**")
            unmatched_breakdown = unmatched_students['GRADUATED_IND'].value_counts()
            breakdown_df = pd.DataFrame({
                'Status': unmatched_breakdown.index.map({'Y': 'Graduated', 'N': 'Not Graduated'}),
                'Count': unmatched_breakdown.values
            })
            st.dataframe(breakdown_df, use_container_width=True)
            
        # Visualization
        fig = px.pie(
            breakdown_df,
            values='Count',
            names='Status',
            title='Unmatched Students by Graduation Status',
            color='Status',
            color_discrete_map={'Graduated': '#1f77b4', 'Not Graduated': '#ff7f0e'}
        )
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# Data Explorer
st.header("Data Explorer")

tab1, tab2, tab3 = st.tabs(["Dashboard Data", "Graduation Data", "Student Data"])

with tab1:
    st.subheader("Full Dashboard Data")
    st.dataframe(filtered_data, use_container_width=True)
    
    # Download button
    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Dashboard Data as CSV",
        data=csv,
        file_name='dashboard_data.csv',
        mime='text/csv',
    )

with tab2:
    st.subheader("Graduation Records")
    st.dataframe(graduation, use_container_width=True)

with tab3:
    st.subheader("Student Records")
    st.dataframe(students, use_container_width=True)
    
# Recommendations

st.header("Recommendations")

st.write("- Implement validation rules to prevent future date errors and credit requirement issues")
st.write("- Perform an audit of the graduation and student systems to determine why student IDs aren't matching")
st.write("- Create an automated data pipeline that standardizes dates to proper datatype, removes duplicates, and resolves null values before entering the system")