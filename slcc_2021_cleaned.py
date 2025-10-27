import marimo

__generated_with = "0.17.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    return mo, pd


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # SLCC 2021 Graduation Data Analysis

    This notebook documents the data quality analysis performed on SLCC graduation data before building the dashboard.

    ## Overview
    - **Data Sources**: Students.csv and Graduations.csv
    - **Purpose**: Validate data quality and prepare for dashboard creation
    - **Key Checks**: Missing values, data consistency, logical validation
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 1. Data Loading""")
    return


@app.cell
def _(pd):
    students = pd.read_csv('Students.csv')
    graduation = pd.read_csv('Graduations.csv')
    return graduation, students


@app.cell
def _(graduation, students):
    print(f"Graduation records: {len(graduation)}")
    print(f"Student records: {len(students)}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 2. Initial Data Exploration""")
    return


@app.cell
def _(graduation):
    graduation.head(20)
    return


@app.cell
def _(graduation):
    graduation.dtypes
    return


app._unparsable_cell(
    r"""
     students.head(20)
    """,
    name="_"
)


@app.cell
def _(students):
    students.dtypes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 3. Data Quality Checks""")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 3.1 Missing Values""")
    return


@app.cell
def _(graduation):
    graduation.isnull().sum()
    return


@app.cell
def _(students):
    students.isnull().sum()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 3.2 Unique Values Analysis""")
    return


@app.function
# Function to display unique values for each column
def unique_lister(df):
    for column in df.columns:
        print(f'{column}: {df[column].unique()}')


@app.cell
def _(graduation):
    unique_lister(graduation)
    return


@app.cell
def _(students):
    unique_lister(students)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 3.3 Data Consistency Checks""")
    return


@app.cell
def _(graduation, students):
    # Check for unmatched student IDs between datasets
    unmatched = graduation[~graduation['STUDENT_ID'].isin(students['STUDENT_ID'])]
    print(f"Unmatched students: {len(unmatched)}")
    unmatched
    return (unmatched,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 4. Data Validation & Business Logic

    """
    )
    return


@app.cell
def _(graduation, pd):
    # Convert date columns to datetime
    graduation['GRADUATION_DATE'] = pd.to_datetime(graduation['GRADUATION_DATE'])
    graduation['GRAD_APPL_DATE'] = pd.to_datetime(graduation['GRAD_APPL_DATE'])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 4.1 Date Logic Validation""")
    return


@app.cell
def _(graduation):
    # Identify records where application date is after graduation date
    grad_date_issues = graduation[graduation['GRAD_APPL_DATE'] > graduation['GRADUATION_DATE']]
    print(f"Illogical date records: {len(grad_date_issues)}")
    grad_date_issues
    return (grad_date_issues,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 4.2 Credit Requirements Validation""")
    return


@app.cell
def _(graduation):
    # Check for students who graduated despite not meeting credit requirements
    below_credits_but_graduated = graduation[
        (graduation['TOTAL_CREDITS'] < graduation['REQUIRED_HOURS']) & 
        (graduation['GRADUATED_IND'] == 'Y')
    ]
    print(f"Below credits but graduated: {len(below_credits_but_graduated)}")
    below_credits_but_graduated
    return (below_credits_but_graduated,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 4.3 GPA Validation""")
    return


@app.cell
def _(graduation):
    # Check for invalid GPA values (> 4.0)
    invalid_gpa_count = (graduation['OVERALL_GPA'] > 4).sum() | (graduation['OVERALL_GPA'] < 0).sum()
    print(f"Records with GPA > 4.0 or GPA < 0: {invalid_gpa_count}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### 4.4 Duplicate Check""")
    return


@app.cell
def _(graduation):
    print(f"Duplicate records: {graduation.duplicated().sum()}")
    print(f"Duplicate student IDs: {graduation['STUDENT_ID'].duplicated().sum()}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 5.Creating New Fields""")
    return


@app.cell
def _(graduation):
    # Create semester labels based on graduation month
    graduation['SEMESTER'] = graduation['GRADUATION_DATE'].dt.month.apply(
        lambda x: 'Spring 2021' if x == 5 else 'Summer 2021' if x == 8 else 'Other'
    )
    return


@app.cell
def _(graduation):
    graduation['SEMESTER'].value_counts()
    return


@app.cell
def _(graduation):
    # Check for unexpected graduation dates
    graduation[graduation['SEMESTER'] == 'Other']
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 6. Dashboard Data Preparation""")
    return


@app.cell
def _(graduation, students):
    # Merge graduation and student data for dashboard
    dashboard_data = graduation.merge(students, on="STUDENT_ID", how='left')
    return (dashboard_data,)


@app.cell
def _(dashboard_data):
    # Create quality indicator flags
    dashboard_data['ILLOGICAL_DATES'] = dashboard_data['GRAD_APPL_DATE'] > dashboard_data['GRADUATION_DATE']
    dashboard_data['BELOW_CREDITS'] = dashboard_data['TOTAL_CREDITS'] < dashboard_data['REQUIRED_HOURS']
    dashboard_data['MISSING'] = dashboard_data['STUDENT_ID'].isnull()
    return


@app.cell
def _(dashboard_data):
    dashboard_data.columns
    return


@app.cell
def _(dashboard_data):
    dashboard_data.dtypes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## 7. Export Quality Summary""")
    return


@app.cell
def _(
    below_credits_but_graduated,
    grad_date_issues,
    graduation,
    pd,
    unmatched,
):
    # Create summary table of data quality issues
    quality_summary = pd.DataFrame({
        'Issue Type': [
            'Illogical Dates', 
            'Unmatched Students', 
            'Below Required Credits', 
            'Missing Student IDs'
        ],
        'Record Count': [
            len(grad_date_issues),
            len(unmatched),
            len(below_credits_but_graduated),
            graduation['STUDENT_ID'].isnull().sum()
        ]
    })

    quality_summary.to_csv('quality_issues_summary.csv', index=False)
    quality_summary
    return


@app.cell
def _(dashboard_data):
    # Export cleaned dashboard data
    dashboard_data.to_csv('dashboard_data.csv', index=False)
    print(f"Dashboard data exported: {len(dashboard_data)} records")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Summary

    This analysis identified several data quality issues:

    - Date inconsistencies (application after graduation)
    - Students graduating below credit requirements
    - Unmatched student records between datasets
    """
    )
    return


@app.cell(hide_code=True)
def _():
    return


@app.cell
def _(graduation):
    graduation[graduation['SEMESTER'] == 'Other']['GRADUATION_DATE'].unique()
    return


@app.cell
def _(graduation):
    graduation[(graduation['GRADUATED_IND'] == 'N') & (graduation['GRAD_APPL_DATE'] > graduation['GRADUATION_DATE'])]
    return


@app.cell
def _(graduation):
    graduation[(graduation['GRADUATED_IND'] == 'Y') & (graduation['GRAD_APPL_DATE'] > graduation['GRADUATION_DATE'])]
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
