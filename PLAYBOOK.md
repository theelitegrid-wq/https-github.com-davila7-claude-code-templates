# Sales Playbook: AI Services + Websites for Local Businesses

**Roles:** the tools find and rank leads and write the first message. **You** send, talk and close.
Claude builds what you sell (websites, chatbots) once a client says yes.

---

## 1. What you sell (3 packages)

Prices are starting points in USD. Adjust for your country: charge what a local business
makes from 1–2 new customers.

| Package | What they get | Setup | Monthly |
|---|---|---|---|
| **Starter Website** | 1–5 page mobile website, Google Maps/WhatsApp/call buttons, contact form, basic Google SEO | $500–900 | $50 hosting + small edits |
| **AI Assistant** | Chatbot on their website or WhatsApp that answers FAQs, prices and hours, and takes bookings 24/7 | $400–800 | $100–250 |
| **Growth Bundle** ⭐ | Website + AI assistant + automatic review requests to customers | $1,200–2,000 | $200–350 |

**Always sell a monthly fee.** Ten clients at $150/month is $1,500 a month you keep without new sales.
That's the "do less work" part.

**Who to target first (best → good):**
1. Busy businesses (**many good reviews**) with **no website** or only a Facebook page: easiest yes.
2. Businesses with old, broken or not-mobile websites.
3. Businesses with OK websites but no booking or chat: sell the AI Assistant.

Best niches: dentists, roofers, plumbers, HVAC, med spas, auto repair, law firms, salons.
They earn a lot per customer, so one missed customer costs them more than your price.

---

## 2. Daily routine (about 1–2 hours)

1. Open `data/leads_ranked.csv`. Start at the top.
2. Send **10–30** first messages from `data/messages.md`. Change a word or two so each sounds like you.
3. **Phone call is best** for local businesses. Email is second. Avoid mass WhatsApp blasts, which get your number banned.
4. In the `status` column write: `sent` → `replied` → `call booked` → `won` / `lost`.
5. Follow up with anyone who hasn't answered (section 4).

Rough numbers: 100 messages → 5–10 replies → 2–4 calls → 1–2 clients.

---

## 3. Phone script (60 seconds)

> Hi, is this the owner? My name is ___. I'll be quick. I was searching for a [dentist] near
> [area] and found you on Google Maps. You have great reviews, but I noticed [you don't have a website /
> your website doesn't work well on phones]. People who search on their phone usually call the next business.
>
> I help local businesses fix exactly that. I'd like to make you a **free sample** of your new
> site so you can see it before paying anything. Can I send it to you on WhatsApp or email?

If they say yes, tell Claude: *"Make a sample website for [business name], [category], [city], phone [x]."*
Send the link within 24 hours. **The free sample is what closes the deal.**

---

## 4. Follow-ups (most sales happen here)

**Day 3:**
> Hi [name], just checking you saw my message about [business]'s website. Happy to send the free
> sample. It takes me a day. Yes or no is fine.

**Day 7 (last one):**
> Hi [name], last message from me. If getting more customers from Google is ever a priority,
> just reply and I'll make the free sample. Wishing you a great month.

Stop after that. If they replied "no", never contact them again.

---

## 5. Closing call

1. **Ask before you pitch:** "How do most new customers find you now?" "What happens when you miss a call?"
2. **Show the sample** on their phone.
3. **Give the price as a choice, not a yes/no:** "Most clients pick the Growth Bundle at $X, or you can start with
   just the website at $Y. Which suits you?"
4. **Payment:** 50% upfront, 50% when it's live. The monthly fee starts at launch. Use Stripe, PayPal or bank transfer
   and a simple one-page agreement (ask Claude to write it).

### Objections

| They say | You say |
|---|---|
| "Too expensive" | "If it brings you 2 extra customers, has it paid for itself? We can start with just the website." |
| "I get customers from word of mouth" | "That's great. When people hear about you, they Google you first. Right now they find [nothing / a broken site]." |
| "My nephew does my website" | "No problem. Keep the sample as ideas. If you ever want it done this week, I'm here." |
| "Send me info" | "Sure. Better: I'll send the sample itself so you can see it. What's the best number?" |
| "Not now" | "Understood. Can I check back in a month?" Write the date in `notes`. |

---

## 6. After they pay

Tell Claude what you sold, for example: *"Build the Growth Bundle for Smile Dental: website + WhatsApp AI assistant
answering hours, prices and booking."* Claude builds it. You send it to the client for approval.

---

## 7. Rules that keep you safe

- Contact businesses, not private people. Send personal messages, **not spam**: 10–30 a day, each a little different.
- Always include an opt-out ("reply 'no' and I won't contact you again") and honour it.
- Email rules differ by country. US (CAN-SPAM) allows business cold email with your real name, address and opt-out.
  The EU/UK are stricter, so prefer phone calls there.
- Don't run the Google Maps scraper too often or too big, or Google may block your internet connection for a while.
- Keep `data/` private. It contains business phone numbers and emails.
