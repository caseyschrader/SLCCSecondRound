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


@app.cell
def _(pd):
    students = pd.read_csv('Students.csv')
    graduation = pd.read_csv('Graduations.csv')
    return graduation, students


@app.cell
def _(graduation, students):
    merged = graduation.merge(
        students,
        on='STUDENT_ID',
        how='left',
        indicator=True
    )
    return (merged,)


@app.cell
def _(mo):
    mo.md(r"""##Exploration""")
    return


@app.cell
def _(merged):
    merged.head(20)
    return


@app.cell
def _(graduation, students):
    print(graduation.count())
    print(students.count())
    return


@app.cell
def _(mo):
    mo.md(r"""Checking nulls""")
    return


@app.cell
def _(graduation):
    graduation.isnull().sum()
    return


@app.cell
def _(students):
    students.isnull().sum()
    return


@app.cell
def _(mo):
    mo.md(r"""checking uniques""")
    return


@app.function
def unique_lister(df):
    for column in df.columns:
        print(f'{column}: {df[column].unique()}')


@app.cell
def _():
    return


@app.cell
def _(graduation):
    unique_lister(graduation)
    return


@app.cell
def _(students):
    unique_lister(students)
    return


@app.cell
def _(graduation):
    graduation.columns
    return


@app.cell
def _(graduation):
    unknown_departments = graduation[graduation['DEPARTMENT'] == 'Unknown']
    return


@app.cell
def _(mo):
    mo.md(r"""checking consistency""")
    return


@app.cell
def _(graduation, students):
    unmatched = graduation[~graduation['STUDENT_ID'].isin(students['STUDENT_ID'])]
    unmatched
    return (unmatched,)


@app.cell
def _(mo):
    mo.md(r"""validation""")
    return


@app.cell
def _(graduation, pd):
    ## datetime logic
    graduation['GRADUATION_DATE'] = pd.to_datetime(graduation['GRADUATION_DATE'])
    graduation['GRAD_APPL_DATE'] = pd.to_datetime(graduation['GRAD_APPL_DATE'])
    return


@app.cell
def _(graduation):
    grad_date_issues = graduation[graduation['GRAD_APPL_DATE'] > graduation['GRADUATION_DATE']]
    return (grad_date_issues,)


@app.cell
def _(graduation):
    ## credits logic check

    below_credits_but_graduated = graduation[(graduation['TOTAL_CREDITS'] < graduation['REQUIRED_HOURS']) & (graduation['GRADUATED_IND'] == 'Y')]

    below_credits_but_graduated
    return (below_credits_but_graduated,)


@app.cell
def _(graduation):
    (graduation['OVERALL_GPA'] > 4).sum()
    return


@app.cell
def _(graduation):
    graduation.duplicated().sum()
    return


@app.cell
def _(graduation):
    graduation['STUDENT_ID'].duplicated().sum()
    return


@app.cell
def _(graduation):
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
    graduation[graduation['SEMESTER'] == 'Other']
    return


@app.cell
def _(graduation, students):
    dashboard_data = graduation.merge(students, on="STUDENT_ID", how='left')
    return (dashboard_data,)


@app.cell
def _(dashboard_data):
    dashboard_data['ILLOGICAL_DATES'] = dashboard_data['GRAD_APPL_DATE'] > dashboard_data['GRADUATION_DATE']
    dashboard_data['BELOW_CREDITS'] = dashboard_data['TOTAL_CREDITS'] < dashboard_data['REQUIRED_HOURS']
    dashboard_data['MISSING'] = dashboard_data['STUDENT_ID'].isnull()
    return


@app.cell
def _(
    below_credits_but_graduated,
    grad_date_issues,
    graduation,
    pd,
    unmatched,
):
    # create an summary table of the issues
    quality_summary = pd.DataFrame({
        'Issue Type': ['Illogical Dates', 'Unmatched Students', 'Below Required Credits', 'Missing Student IDs'],
        'Record Count': [
            len(grad_date_issues),
            len(unmatched),
            len(below_credits_but_graduated),
            graduation['STUDENT_ID'].isnull().sum()
        ]
    })

    quality_summary.to_csv('quality_issues_summary.csv', index=False)
    return


@app.cell
def _(dashboard_data):
    dashboard_data.to_csv('dashboard_data.csv', index=False)
    return


@app.cell
def _(dashboard_data):
    dashboard_data.columns
    return


@app.cell
def _(dashboard_data):
    dashboard_data.dtypes
    return


@app.cell
def _(graduation):
    graduation
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
