# Rebuilds Pandian_Sambath_Resume_v2.docx exactly as finalised on 21 Nov 2026.
#   python resume/build_resume.py resume/Pandian_Sambath_Resume_v2.docx
# Then Word -> PDF (PowerShell):
#   $w=New-Object -ComObject Word.Application; $d=$w.Documents.Open("<abs>\Pandian_Sambath_Resume_v2.docx",$false,$true)
#   $d.SaveAs([ref]"<abs>\Pandian_Sambath_Resume_v2.pdf",[ref]17); $d.Close($false); $w.Quit()
# Then publish to the profile site:  python dev/scripts/publish_resume.py
# Keep it at 2 pages: check the PDF page count after every edit.

"""Build Pandian Sambath's resume as an ATS-safe .docx (single column, no tables/text boxes)."""
import sys
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Inches

OUT = sys.argv[1]
NAVY = RGBColor(0x1F, 0x3A, 0x68)
GREY = RGBColor(0x55, 0x55, 0x55)
FONT = "Calibri"
BODY = 10

doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.27), Inches(11.69)  # A4
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Inches(0.6))
sec.top_margin = sec.bottom_margin = Inches(0.5)
TEXT_WIDTH = sec.page_width - sec.left_margin - sec.right_margin

st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(BODY)
st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
st.paragraph_format.space_after = Pt(0)
st.paragraph_format.space_before = Pt(0)
st.paragraph_format.line_spacing = 1.0


def run(p, text, bold=False, italic=False, color=None, size=None):
    r = p.add_run(text)
    r.bold, r.italic = bold, italic
    if color is not None:
        r.font.color.rgb = color
    if size:
        r.font.size = Pt(size)
    return r


def para(space_before=0, space_after=0, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if align is not None:
        p.alignment = align
    return p


def bottom_border(p):
    pPr = p._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    b = OxmlElement("w:bottom")
    for k, v in (("w:val", "single"), ("w:sz", "8"), ("w:space", "1"), ("w:color", "1F3A68")):
        b.set(qn(k), v)
    bdr.append(b)
    pPr.append(bdr)


def heading(text):
    p = para(space_before=7, space_after=3)
    run(p, text.upper(), bold=True, color=NAVY, size=11)
    bottom_border(p)


def right_tab(p):
    p.paragraph_format.tab_stops.add_tab_stop(TEXT_WIDTH, WD_TAB_ALIGNMENT.RIGHT)


def line_with_date(left_parts, date, space_before=4):
    """left_parts: list of (text, bold, italic, color)."""
    p = para(space_before=space_before)
    right_tab(p)
    for text, b, i, c in left_parts:
        run(p, text, bold=b, italic=i, color=c)
    run(p, "\t" + date, color=GREY)
    return p


def bullet(label, text):
    p = doc.add_paragraph(style="List Bullet")
    pf = p.paragraph_format
    pf.left_indent = Inches(0.22)
    pf.first_line_indent = Inches(-0.16)
    pf.space_after = Pt(1.5)
    if label:
        run(p, label + ": ", bold=True)
    run(p, text)
    return p


def skill(label, text):
    p = para(space_after=1.5)
    run(p, label + ": ", bold=True)
    run(p, text)


def project(title, stack, date=None):
    p = para(space_before=4, space_after=1)
    right_tab(p)
    run(p, title, bold=True, color=NAVY)
    if date:
        run(p, "\t" + date, color=GREY)
    s = para(space_after=1.5)
    run(s, stack, italic=True, color=GREY, size=9.5)


def link(p, text, url):
    """Clickable hyperlink, styled like the surrounding grey contact text."""
    r_id = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                            is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "555555")
    rPr.append(c)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    p._p.append(h)


# ── Header ────────────────────────────────────────────────────────────────
p = para(align=WD_ALIGN_PARAGRAPH.CENTER)
run(p, "PANDIAN SAMBATH", bold=True, color=NAVY, size=20)
p = para(space_before=1, align=WD_ALIGN_PARAGRAPH.CENTER)
run(p, "System Engineer  |  Python · AWS · Generative AI", bold=True, size=11)
p = para(space_before=2, align=WD_ALIGN_PARAGRAPH.CENTER)
run(p, "Chennai, India  |  +91-8524827391  |  ", color=GREY)
link(p, "pandian.s.sambath@gmail.com", "mailto:pandian.s.sambath@gmail.com")
p = para(align=WD_ALIGN_PARAGRAPH.CENTER)
link(p, "linkedin.com/in/pandiansambath", "https://www.linkedin.com/in/pandiansambath")
run(p, "  |  ", color=GREY)
link(p, "github.com/pandiansambath", "https://github.com/pandiansambath")
run(p, "  |  ", color=GREY)
link(p, "pandi-dev.dineai.cloud", "https://pandi-dev.dineai.cloud/")


# Slightly tighter page so the fuller content fits on two pages at the same 10pt font.
sec.left_margin = sec.right_margin = Inches(0.5)
sec.top_margin = sec.bottom_margin = Inches(0.4)
TEXT_WIDTH = sec.page_width - sec.left_margin - sec.right_margin


def heading(text, note=None):
    p = para(space_before=3.5, space_after=2.5)
    p.paragraph_format.keep_with_next = True
    if note:
        right_tab(p)
    run(p, text.upper(), bold=True, color=NAVY, size=11)
    if note:
        run(p, "	" + note, color=GREY, size=9.5)
    bottom_border(p)


def bullet(label, text, highlight=()):
    """A bullet with an optional bold label; phrases in `highlight` are set in bold navy."""
    p = doc.add_paragraph(style="List Bullet")
    pf = p.paragraph_format
    pf.left_indent = Inches(0.22)
    pf.first_line_indent = Inches(-0.16)
    pf.space_after = Pt(0.3)
    if label:
        run(p, label + ": ", bold=True)
    rich(p, text, highlight)
    return p


def rich(p, text, highlight=()):
    """Write text, setting each phrase in `highlight` in bold navy."""
    while text:
        hits = [(text.find(h), h) for h in highlight if h in text]
        if not hits:
            run(p, text)
            return
        i, h = min(hits)
        if i:
            run(p, text[:i])
        run(p, h, bold=True, color=NAVY)
        text = text[i + len(h):]


def hlink(p, text, url, bold=False, size=None, underline=True):
    """Clickable link: navy and underlined, so it reads as a link on screen and in print."""
    r_id = p.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                            is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), r_id)
    r = OxmlElement("w:r")
    rPr = OxmlElement("w:rPr")
    if bold:
        rPr.append(OxmlElement("w:b"))
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "1F3A68")
    rPr.append(c)
    if size:
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), str(int(size * 2)))
        rPr.append(sz)
    if underline:
        u = OxmlElement("w:u")
        u.set(qn("w:val"), "single")
        rPr.append(u)
    r.append(rPr)
    t = OxmlElement("w:t")
    t.text = text
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    p._p.append(h)


def exp_title(title, date=None, url=None):
    p = para(space_before=5, space_after=1)
    p.paragraph_format.keep_with_next = True
    right_tab(p)
    run(p, title, bold=True, color=NAVY, size=10.5)
    if url:
        run(p, "  |  ", bold=True, color=NAVY, size=10.5)
        hlink(p, url, url, bold=True, size=10.5)
    if date:
        run(p, "\t" + date, color=GREY)


def oneliner(text, lead=None):
    p = para(space_after=1.5)
    p.paragraph_format.keep_with_next = True
    if lead:
        run(p, lead + " ", bold=True, color=NAVY)
    run(p, text, bold=True)


def labelled(label, text, space_before=0.5, highlight=()):
    p = para(space_before=space_before, space_after=0.5)
    run(p, label + ": ", bold=True)
    rich(p, text, highlight)


SITE = "https://dineai.cloud"
REPO = "https://github.com/pandiansambath/mise-erp"
# The official rank list, served by his profile site; #page=35 opens it at his name.
RANK_LIST = "https://pandi-dev.dineai.cloud/api/dev-site/RANK_AFF_UG_2023.pdf#page=35"

# ── Summary ───────────────────────────────────────────────────────────────
heading("Professional Summary")
p = para()


def say(text, highlight=False):
    run(p, text, bold=highlight, color=NAVY if highlight else None)


# His original paragraph, changed only where his feedback asked.
say("Software Development Engineer at Tata Consultancy Services with 3 years building production-grade, "
    "high-availability distributed systems on AWS for British Airways. Consolidated 50 redundant Lambda functions into "
    "1 shared Apache Camel ECS image (98% codebase reduction) — delivered before deadline as the youngest engineer on "
    "the team, working alongside senior and onsite colleagues — earning the ")
say("TCS Star of the Month", True)
say(" award. Designed a Python FastAPI service on AWS ECS serving as a major integration path from our ECS services "
    "to the legacy ")
say("FICO IBM TPF mainframe", True)
say(" over raw TCP sockets, with a custom binary protocol and TTL-based session management. Proposed and delivered a "
    "common base ECR image POC with immutable tagging, adopted by all Lambda functions. Strong focus on reliability "
    "and clean design patterns. Also built Orkestra (POC), an ")
say("AI SDLC", True)
say(" platform where AI agents on Amazon Bedrock work like a software team, from requirement to tested AWS deployment. "
    "Outside work, built and run DineAI (")
hlink(p, "dineai.cloud", SITE, bold=True, underline=False)
say("): a live, AI-powered restaurant management SaaS. Orkestra and DineAI were built with AI-assisted development "
    "(Claude Code). ")
say("Anna University Gold Medalist (17th rank, 92%). Cleared TCS Wings1 exams with Distinction, first attempt, "
    "and got promoted twice in 2 years: Ninja (3.36 LPA) → Digital (7 LPA) → Innovator (10 LPA).", True)

# ── Skills ────────────────────────────────────────────────────────────────
heading("Technical Skills")
skill("Languages", "Python – Intermediate  |  SQL  |  Java – AI-assisted")
skill("Generative AI", "Amazon Bedrock, Anthropic Claude (Opus, Sonnet, Haiku), Anthropic SDK, AI agents, multi-agent "
      "orchestration, MCP, RAG, vector databases, prompt engineering, tool use (function calling), human-in-the-loop "
      "approvals, LLM cost control")
skill("Backend", "FastAPI, Pydantic, Django REST Framework, Apache Camel, REST APIs, microservices, "
      "event-driven architecture")
skill("AWS", "EC2, ECS, ECR, Lambda, API Gateway, ALB, SQS, SNS, S3, RDS, DynamoDB, VPC, IAM (least privilege), "
      "Secrets Manager, SSM Parameter Store, EventBridge, CloudWatch, CloudTrail, CodeArtifact")
skill("Messaging & Integration", "IBM MQ, ActiveMQ, Apache Kafka, TCP/IP sockets, IBM TPF mainframe, "
      "custom binary protocols")
skill("DevOps & Tools", "Terraform, Docker, GitHub Actions CI/CD, SonarQube, Snyk, CodeScene, Git & GitHub, JIRA, Confluence")
skill("Databases & Testing", "PostgreSQL, DynamoDB, Supabase; Pytest, Playwright")
skill("Frontend (AI-assisted)", "Next.js, React, TypeScript, Tailwind CSS")
skill("AI Tools", "Claude Code, Claude for VS Code, OpenAI Codex, Google Antigravity, AWS Kiro")

# ── Experience ────────────────────────────────────────────────────────────
heading("Work Experience")
line_with_date([("Software Development Engineer", True, False, None),
                ("  |  Tata Consultancy Services (TCS), Chennai  —  Client: British Airways", False, False, None)],
               "Jan 2024 – Present", space_before=0)
doc.paragraphs[-1].paragraph_format.keep_with_next = True

exp_title("Hands-on Experience 1: Shared Apache Camel Message-Routing Service")
oneliner("One shared service that moves messages between IBM MQ, Kafka, ActiveMQ, SQS and S3, replacing 50 separate "
         "Lambda functions that all did the same receive-and-forward job.")
bullet("Problem", "each interface had its own transfer Lambda (IBM MQ → SQS, SQS → IBM MQ, IBM MQ → Kafka, Kafka → "
       "IBM MQ, Kafka → SQS, ActiveMQ → SQS, S3 → SQS, S3 events → MQ / Kafka), so 50 Lambdas repeated the same code.")
bullet("Solution", "designed one shared Apache Camel Docker image in a single ECR repository with 17 configurable "
       "routes for every pattern; each team runs its own ECS task from it and switches routes on or off with "
       "environment variables.")
bullet("Consolidation & impact", "moved the interfaces off their own transfer Lambdas onto the shared Camel routes: "
       "98% less duplicated code, per-interface setup cut from days to minutes, 50+ scheduled Lambda triggers replaced "
       "by always-on, event-driven ECS listeners for IBM MQ and ActiveMQ, ~40–50 ms end-to-end latency with all 17 "
       "routes enabled.")
labelled("Tech stack", "Apache Camel, Docker, Amazon ECR, Amazon ECS, IBM MQ, ActiveMQ, Apache Kafka, SQS, S3")
labelled("Recognition", "TCS Star of the Month award (Nov 2025) for this project, as the youngest engineer on the "
         "team, with 1.6 years of experience; recognised for reusable design and team mentorship.", space_before=0,
         highlight=("TCS Star of the Month", "youngest engineer on the team, with 1.6 years of experience"))

exp_title("Hands-on Experience 2: FICO-Access — IBM Mainframe Integration Gateway")
oneliner("A major integration path from our ECS services to the legacy FICO IBM TPF mainframe (Flight Information "
         "& Control Operations), used to read and write flight data.")
bullet("Binary + XML protocol over raw TCP", "built FICO-Access in Python FastAPI on AWS ECS; it talks to the "
       "mainframe using a 43-byte fixed-length binary header (TPF standard) plus an XML payload and no REST layer, for "
       "ultra-low latency.")
bullet("TTL-cached sessions", "signon → execute → signoff on one persistent connection; an in-memory TTL cache maps "
       "session ID → TCP socket, so there is no reconnection overhead and abandoned sessions are evicted before they "
       "leak sockets.")
bullet("Token pool (Python Lambda behind an ALB)", "the mainframe identifies callers by random 10-character tokens; "
       "the Lambda keeps a pool of them in DynamoDB and uses atomic conditional writes so two callers can never take "
       "the same token. Exposed /get-token, /release-token and /block-token APIs with per-application throttling.")
bullet("Infra & observability", "used the team's shared Terraform modules across Dev, SIT, Pre-Prod and Prod; "
       "CloudWatch logs and alerts for socket failures, mainframe timeouts and token-pool exhaustion; CI/CD via GitHub "
       "Actions.")
labelled("Tech stack", "Python, FastAPI, AWS ECS, ALB, Lambda, DynamoDB, TCP sockets, Terraform, CloudWatch, "
         "GitHub Actions")

exp_title("Hands-on Experience 3: Common Base Lambda Container Image (POC)")
oneliner("A shared Docker base image that every project Lambda builds from, so common setup lives in one place.")
bullet("Problem", "when the project moved Lambdas from ZIP to container deployment, each team built its own image, "
       "repeating the Python version, logger setup, utilities and package installs.")
bullet("POC & proposal", "designed and demonstrated a base ECR image with the standard Python version, a shared "
       "logger.py, utility modules and pre-installed packages; every Lambda Dockerfile starts FROM it, so an upgrade "
       "is one image change.")
bullet("Solved tag propagation", "immutable tags (timestamp + commit hash) meant editing every Lambda Dockerfile on "
       "each rebuild; stored the current tag in one shared repo and injected it as a Docker build ARG from GitHub "
       "Actions, so one change reaches every Lambda. Avoided a mutable 'latest' tag to keep builds reproducible, "
       "rollback-safe and auditable.")
bullet("Outcome", "accepted and handed to another engineer to maintain after the POC; all project Lambdas run on it.")
labelled("Tech stack", "Docker, Amazon ECR, AWS Lambda, GitHub Actions")

exp_title("Hands-on Experience 4: Orkestra — AI SDLC Platform (POC)")
oneliner("A team of AI agents that runs the full SDLC like a software team: each agent does one job and hands over to "
         "the next once a human approves, from requirement to tested AWS deployment.")
bullet("BA agent (Echo)", "share a requirement doc or plain text; it asks what's missing and writes the requirement "
       "document.")
bullet("Data Analyst agent (Atlas)", "builds the data mapping from the input and output samples.")
bullet("Architect agent (Archie)", "uses the earlier work to create the HLD, LLD and a draw.io architecture diagram.")
bullet("Platform agent (Terra)", "writes the Terraform scripts and deploys the infrastructure to AWS.")
bullet("Developer agent (Dev)", "writes the code and unit tests, deploys it and runs a first round of testing.")
bullet("QA agent (Quinn)", "tests the live flow and raises tickets; any agent can be assigned a ticket at any point.")
bullet("CTO agent (Orion)", "highest-privilege agent; orchestrates the crew, unblocks stuck agents and gives each "
       "agent its own least-privilege IAM role. Agents collaborate in a shared chat room; a Q&A agent (Sage) answers "
       "project questions.")
bullet("My role (AI-assisted build)", "concept, agent roles, workflow and AWS access model; the code was written with "
       "Claude Code, and I reviewed, tested and deployed it. Proven end to end on a real requirement for under $14 "
       "of AI cost.")
labelled("Tech stack", "Python, FastAPI, Amazon Bedrock (Claude Opus 5.5 for the CTO, BA and Architect agents; Claude "
         "Sonnet 5 for the rest), Anthropic SDK, Terraform, AWS IAM, Docker, React, TypeScript")

# ── Personal project ──────────────────────────────────────────────────────
heading("Personal Project")
exp_title("DineAI — AI-Powered Restaurant Management SaaS", "Jun 2026 – Present", url=SITE)
p = para(space_after=1.5)
p.paragraph_format.keep_with_next = True
run(p, "“Where does your money go?” ", bold=True, color=NAVY)
run(p, "A live web app that answers this for UK restaurants, with an AI assistant built in; currently used by "
       "Nirai, a restaurant in Reading, UK (", bold=True)
hlink(p, "https://niraireading.com", "https://niraireading.com/", bold=True)
run(p, ").", bold=True)
bullet("Product", "multi-tenant SaaS for purchasing and supplier price comparison, stock, recipe costing, live P&L, "
       "rota, attendance, payroll, sales, QR table ordering and documents.")
bullet("AI features", "a Claude assistant on Amazon Bedrock reads invoices, PDFs and spreadsheets into records once "
       "a person confirms, and answers business questions; Haiku or Sonnet by plan, AI quotas per restaurant; the "
       "AI only suggests.")
bullet("Landing page", "a premium, animated landing page designed and built with Claude Opus.")
bullet("Engineering", "modular FastAPI backend (25+ modules) on PostgreSQL (RDS) with custom roles; AWS built with "
       "Terraform (VPC, EC2, RDS, S3, IAM), Docker, GitHub Actions CI/CD with a test gate, CloudWatch; pytest and "
       "Playwright tests.")
bullet("My role (AI-assisted build)", "I own the product, the restaurant's requirements, design decisions, testing, "
       "deployment and AWS operations; the code is written with Claude Code and other AI coding tools.")
labelled("Tech stack", "Python, FastAPI, PostgreSQL, SQLAlchemy, Next.js, TypeScript, Bedrock (Claude), Terraform, "
         "GitHub Actions")
p = para(space_before=0, space_after=0.5)
run(p, "Code: ", bold=True)
hlink(p, REPO, REPO)

# ── Achievements ──────────────────────────────────────────────────────────
heading("Achievements & Certifications")
bullet("TCS Star of the Month (Nov 2025)", "merged 50 duplicate transfer Lambdas into one shared Apache Camel "
       "codebase.")
bullet("Beyond Performance Award (Oct 2024)", "among the top performers across the project team within 9 months of "
       "joining.")
bullet("TCS Wings1 Digital, Distinction (Jan 2025)", "all 3 exams on the first attempt (Articulation; Python & "
       "Django REST API with JWT; Data Analytics & ML on AWS SageMaker, EMR, Glue); promoted Ninja → Digital "
       "(System Engineer).")
bullet("TCS Wings1 Innovator, Distinction (Jan 2026)", "all 3 exams on the first attempt: an Advanced Django REST API "
       "coding challenge (higher-level test cases), then Business Skills and Process Assessment; promoted Digital → "
       "Innovator.")
bullet("TCS AI Hackathon", "certificate of participation; built an AI airline booking project.")
bullet("Crash Course on Python", "Google / Coursera (Jul 2023).")

# ── Education ─────────────────────────────────────────────────────────────
heading("Education & Languages")
line_with_date([("B.Tech, Information Technology", True, False, None),
                ("  |  Panimalar Institute of Technology (Anna University), Chennai", False, False, None)],
               "Graduated May 2023", space_before=0)
p = para()
right_tab(p)
run(p, "Anna University Gold Medalist — 17th Rank", bold=True, color=NAVY)
run(p, "  |  92%  |  ")
hlink(p, "Rank list (page 35)", RANK_LIST)
run(p, "	")
run(p, "Languages: ", bold=True)
run(p, "Tamil (native), English (professional)")

# ── Volunteering ──────────────────────────────────────────────────────────
heading("Volunteering", note="how I recharge outside work")
bullet("Thaagam Foundation NGO", "celebrated birthdays with orphanage children, served donor-funded meals "
       "every day (sharing each day's donors on Instagram), then fed stray dogs at Marina Beach in the evenings.")
bullet("TCS Maitree Kids Carnival", "volunteered at the games (chess, archery, dance, etc.) for TCS employees and "
       "their kids.")
bullet("TCS Hopes", "every Diwali, visit an orphanage to burst crackers and enjoy the day with the children.")


def no_break_hyphen(word):
    """Swap the hyphen in `word` for Word's own non-breaking hyphen, so the word never splits across lines."""
    import copy
    left, right = word.split("-", 1)
    for p in doc.paragraphs:
        for r in list(p.runs):
            if word not in r.text:
                continue
            before, after = r.text.split(word, 1)
            r.text = before + left
            hyph = copy.deepcopy(r._r)
            for t in hyph.findall(qn("w:t")):
                hyph.remove(t)
            hyph.append(OxmlElement("w:noBreakHyphen"))
            rest = copy.deepcopy(hyph)
            rest.remove(rest.find(qn("w:noBreakHyphen")))
            t = OxmlElement("w:t")
            t.text = right + after
            t.set(qn("xml:space"), "preserve")
            rest.append(t)
            r._r.addnext(hyph)
            hyph.addnext(rest)


no_break_hyphen("43-byte")

doc.core_properties.author = "Pandian Sambath"
doc.core_properties.title = "Pandian Sambath — Resume"
doc.save(OUT)
print("saved", OUT)
