from env.models import Email, Label, Priority, Category
import datetime

EMAILS: list[Email] = []
LABELS: dict[str, Label] = {}

# Priority/Category mapped tasks for 30 emails:
# 10 Urgent, 10 Normal, 10 Low
# 8 Billing, 8 Support, 7 Spam, 7 Inquiry

data = [
    ("email_01", "URGENT SYSTEM OUTAGE in Production", "All our servers went down 5 minutes ago. No one can access the platform. Please help immediately!", "cto@startup.com", "CTO Startup", Priority.URGENT, Category.SUPPORT),
    ("email_02", "Monthly Invoice #INV-2023-01", "Here is your monthly invoice. Please pay by the end of the week.", "billing@aws.com", "AWS Billing", Priority.NORMAL, Category.BILLING),
    ("email_03", "You won a free iPhone 15!", "Click here to claim your prize absolutely free, limited time offer.", "lottery@scam.to", "Lottery Winner", Priority.LOW, Category.SPAM),
    ("email_04", "Interested in Enterprise Plan", "We are a company of 5,000 employees looking to upgrade. Can we get a demo?", "procurement@mega.com", "Mega Corp", Priority.NORMAL, Category.INQUIRY),
    ("email_05", "Double charge on my credit card", "I was charged twice yesterday for my subscription. I need a refund ASAP, this overdrafts my account!", "angryuser@gmail.com", "Angry User", Priority.URGENT, Category.BILLING),
    ("email_06", "Login button not working on Safari", "Hey, I can't click the login button when using Safari on my Mac.", "user1@icloud.com", "Mac User", Priority.NORMAL, Category.SUPPORT),
    ("email_07", "Security vulnerability disclosure", "I have found a critical remote code execution vulnerability in your API. Details attached.", "hacker@whitehat.net", "Whitehat", Priority.URGENT, Category.SUPPORT),
    ("email_08", "SEO Services Guaranteed Page 1", "We can improve your Google ranking in 2 weeks. $100/month.", "seo@spamservice.bot", "SEO Spam", Priority.LOW, Category.SPAM),
    ("email_09", "Partnership opportunity", "I run a blog with 1M readers. Can we do an affiliate partnership?", "blogger@influence.com", "Influencer", Priority.LOW, Category.INQUIRY),
    ("email_10", "Cancel my account", "I want to cancel my account, your service is terrible. Do it now.", "churning@yahoo.com", "Churning User", Priority.NORMAL, Category.SUPPORT),
    ("email_11", "URGENT: Legal Notice", "CEASE AND DESIST: You are infringing on our patents. Please respond within 24 hours.", "lawyer@lawfirm.com", "Law Firm", Priority.URGENT, Category.INQUIRY),
    ("email_12", "Where is my receipt?", "I bought the pro plan last month but I can't find the receipt. Can you resend?", "user99@msn.com", "Old User", Priority.NORMAL, Category.BILLING),
    ("email_13", "Can't access data export", "I need to export my data for a quarterly report due tomorrow morning.", "analyst@finance.com", "Analyst", Priority.URGENT, Category.SUPPORT),
    ("email_14", "How much does it cost?", "Hi, what are your pricing plans for small teams of 3 people?", "smallbiz@biz.com", "Small Biz", Priority.LOW, Category.INQUIRY),
    ("email_15", "Make $5000 a day from home", "Learn my secret method today! Buy the course.", "guru@money.com", "Guru", Priority.LOW, Category.SPAM),
    ("email_16", "Incorrect tax amount on invoice #1042", "You charged me 20% VAT but I am exempt. Please correct this immediately.", "finance@eu.co", "EU Finance", Priority.URGENT, Category.BILLING),
    ("email_17", "Bug in analytics dashboard", "The numbers don't add up correctly since the new update.", "metrics@company.com", "Metrics Guy", Priority.NORMAL, Category.SUPPORT),
    ("email_18", "Extend trial period?", "Our trial expires tomorrow but our VP is on vacation. Can we get 1 more week?", "pm@tech.com", "Product Manager", Priority.LOW, Category.INQUIRY),
    ("email_19", "Payment failed notification", "Your payment for $50 could not be processed. Please update your card.", "stripe@stripe.com", "Stripe", Priority.URGENT, Category.BILLING),
    ("email_20", "Hot singles in your area", "Don't miss out on meeting new people.", "dating@spam.com", "Spam", Priority.LOW, Category.SPAM),
    ("email_21", "Student discount application", "I am a university student, do you offer educational pricing?", "student@edu.edu", "Student", Priority.LOW, Category.INQUIRY),
    ("email_22", "Password reset link not arriving", "I've requested a reset link 5 times and haven't received it.", "lockedout@gmail.com", "Locked Out", Priority.URGENT, Category.SUPPORT),
    ("email_23", "Updating billing address", "I need to change the company address on our next invoice.", "admin@startup.com", "Admin", Priority.NORMAL, Category.BILLING),
    ("email_24", "Invitation to speak at conference", "We would love someone from your team to do a keynote at TechCon 2026.", "events@techcon.org", "TechCon", Priority.NORMAL, Category.INQUIRY),
    ("email_25", "Your device is infected with malware", "I know all your secrets. Send Bitcoin or I will release the footage.", "extortion@scam.net", "Extortion", Priority.LOW, Category.SPAM),
    ("email_26", "Enterprise SLA terms?", "Do you offer a 99.99% SLA for enterprise tier?", "legal@bigcorp.com", "Big Corp Legal", Priority.NORMAL, Category.INQUIRY),
    ("email_27", "Accidental upgrade", "I accidentally clicked the upgrade button on the app, please reverse it!", "oops@gmail.com", "Oops User", Priority.NORMAL, Category.BILLING),
    ("email_28", "Custom domain setup not propagating", "I followed the guide but my custom domain still shows a 404 error after 48 hours.", "webmaster@domain.com", "Webmaster", Priority.NORMAL, Category.SUPPORT),
    ("email_29", "Account taking 10 seconds to load", "The platform is incredibly slow for us today.", "slow@slow.com", "Slow User", Priority.URGENT, Category.SUPPORT),
    ("email_30", "Cheap meds online no prescription", "Order now for instant delivery.", "meds@shady.ru", "Shady", Priority.LOW, Category.SPAM),
]

for idx, (id_, subject, body, from_email, sender, p, c) in enumerate(data):
    ts = (datetime.datetime(2026, 4, 1, 10, 0) + datetime.timedelta(hours=idx)).isoformat()
    EMAILS.append(Email(
        id=id_,
        subject=subject,
        body=body,
        from_email=from_email,
        sender=sender,
        timestamp=ts
    ))
    LABELS[id_] = Label(priority=p, category=c)
