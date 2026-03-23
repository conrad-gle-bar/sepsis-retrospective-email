# Sepsis Reinforcement Email System

An automated email system for sending personalized retrospective sepsis event data to healthcare providers. Sepsis is defined by the CDC Adult Sepsis Events (ASE) criteria. Used primarily for internal quality assurance and improvement. Secondary benefit for this system is reminding providers that these data are followed for the enterprise and this can change behaviors towards our sepsis surveillance systems.

## Features

- **Automated Data Retrieval**: Pulls sepsis event data from Azure and Clarity databases
- **Personalized Reports**: Generates individualized email reports for each provider based on their treatment team assignments
- **Active Directory Integration**: Validates provider status and retrieves current contact information
- **Rich HTML Tables**: Creates formatted tables with sepsis surveillance system data and bundle metrics
- **Comprehensive Metrics**: Tracks nurse/provider responses, blood culture timing, antibiotic administration, and lactate measurements

## Azure Database Table: `ase_email_report`
Expected columns:
- `PAT_ENC_CSN_ID`: Patient encounter ID
- `PAT_MRN_ID`: Patient medical record number
- `ONSET_DATE`: Sepsis onset date
- `ONSET_TYPE`: Community or Hospital onset
- `DISPOSITION`: Patient disposition (Discharged, Death, None)
- `FIRST_ALERT_IN_WINDOW`: Initial alert timestamp
- `NURSE_RESPONSE_IN_ACTIVITY`: Boolean for nurse response
- `PROVIDER_RESPONSE_IN_ACTIVITY`: Boolean for provider response
- `CONFIRMED_IN_ACTIVITY`: Boolean for confirmation
- `DISMISSED_IN_ACTIVITY`: Boolean for dismissal
- `BLOOD_CULTURE_IN_3HR`: Boolean for blood culture within 3 hours
- `ANTIBIOTICS_IN_3HR`: Boolean for antibiotics within 3 hours
- `LACATE_IN_3HR`: Boolean for lactate within 3 hours

## Workflow

1. Wake up the Azure database (if needed)
2. Retrieve sepsis event data
3. Fetch treatment team members for each event
4. Generate personalized email reports
5. Send emails to all providers
6. Send a tracing summary to the admin

## Email Content

Each provider receives an HTML email containing:

- **Header**: Personalized greeting with provider name
- **Context**: Explanation of the CDC Adult Sepsis Event program
- **Data Table**: Up to 5 recent sepsis events from their patients, including:
  - Patient eMRN
  - Onset type (Community/Hospital)
  - Disposition
  - Surveillance system response times
  - Bundle metric compliance
- **Column Definitions**: Detailed explanations of each metric
- **References**: Links to CDC and JAMA resources

## References

- [CDC Sepsis Core Elements](https://www.cdc.gov/sepsis/hcp/core-elements/index.html)
- [JAMA Sepsis-3 Definitions](https://jamanetwork.com/journals/jama/fullarticle/2654187)
