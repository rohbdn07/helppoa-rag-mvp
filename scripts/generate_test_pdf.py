"""Generate a fictional 20-page test PDF for the Helppoa RAG pipeline.

All institutions, phone numbers, fees, and procedures in the output document
are INVENTED. Do not use any of this content as real legal or civic guidance.
The fictional framing is intentional: the file exists only to give the RAG
something larger and more varied than the seed text document, so retrieval
quality can actually be measured.

Run:
    venv/bin/python scripts/generate_test_pdf.py

Output:
    data/helppoa_test_reference.pdf
"""

from pathlib import Path

from reportlab.lib.colors import HexColor, grey
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


OUTPUT = Path("data/helppoa_test_reference.pdf")

WARNING_BANNER = (
    "<b><font color='#b00020'>FICTIONAL TEST DOCUMENT — NOT LEGAL ADVICE.</font></b> "
    "All institutions, phone numbers, fees, and procedures below are invented "
    "for testing the Helppoa RAG pipeline. Do not rely on any of this content "
    "for real-world decisions."
)

# Each topic is (title, body_html). Body uses ReportLab's mini-HTML
# (b, br, i tags). Each topic is sized to fill ~2 pages at 11pt body text.
TOPICS: list[tuple[str, str]] = [
    (
        "1. Residence Permits and Newcomer Registration",
        """
Newly arrived residents must register with the Office of Fictional Newcomer
Registration (OFNR) within 21 days of arrival. The OFNR issues the Provisional
Residence Card (PRC), which is required to open a bank account, sign a rental
contract, or enrol in a language course.<br/><br/>

<b>Key facts</b><br/>
- The PRC is valid for 90 days from the date of issue.<br/>
- A permanent Residence Identification Number (RIN) is issued within 14
business days of submitting the long-form application.<br/>
- The application fee is 47 fictional euros.<br/>
- Children under 7 do not require a separate PRC; they are added to the
primary applicant's record.<br/>
- Late registration (after 21 days) incurs a 60-euro administrative fee.<br/><br/>

<b>Required documents</b><br/>
1. Passport or national ID card valid for at least 6 months.<br/>
2. Proof of address: lease contract, hotel reservation, or sponsor letter.<br/>
3. Two passport-style photographs (35x45 mm, white background).<br/>
4. Completed Form OFNR-101 available at any OFNR service desk.<br/>
5. Proof of sufficient funds: 1,250 fictional euros per month minimum.<br/><br/>

<b>Common pitfall</b><br/>
The PRC does not grant the right to work. To take up employment a separate
Work Authorization Stamp (WAS) must be requested through the OFNR portal
before the start of the contract. Working without a WAS may result in
termination of the residence permit and a fine of up to 2,000 euros.<br/><br/>

<b>Contact</b><br/>
Office of Fictional Newcomer Registration (OFNR)<br/>
Phone: +358 99 000 0101 (Mon–Thu 8:30–15:00, Fri 8:30–13:00)<br/>
Email: ofnr-info@fictional-helppoa.test<br/>
Service desks: Helsinki Pasila, Tampere Hervanta, Turku Centre, Oulu Linnanmaa.
""",
    ),
    (
        "2. Healthcare and Health Insurance",
        """
Residents with a valid PRC are entitled to use the public health network
operated by the Fictional Health Coverage Bureau (FHCB). The FHCB issues a
Health Access Card (HAC), which must be presented at every appointment.<br/><br/>

<b>Key facts</b><br/>
- HAC issuance takes up to 21 calendar days after PRC registration.<br/>
- The standard appointment co-payment is 22 fictional euros for adults.<br/>
- Visits for children under 18 are free of co-payment.<br/>
- An annual co-payment ceiling of 720 euros applies; overage is reimbursed.<br/>
- Emergency care is provided regardless of HAC status, but a follow-up
verification check is performed within 30 days.<br/><br/>

<b>How to book a non-urgent appointment</b><br/>
1. Call the regional FHCB switchboard at +358 99 000 0202.<br/>
2. Provide your HAC number and the symptom description.<br/>
3. The triage nurse assigns either a same-week slot or a queue ticket.<br/>
4. Same-day cancellation requires at least 4 hours notice; otherwise a
no-show fee of 35 euros may be charged.<br/><br/>

<b>Prescription medications</b><br/>
The FHCB reimburses 60 percent of the listed price for prescriptions on the
Standard Reimbursement List (SRL). Reimbursement is processed automatically
at registered pharmacies when the HAC is presented.<br/><br/>

<b>Mental-health services</b><br/>
Direct self-referral to a public psychologist is permitted up to 3 sessions
per year without a doctor's referral. Beyond 3 sessions a referral from a
general practitioner is required.<br/><br/>

<b>Contact</b><br/>
Fictional Health Coverage Bureau (FHCB)<br/>
Phone: +358 99 000 0202 (24 hours; non-urgent calls 8:00–20:00)<br/>
Emergencies: 112
""",
    ),
    (
        "3. Taxation and Income Reporting",
        """
All residents earning income in the country must register with the Fictional
Income and Levy Office (FILO) before the first salary payment. FILO issues a
Tax Withholding Card (TWC), which the employer uses to apply the correct
withholding rate.<br/><br/>

<b>Key facts</b><br/>
- The default withholding rate without a TWC is 60 percent.<br/>
- Personal allowance for the tax year is 14,500 fictional euros.<br/>
- The marginal rate above the allowance starts at 17.5 percent.<br/>
- Employer-provided lunch benefits up to 130 euros per month are
tax-exempt.<br/>
- Annual tax declaration is due by 30 April of the following year.<br/><br/>

<b>How to obtain a Tax Withholding Card</b><br/>
1. Submit Form FILO-204 at any FILO branch or via the online portal.<br/>
2. Attach a copy of the PRC or RIN.<br/>
3. Provide the employment contract or signed offer letter.<br/>
4. The TWC is issued within 7 business days; expedited issuance (24 hours)
costs 25 euros.<br/><br/>

<b>Self-employment and freelancers</b><br/>
Independent contractors must register a Freelance Activity Code (FAC) and
submit quarterly advance payments. The Q1 advance is due by 15 April,
Q2 by 15 July, Q3 by 15 October, and Q4 by 15 January of the following year.
Late payment incurs an interest charge of 4 percent annualised.<br/><br/>

<b>Common pitfall</b><br/>
Many newcomers assume the personal allowance is applied automatically; it is
not. Without a TWC the employer applies the full 60 percent withholding, and
the over-withheld amount is only refunded after the annual declaration.<br/><br/>

<b>Contact</b><br/>
Fictional Income and Levy Office (FILO)<br/>
Phone: +358 99 000 0303 (Mon–Fri 8:00–16:00)<br/>
Email: filo-help@fictional-helppoa.test
""",
    ),
    (
        "4. Tenant Rights and Housing",
        """
Residential tenancies are governed by the Fictional Residential Lease Act
(FRLA). Both landlord and tenant must sign a written contract; verbal
agreements are not enforceable beyond 30 days.<br/><br/>

<b>Key facts</b><br/>
- The maximum security deposit is 3 months' rent.<br/>
- The deposit must be returned within 14 days of move-out, less any
documented damage.<br/>
- Rent increases require 6 months' written notice and may not exceed the
annual housing index plus 1.5 percent.<br/>
- The minimum lease term for a fixed-term contract is 6 months.<br/>
- Subletting is permitted only with the landlord's written consent.<br/><br/>

<b>Repairs and maintenance</b><br/>
The landlord is responsible for structural repairs, heating, and plumbing.
The tenant is responsible for cosmetic damage and minor wear caused by
ordinary use. If a critical system (heat, water, electricity) fails, the
landlord must restore service within 72 hours of written notice. Failure to
do so entitles the tenant to a rent reduction of 25 percent for the affected
period.<br/><br/>

<b>Eviction</b><br/>
A landlord cannot evict a tenant without proper legal grounds. Valid grounds
include non-payment of rent for more than 30 days, serious disturbance of
neighbours, or material breach of the lease. The landlord must provide
written notice: 1 month for tenancies under 1 year, 3 months for tenancies
of 1 year or longer. Illegal eviction may be reported to the Fictional
Housing Tribunal (FHT) at +358 99 000 0404.<br/><br/>

<b>Disputes</b><br/>
Tenants can bring disputes to the Fictional Housing Tribunal at no cost
within 6 months of the disputed event. The Tribunal issues a binding ruling
within 60 days of the hearing.<br/><br/>

<b>Contact</b><br/>
Fictional Housing Tribunal (FHT)<br/>
Phone: +358 99 000 0404 (Mon–Fri 9:00–15:00)
""",
    ),
    (
        "5. Banking, Identity, and Digital Authentication",
        """
A resident bank account is required to receive salary payments and pay
utilities. Banks accept the PRC as primary identification only when paired
with a second proof of address such as a recent utility bill or a signed
lease contract.<br/><br/>

<b>Key facts</b><br/>
- Account opening typically takes 5–10 business days.<br/>
- Most banks issue a debit card within 14 days of account opening.<br/>
- Online banking activation requires the Digital Identity Token (DIT),
which is mailed separately to the registered address.<br/>
- The DIT must be activated within 30 days or it is invalidated.<br/>
- Replacement of a lost DIT costs 20 euros and takes 7 business days.<br/><br/>

<b>Digital Identity Token (DIT)</b><br/>
The DIT is the standard authentication mechanism for government services,
banks, and many private platforms. It supports two-factor login via mobile
app or hardware key. To register a new device, log in with the existing
device and select "Add device" within 24 hours.<br/><br/>

<b>Common pitfalls</b><br/>
1. Some banks reject the PRC alone; bringing the lease contract avoids
delays.<br/>
2. The DIT mobile app must be re-paired after a phone reset; the pairing
code is sent only to the registered email address.<br/>
3. Lost-DIT replacement requires in-person identification at a branch.<br/><br/>

<b>Contact</b><br/>
Fictional Digital Authentication Centre (FDAC)<br/>
Phone: +358 99 000 0505 (Mon–Fri 8:00–18:00, Sat 9:00–13:00)
""",
    ),
    (
        "6. Employment and Worker Rights",
        """
Employment relationships are governed by the Fictional Employment Standards
Act (FESA). All employment contracts must be in writing for engagements
longer than one month.<br/><br/>

<b>Key facts</b><br/>
- The statutory probation period is up to 6 months.<br/>
- Standard working time is 7.5 hours per day, 37.5 hours per week.<br/>
- Overtime above 37.5 hours per week is paid at 150 percent of base rate.<br/>
- Overtime above 45 hours per week is paid at 200 percent of base rate.<br/>
- Annual paid leave entitlement is 25 working days after 12 months of
service.<br/>
- Sick-leave pay covers 100 percent of salary for the first 9 days; from
day 10 the FHCB takes over with 75 percent coverage.<br/><br/>

<b>Termination notice periods</b><br/>
Employer notice to employee: 14 days during probation, 1 month for service
under 1 year, 2 months for 1–4 years, 4 months for 4–8 years, 6 months for
service over 8 years. Employee notice to employer is uniformly 1 month
after probation.<br/><br/>

<b>Unemployment benefits</b><br/>
Workers who have been employed for at least 6 months in the previous 12
months are eligible for unemployment support through the Fictional
Employment Support Office (FESO). The standard daily rate is 60 percent of
average insured earnings, capped at 110 euros per day. Benefits are paid
for up to 300 working days within a 4-year reference period.<br/><br/>

<b>Workplace harassment</b><br/>
Reports of harassment must be filed within 90 days of the incident either
through the employer's grievance channel or directly to the Fictional
Workplace Conduct Authority (FWCA). FWCA investigates within 30 days and
may impose fines of up to 12,000 euros on non-compliant employers.<br/><br/>

<b>Contact</b><br/>
Fictional Employment Support Office (FESO)<br/>
Phone: +358 99 000 0606 (Mon–Fri 8:00–16:00)
""",
    ),
    (
        "7. Education and Childcare",
        """
Compulsory education in the country runs from age 7 to age 16. Public
schools are free of tuition. Optional pre-primary education is available
from age 5.<br/><br/>

<b>Key facts</b><br/>
- School registration must be completed by 1 May for enrolment in the
following August.<br/>
- The school year runs from mid-August to early June, with mandatory
breaks at Christmas, mid-winter, and Easter.<br/>
- Subsidised after-school care is offered for children up to age 10 at a
fee of 110 euros per month.<br/>
- Public-school meals are free.<br/>
- Private schools may charge tuition; tuition relief is available based on
household income through the Education Equity Fund (EEF).<br/><br/>

<b>Childcare for under-7s</b><br/>
Municipal day-care is offered to all children aged 10 months to 6 years.
Fees are income-tested on a sliding scale from 0 to 295 euros per month.
Applications must be submitted at least 4 months before the desired start
date.<br/><br/>

<b>Special educational support</b><br/>
Children whose first language is not the local language receive up to 4
hours per week of supplementary language instruction during the first two
years of enrolment, at no cost.<br/><br/>

<b>Common pitfall</b><br/>
The 1 May registration deadline is strict. Missing the deadline often means
placement at the next available school regardless of catchment area, with
re-application required for the following year.<br/><br/>

<b>Contact</b><br/>
Fictional Education and Care Authority (FECA)<br/>
Phone: +358 99 000 0707 (Mon–Fri 9:00–15:00)
""",
    ),
    (
        "8. Police, Emergencies, and Reporting Crime",
        """
The general emergency number is 112, available 24 hours and free from any
phone, including without a SIM card.<br/><br/>

<b>When to call 112</b><br/>
- Immediate threat to life, health, or property.<br/>
- Crime in progress or just occurred.<br/>
- Serious traffic accident.<br/>
- Fire or hazardous material incident.<br/><br/>

<b>Non-urgent matters</b><br/>
For non-urgent reports such as stolen bicycles, lost documents, or small-
scale property damage, contact the Fictional Police Service (FPS)
non-emergency line at +358 99 000 0808 or use the online reporting portal.
Online reports receive an acknowledgement within 48 hours and a case number
within 7 days.<br/><br/>

<b>Lost residence card or DIT</b><br/>
Lost or stolen documents must be reported within 72 hours, both to the FPS
and to the issuing authority (OFNR for the PRC, FDAC for the DIT). The
police report number is required when applying for a replacement.<br/><br/>

<b>Victim support</b><br/>
Free, confidential victim support is available through the Fictional Victim
Assistance Network (FVAN). Services include legal advice, counselling, and
court accompaniment, regardless of whether a formal report has been made.<br/><br/>

<b>Reporting hate crimes</b><br/>
Reports of hate-motivated crime can be filed through any standard channel
or directly with the Fictional Equal Treatment Commission (FETC), which
maintains a dedicated hotline.<br/><br/>

<b>Contacts</b><br/>
Emergencies: 112<br/>
Fictional Police Service (FPS) non-emergency: +358 99 000 0808<br/>
Fictional Victim Assistance Network (FVAN): +358 99 000 0809<br/>
Fictional Equal Treatment Commission (FETC): +358 99 000 0810
""",
    ),
    (
        "9. Driving, Public Transport, and Vehicle Registration",
        """
Foreign driving licenses are accepted for the first 12 months of residence.
After 12 months a local exchange license is required.<br/><br/>

<b>Key facts</b><br/>
- Exchange application must be filed before the 12-month deadline.<br/>
- Licenses from countries on the Fictional Mutual Recognition List (FMRL)
are exchanged without a driving test.<br/>
- Licenses from non-FMRL countries require a written theory test and a
practical driving test.<br/>
- The exchange fee is 95 euros.<br/>
- New license is issued within 21 days of a successful application.<br/><br/>

<b>Vehicle registration</b><br/>
Imported vehicles must be registered within 30 days of arrival. Registration
includes a technical inspection and payment of the Initial Vehicle Levy
(IVL), which depends on engine displacement and emissions.<br/><br/>

<b>Public transport</b><br/>
The integrated public transport network is operated by the Fictional
Regional Mobility Authority (FRMA). A monthly travel pass costs 65 euros
for adults, 35 euros for students, and 28 euros for seniors over 65.
Children under 7 travel free with an adult.<br/><br/>

<b>Cycling</b><br/>
Cycling is permitted on dedicated cycle paths and on roadways. Helmets are
strongly recommended and mandatory for under-15s. Bicycle lights are
required from 30 minutes before sunset until 30 minutes after sunrise.<br/><br/>

<b>Common pitfall</b><br/>
Driving with an expired foreign license after the 12-month deadline is
treated as driving without a valid license, with fines of up to 800 euros
and possible insurance invalidation.<br/><br/>

<b>Contacts</b><br/>
Fictional Driver Licensing Authority (FDLA): +358 99 000 0909<br/>
Fictional Regional Mobility Authority (FRMA): +358 99 000 0910
""",
    ),
    (
        "10. Useful Contacts and Closing Notes (overview)",
        """
This page consolidates the principal contacts referenced throughout the
document. All numbers are fictional and exist only for testing.<br/><br/>

<b>Emergencies</b><br/>
General emergency: 112<br/>
Fictional Poison Information Line: +358 99 000 1001<br/>
Fictional Crisis Helpline (24h): +358 99 000 1002<br/><br/>

<b>Civic and administrative</b><br/>
Office of Fictional Newcomer Registration (OFNR): +358 99 000 0101<br/>
Fictional Health Coverage Bureau (FHCB): +358 99 000 0202<br/>
Fictional Income and Levy Office (FILO): +358 99 000 0303<br/>
Fictional Housing Tribunal (FHT): +358 99 000 0404<br/>
Fictional Digital Authentication Centre (FDAC): +358 99 000 0505<br/>
Fictional Employment Support Office (FESO): +358 99 000 0606<br/>
Fictional Education and Care Authority (FECA): +358 99 000 0707<br/>
Fictional Police Service (FPS) non-emergency: +358 99 000 0808<br/>
Fictional Driver Licensing Authority (FDLA): +358 99 000 0909<br/><br/>

<b>Support and advocacy</b><br/>
Fictional Victim Assistance Network (FVAN): +358 99 000 0809<br/>
Fictional Equal Treatment Commission (FETC): +358 99 000 0810<br/>
Fictional Workplace Conduct Authority (FWCA): +358 99 000 0611<br/><br/>

<b>Important reminder</b><br/>
This document is a fictional reference produced for testing the Helppoa
retrieval pipeline. It does not represent any real country, agency, or
legal framework. Procedures and figures are illustrative only.<br/><br/>

<b>About Helppoa</b><br/>
Helppoa is an experimental local-first retrieval-augmented assistant being
prototyped to help newcomers navigate civic systems. The fictional content
in this document is used solely to evaluate retrieval quality with a
larger, more varied corpus than the seed text file.
""",
    ),
]


# A second "Worked examples" page per topic. Doubles the page count to ~20
# and gives ready-made queries you can use to test the RAG.
EXAMPLES: list[tuple[str, str]] = [
    (
        "1. Worked Examples — Residence Permits",
        """
<b>Scenario A: Single applicant, late registration</b><br/>
Anika arrived on 4 March and registered on 4 April (31 days later). She
must pay the standard 47-euro fee plus a 60-euro late-registration fee,
total 107 euros. Her PRC is issued on 9 April and is valid until 8 July.<br/><br/>

<b>Scenario B: Family with two children</b><br/>
The Patel family arrives with two children aged 5 and 9. Both parents and
the 9-year-old need separate PRCs (3 × 47 = 141 euros). The 5-year-old is
added to a parent's record at no extra cost. Total fee: 141 euros.<br/><br/>

<b>Scenario C: Employment before WAS</b><br/>
Diego started a part-time job on his second day in the country, before
applying for the Work Authorization Stamp. The employer is fined 1,200
euros and Diego's PRC is flagged for review. He can re-apply with a new
sponsor letter but must pay a 200-euro reinstatement fee.<br/><br/>

<b>Common questions answered in this section</b><br/>
- How long is the PRC valid? 90 days from issue.<br/>
- What is the fee for late registration? 60 euros on top of the standard
fee.<br/>
- Do children need their own PRC? Only at age 7 and above.<br/>
- Can I work with only a PRC? No — a separate Work Authorization Stamp is
required.
""",
    ),
    (
        "2. Worked Examples — Healthcare",
        """
<b>Scenario A: Adult routine visit</b><br/>
Mei books a routine GP appointment. She pays the 22-euro adult co-payment
on arrival and presents her HAC. The visit is otherwise free.<br/><br/>

<b>Scenario B: Reaching the annual co-payment ceiling</b><br/>
Over the year Tomas accumulates 740 euros of co-payments due to a chronic
condition. The 20 euros above the 720-euro ceiling is reimbursed
automatically by the FHCB within 30 days.<br/><br/>

<b>Scenario C: Same-day cancellation</b><br/>
Lena cancels a 09:30 appointment at 07:15 the same morning — only 2 hours
and 15 minutes notice. She is charged the 35-euro no-show fee because the
cancellation came inside the 4-hour window.<br/><br/>

<b>Common questions answered in this section</b><br/>
- How much is the standard co-payment? 22 euros for adults; free for under-18s.<br/>
- What is the annual co-payment ceiling? 720 euros, reimbursed above that.<br/>
- How long does the HAC take? Up to 21 calendar days after PRC registration.<br/>
- Can I see a psychologist directly? Yes, up to 3 sessions per year without
a referral.
""",
    ),
    (
        "3. Worked Examples — Taxation",
        """
<b>Scenario A: First salary without a TWC</b><br/>
Pavel starts work on 1 February without a Tax Withholding Card. The
employer applies the default 60-percent withholding to his first three
salaries until his TWC arrives in March. The over-withheld amount is
refunded after his annual tax declaration the following spring.<br/><br/>

<b>Scenario B: Personal allowance applied correctly</b><br/>
Astrid's gross annual salary is 38,000 euros. With the 14,500-euro
personal allowance applied, only 23,500 euros is taxable, beginning at
the 17.5-percent marginal rate.<br/><br/>

<b>Scenario C: Freelancer missed a quarterly deadline</b><br/>
Felix was due to pay a Q2 advance of 1,400 euros by 15 July but paid on
30 July (15 days late). The interest charge at 4 percent annualised is
roughly 2.30 euros: small, but the missed payment goes on his FILO
record.<br/><br/>

<b>Common questions answered in this section</b><br/>
- What is the default withholding without a TWC? 60 percent.<br/>
- When is the annual tax declaration due? 30 April.<br/>
- What is the personal allowance? 14,500 euros.<br/>
- When are freelancer advances due? 15 April, 15 July, 15 October, 15 January.
""",
    ),
    (
        "4. Worked Examples — Tenant Rights",
        """
<b>Scenario A: Heating outage</b><br/>
The heating in Marko's apartment fails on a Friday evening. He sends a
written notice that night. The landlord must restore heat by Monday
evening (72 hours). If service is not restored, Marko is entitled to a
25-percent rent reduction for every day of continued failure.<br/><br/>

<b>Scenario B: Deposit return</b><br/>
Sara moves out on 1 March. The landlord must return her 2,400-euro
deposit (less documented damage) by 15 March. If the landlord withholds
1,000 euros for "general wear" without itemised documentation, Sara can
challenge the deduction at the Fictional Housing Tribunal.<br/><br/>

<b>Scenario C: Eviction notice</b><br/>
Otto has lived in his apartment for 15 months. His landlord serves a
written eviction notice citing repeated late rent payments. Because the
tenancy is over 1 year, the notice period is 3 months, not 1 month.<br/><br/>

<b>Common questions answered in this section</b><br/>
- What is the maximum deposit? 3 months' rent.<br/>
- How long does the landlord have to fix critical systems? 72 hours.<br/>
- Can a landlord evict without grounds? No.<br/>
- What is the notice period for tenancies over 1 year? 3 months.
""",
    ),
    (
        "5. Worked Examples — Banking and Digital ID",
        """
<b>Scenario A: Account opening with PRC only</b><br/>
Aisha visits a bank with her PRC but no other proof of address. The
branch declines and asks her to return with a signed lease contract.
After bringing the lease the next week, the account is opened in 6
business days.<br/><br/>

<b>Scenario B: DIT activation deadline</b><br/>
Hugo's DIT arrives on 10 May. He must activate it by 9 June. He travels
abroad and forgets; the DIT is invalidated on 10 June and a 20-euro
replacement is required.<br/><br/>

<b>Scenario C: Lost DIT</b><br/>
Niamh loses her DIT during a move. She reports the loss the same day.
She visits a branch in person to identify herself, pays 20 euros, and
receives a new DIT 7 business days later.<br/><br/>

<b>Common questions answered in this section</b><br/>
- How long does account opening take? Typically 5–10 business days.<br/>
- What is the DIT activation window? 30 days from receipt.<br/>
- How much does DIT replacement cost? 20 euros.<br/>
- What second proof of address do banks usually require? A lease contract
or recent utility bill.
""",
    ),
    (
        "6. Worked Examples — Employment",
        """
<b>Scenario A: Probation termination</b><br/>
Zara's employer terminates her contract during the 4th month of a 6-month
probation period. The notice period is 14 days regardless of whether the
probation has run its full length.<br/><br/>

<b>Scenario B: Overtime at 50 hours per week</b><br/>
Ben works 50 hours in a single week. The first 37.5 hours are at base
rate. Hours 37.5 to 45 (7.5 hours) are paid at 150 percent. Hours 45 to
50 (5 hours) are paid at 200 percent.<br/><br/>

<b>Scenario C: Sick leave beyond day 9</b><br/>
Helga is on certified sick leave for 14 days. Days 1–9 are paid at 100
percent of salary by the employer. Days 10–14 are covered at 75 percent
by the FHCB.<br/><br/>

<b>Scenario D: Termination after 3 years of service</b><br/>
Kai has been with the same employer for 3 years and 2 months. The
employer terminates the contract: the notice period is 2 months (the 1–4
year band).<br/><br/>

<b>Common questions answered in this section</b><br/>
- What is the standard work week? 37.5 hours.<br/>
- What is the overtime rate above 45 hours? 200 percent of base.<br/>
- How long is the maximum probation? 6 months.<br/>
- Notice period for 4 years of service? 4 months.
""",
    ),
    (
        "7. Worked Examples — Education and Childcare",
        """
<b>Scenario A: Missed school registration deadline</b><br/>
The Liu family arrives on 28 April and registers their 7-year-old on
3 May — just past the 1 May cutoff. The child is placed at the next
available school in a different district. Re-application for a closer
school is permitted only for the following academic year.<br/><br/>

<b>Scenario B: Day-care fee on a sliding scale</b><br/>
With a household monthly income of 3,800 euros, the Park family qualifies
for a day-care fee of 165 euros per month for a single child — below the
maximum of 295 euros.<br/><br/>

<b>Scenario C: Supplementary language support</b><br/>
Inés enrols in 4th grade in August. Because her first language is not the
local language, she receives 4 hours per week of supplementary language
instruction at no cost during her first two years.<br/><br/>

<b>Common questions answered in this section</b><br/>
- When does the school year start? Mid-August.<br/>
- What is the school registration deadline? 1 May.<br/>
- What does after-school care cost? 110 euros per month.<br/>
- How long is supplementary language support provided? 2 years.
""",
    ),
    (
        "8. Worked Examples — Police and Emergencies",
        """
<b>Scenario A: Stolen bicycle</b><br/>
Markus's bicycle is stolen overnight from a public rack. He files an
online report at 09:00. He receives an acknowledgement at 09:00 the next
morning and a case number 6 days later.<br/><br/>

<b>Scenario B: Lost residence card</b><br/>
Iris loses her PRC at the airport. She reports the loss to the FPS within
24 hours, then to the OFNR within 48 hours. With the police report number
in hand, she applies for a replacement at any OFNR service desk.<br/><br/>

<b>Scenario C: Hate crime report</b><br/>
Omar experiences harassment on public transport. He calls 112 at the time
of the incident; for follow-up he files a separate report with the FETC,
which begins a parallel investigation.<br/><br/>

<b>Common questions answered in this section</b><br/>
- When should I call 112? Immediate threat to life, health, or property.<br/>
- How long do online reports take to acknowledge? Up to 48 hours.<br/>
- How quickly must lost documents be reported? Within 72 hours.<br/>
- Where do I report a hate crime? Any standard channel or the FETC.
""",
    ),
    (
        "9. Worked Examples — Driving and Transport",
        """
<b>Scenario A: License from an FMRL country</b><br/>
Pierre arrives from a country on the FMRL. He exchanges his license
within the 12-month window, pays 95 euros, and receives a local license
21 days later — no test required.<br/><br/>

<b>Scenario B: License from a non-FMRL country</b><br/>
Yuki's home country is not on the FMRL. She must pass both a written
theory test and a practical driving test before exchange. She schedules
both 4 months in advance.<br/><br/>

<b>Scenario C: Imported vehicle</b><br/>
Sven imports a car on 5 June. He must register it by 5 July. Registration
includes a technical inspection (95 euros) and the IVL (varies by engine
displacement and emissions).<br/><br/>

<b>Scenario D: Cycling without lights</b><br/>
Anna is stopped after sunset cycling without lights. She receives an
on-the-spot fine of 50 euros and a written reminder of the rule (lights
required from 30 minutes before sunset to 30 minutes after sunrise).<br/><br/>

<b>Common questions answered in this section</b><br/>
- How long are foreign licenses valid? 12 months from arrival.<br/>
- What does license exchange cost? 95 euros.<br/>
- When must imported vehicles be registered? Within 30 days of arrival.<br/>
- Are bicycle lights mandatory? Yes, after sunset.
""",
    ),
    (
        "10. Worked Examples — End-to-end Newcomer Journey",
        """
<b>Day 1–7: Arrival</b><br/>
Find temporary accommodation. Begin gathering documents: passport,
photographs, sponsor letter or proof of funds. Open a phone-based
calendar reminder for Day 21 (registration deadline).<br/><br/>

<b>Day 8–21: Registration</b><br/>
Visit the OFNR with Form OFNR-101 and supporting documents. Pay the
47-euro fee. Receive the PRC.<br/><br/>

<b>Day 22–35: Banking and Digital ID</b><br/>
Open a bank account using the PRC plus a lease contract. Wait for the
DIT to arrive by post; activate within 30 days of receipt. Order a debit
card.<br/><br/>

<b>Day 35–60: Healthcare and Tax</b><br/>
HAC arrives within 21 days of PRC registration. Submit Form FILO-204 to
obtain the Tax Withholding Card before the first salary payment. Confirm
correct withholding on the first payslip.<br/><br/>

<b>Day 60+: Daily life</b><br/>
Register for public transport pass; if applicable, apply to exchange a
foreign driving license before the 12-month deadline. Enrol children in
school by the 1 May annual deadline.<br/><br/>

<b>Reminder</b><br/>
This document is fictional. Procedures and figures do not represent any
real country. The document exists only as test content for the Helppoa
RAG pipeline.
""",
    ),
]


def build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles = {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontSize=22,
            leading=28,
            spaceAfter=18,
            textColor=HexColor("#101820"),
        ),
        "heading": ParagraphStyle(
            "heading",
            parent=base["Heading2"],
            fontSize=15,
            leading=20,
            spaceBefore=10,
            spaceAfter=8,
            textColor=HexColor("#101820"),
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["BodyText"],
            fontSize=11,
            leading=16,
            spaceAfter=6,
        ),
        "warning": ParagraphStyle(
            "warning",
            parent=base["BodyText"],
            fontSize=9.5,
            leading=13,
            textColor=HexColor("#b00020"),
            spaceAfter=14,
        ),
    }
    return styles


def draw_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(grey)
    canvas.drawString(
        2 * cm,
        1.2 * cm,
        "FICTIONAL — for RAG pipeline testing only. Not legal advice.",
    )
    canvas.drawRightString(
        A4[0] - 2 * cm,
        1.2 * cm,
        f"Page {doc.page}",
    )
    canvas.restoreState()


def build_pdf(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="Helppoa Test Reference (Fictional)",
        author="Helppoa RAG test fixture",
    )
    styles = build_styles()

    story = []
    story.append(Paragraph("Helppoa Test Reference", styles["title"]))
    story.append(
        Paragraph(
            "<i>A fictional newcomer guide for testing the Helppoa RAG pipeline.</i>",
            styles["body"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(WARNING_BANNER, styles["warning"]))
    story.append(
        Paragraph(
            "This document covers ten topics relevant to a newly arrived "
            "resident: registration, healthcare, taxation, housing, banking, "
            "employment, education, public safety, transport, and contacts. "
            "All institutions, fees, and procedures are invented.",
            styles["body"],
        )
    )
    story.append(PageBreak())

    for (title, body), (ex_title, ex_body) in zip(TOPICS, EXAMPLES):
        story.append(Paragraph(title, styles["heading"]))
        story.append(Paragraph(WARNING_BANNER, styles["warning"]))
        story.append(Paragraph(body.strip(), styles["body"]))
        story.append(PageBreak())

        story.append(Paragraph(ex_title, styles["heading"]))
        story.append(Paragraph(WARNING_BANNER, styles["warning"]))
        story.append(Paragraph(ex_body.strip(), styles["body"]))
        story.append(PageBreak())

    doc.build(story, onFirstPage=draw_footer, onLaterPages=draw_footer)


if __name__ == "__main__":
    build_pdf(OUTPUT)
    print(f"Wrote {OUTPUT}")
