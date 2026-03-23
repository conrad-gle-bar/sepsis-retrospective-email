from great_tables import GT, style, loc
import smtplib
from email.utils import formataddr
from email.message import EmailMessage
import polars as pl
import os

def send_outlook_email(email, full_name, subject, body):
    sender_name = os.getenv('SENDER_NAME')
    sender_email = os.getenv('SENDER_EMAIL')
    from_tuple = (sender_name, sender_email)

    msg = EmailMessage()
    msg['From'] = formataddr(from_tuple)
    msg['To'] = formataddr((full_name, email))
    msg['Reply-To'] = sender_email

    msg['Subject'] = subject

    msg.set_content(body, subtype="html")

    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 25))  

    from_email = formataddr(from_tuple)
    to_email = formataddr((full_name, email))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        try:
            server.sendmail(from_email, to_email, msg.as_string())
            return 'SUCCESS'
        except:
            return 'SENDMAIL_ERROR'

def create_email_table(starting_table=None):
    start_date = starting_table['ONSET_DATE'].min().strftime('%B %d %Y')
    end_date = starting_table['ONSET_DATE'].max().strftime('%B %d %Y')
    table = starting_table.select(
        pl.col('PAT_MRN_ID'),
        pl.col('ONSET_TYPE'),
        pl.col('DISPOSITION'),
        pl.col('FIRST_ALERT_IN_WINDOW').alias('INITIAL_ALERT_TIME'),
        pl.col('NURSE_RESPONSE_IN_ACTIVITY'),
        pl.col('PROVIDER_RESPONSE_IN_ACTIVITY'),
        pl.col('CONFIRMED_IN_ACTIVITY'),
        pl.col('DISMISSED_IN_ACTIVITY'),
        pl.col('BLOOD_CULTURE_IN_3HR'),
        pl.col('ANTIBIOTICS_IN_3HR'),
        pl.col('LACATE_IN_3HR'),
    )
    table = table.rename({col: col.replace('_', ' ').lower().capitalize() for col in table.columns})
    table = table.rename({'Pat mrn id': 'eMRN'})
    gt_tbl = (
        GT(table[:5])
        .tab_header(title="Adult Sepsis Events", subtitle=f"{start_date} to {end_date}")
        .tab_style(
            style=style.text(size='small'),
            locations=loc.column_labels(),
        )
        .tab_style(
            style=style.text(size='small'),
            locations=loc.body(),
        )
        .tab_spanner(
            label="Surveillance System",
            columns=["Initial alert time", 'Nurse response in activity', 'Provider response in activity', 'Confirmed in activity', 'Dismissed in activity']
        )
        .tab_spanner(
            label="Bundle Metrics",
            columns=["Blood culture in 3hr", "Antibiotics in 3hr", 'Lacate in 3hr']
        )
        .fmt_datetime(columns=['Initial alert time'], date_style='m_day_year', time_style='h_m_p')
        .cols_width(
            cases={
                "Initial alert time": "150px",
            }
        )
    ).opt_horizontal_padding(scale=0.5).opt_vertical_padding(scale=0.5)
    return gt_tbl

def create_email_body(table_html):
    hospital_name = os.getenv('HOSPITAL_NAME', 'Hospital')
    committee_name = os.getenv('COMMITTEE_NAME', 'Sepsis Committee')

    email_body = f'''
Good morning,<br />
<br />
You are receiving this email part of the {hospital_name}'s {committee_name} periodic emails to nurses and providers
for patients who met a “CDC Adult Sepsis Event” (ASE) during their recent hospital encounter. The data below are ASEs for which you
were on the treatment team at the time. These data are collected retrospectively and not intended to guide or judge clinical decision making.
However, they may provide insight into sepsis management and opportunities for personal case review.
These data also include information about the use of the “Sepsis Surveillance System” and are important as we
evaluate the accuracy of this AI-enhanced alerting system.
<br /><br />
Thank you for your excellent clinical care and we hope these data provide some insight for you,<br />
<br />
{hospital_name} {committee_name}<br />
<br /><br /><br /><br />
{table_html}
<br /><br />
<b>Column Definitions</b>:<br />
<b>eMRN</b>: Patient eMRN. Patients can have multiple sepsis events and will be listed multiple times.<br />
<b>Onset type</b>: [Community, Hospital] based on the CDC definition. If the sepsis event starts within 48 hours of admission, it is community onset.<br />
<b>Disposition</b>: [Discharged, Death, None] None means the patient remains inpatient.<br />
<b>Initial alert time</b>: First occurance of the Sepsis Surveillance System alerting the nurse and provider. (If "None", no alert was triggered)<br />
<b>Nurse response in activity</b>: At least one nurse responded in the sepsis activity.<br />
<b>Provider response in activity</b>: At least one provider responded in the sepsis activity.<br />
<b>Confirmed in activity</b>: Sepsis was confirmed, at least once, in the activity.<br />
<b>Dismissed in activity</b>: Sepsis was dismissed, at least once, in the activity.<br />
<b>Blood culture in 3hr</b>: At least one blood culture was ordered within 3 hours of time zero.<br />
<b>Antibiotics in 3hr</b>: At least one dose of antibiotics was administered within 3 hours of time zero.<br />
<b>Lacate in 3hr</b>: At least one lactate was drawn within 3 hours of time zero.<br />
<br /><br />
Notes:<br />
Multiple providers could have responded. Therefore, it is possible for this to be confirmed & dismissed within the same event.<br />
"Time zero" is the time of the initial alert from the sepsis surveillance system or, if the surveillance system did not alert, 
the earliest time in the window period when either the blood culture was collected, first antibiotic was adminitered, or organ dysfunction criteria was met.
<br /><br />
References:<br />
<a href="https://www.cdc.gov/sepsis/hcp/core-elements/index.html">CDC Link</a><br />
<a href="https://jamanetwork.com/journals/jama/fullarticle/2654187">JAMA Article</a><br />
<br />
'''
    return email_body


if __name__ == "__main__":
    import dotenv
    dotenv.load_dotenv()

    test_email = os.getenv('SENDER_EMAIL')
    test_name = os.getenv('SENDER_NAME')
    send_outlook_email(test_email, test_name, 'testing email function', 'testing email function')
    print('SUCCESS')