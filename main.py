import polars as pl
import dotenv
import os

from database_functions import fetch_treatment_team, fetch_emrns, extractAzureData, wake_up_azure
from email_functions import create_email_table, send_outlook_email, create_email_body
from ad_functions import return_ad_mail, return_full_name

dotenv.load_dotenv()

wake_up_azure()

ase_query = '''select * from ase_email_report'''
ase = extractAzureData(ase_query)

enc_ids = list(ase['PAT_ENC_CSN_ID'])
alert_dates = list(ase.select(
    pl.coalesce("FIRST_ALERT_IN_WINDOW", "ONSET_DATE").cast(pl.Date).cast(pl.String).alias("ALERT_DATE")
)['ALERT_DATE'])

email_grouped = fetch_treatment_team(zip(enc_ids, alert_dates)).group_by('SYSTEM_LOGIN').agg(pl.col('PAT_ENC_CSN_ID'))
emrns = fetch_emrns(enc_ids)
ase = ase.join(emrns, on='PAT_ENC_CSN_ID')

emails_sent = []
email_tracing = f"{len(email_grouped)} emails attempted.<br /><br />"
print(email_tracing)

for i in range(0, len(email_grouped)):
    system_login = email_grouped[i]['SYSTEM_LOGIN'][0]

    try:
        emails_sent.append(return_ad_mail(system_login))
        encounters_to_email = email_grouped[i]['PAT_ENC_CSN_ID']
        email_table = create_email_table(ase.filter(
            pl.col('PAT_ENC_CSN_ID').is_in(encounters_to_email)
        ))

        subject = 'SMH Personalized Sepsis Events Retrospective'
        body = create_email_body(email_table.as_raw_html(inline_css=True))
                                    
        email_result = send_outlook_email(return_ad_mail(system_login), return_full_name(system_login), subject, body)
        print(return_ad_mail(system_login), return_full_name(system_login), len(encounters_to_email[0])) # UNCOMMENT FOR TESTING
    except Exception as e:
        email_result = f"Error occurred: {e}"

    email_tracing += f'{system_login}: {email_result} : {len(encounters_to_email[0])} events.<br />'


admin_email = os.getenv('ADMIN_EMAIL')
admin_name = os.getenv('ADMIN_NAME')
send_outlook_email(admin_email, admin_name, 'SMH Sepsis Emails Tracing', email_tracing)


