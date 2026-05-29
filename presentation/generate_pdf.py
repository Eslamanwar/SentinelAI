#!/usr/bin/env python3
"""Generate SentinelAI hackathon presentation PDF."""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

W, H = LETTER  # 612 x 792

# Colors
BG = HexColor("#0a0a0a")
CARD_BG = HexColor("#141414")
WHITE = HexColor("#ededed")
GRAY = HexColor("#9ca3af")
BLUE = HexColor("#3b82f6")
ORANGE = HexColor("#f97316")
RED = HexColor("#ef4444")
GREEN = HexColor("#22c55e")
PURPLE = HexColor("#a855f7")
YELLOW = HexColor("#eab308")
DARK_BORDER = HexColor("#262626")


def draw_bg(c):
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)


def draw_text(c, x, y, text, size=14, color=WHITE, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, y, text)


def draw_centered(c, y, text, size=14, color=WHITE, font="Helvetica"):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawCentredString(W / 2, y, text)


def draw_card(c, x, y, w, h, border_color=DARK_BORDER):
    c.setFillColor(CARD_BG)
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)


def draw_bullet(c, x, y, text, size=13, color=WHITE, bullet_color=BLUE):
    c.setFillColor(bullet_color)
    c.circle(x + 4, y + 4, 3, fill=1, stroke=0)
    c.setFont("Helvetica", size)
    c.setFillColor(color)
    c.drawString(x + 16, y, text)


def draw_badge(c, x, y, text, bg_color, text_color=WHITE):
    tw = len(text) * 6 + 16
    c.setFillColor(bg_color)
    c.roundRect(x, y - 4, tw, 18, 4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 9)
    c.setFillColor(text_color)
    c.drawString(x + 8, y, text)
    return tw


# --- SLIDES ---

def slide_title(c):
    draw_bg(c)
    # Shield icon placeholder
    c.setFillColor(BLUE)
    c.circle(W / 2 - 90, H / 2 + 80, 24, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(WHITE)
    c.drawCentredString(W / 2 - 90, H / 2 + 73, "S")

    draw_text(c, W / 2 - 55, H / 2 + 68, "SentinelAI", size=42, font="Helvetica-Bold", color=WHITE)

    draw_centered(c, H / 2 + 30, "Autonomous Infrastructure Threat Intelligence Agent", size=16, color=GRAY)

    draw_centered(c, H / 2 - 20, "Bright Data AI Agents Web Data Hackathon", size=14, color=BLUE)
    draw_centered(c, H / 2 - 42, "Track 3: Security & Compliance", size=13, color=ORANGE)

    # Tech badges
    badges = [("LangGraph", BLUE), ("Claude Opus 4.6", ORANGE), ("Bright Data", GREEN), ("Kafka", PURPLE)]
    bx = 140
    for label, color in badges:
        tw = draw_badge(c, bx, H / 2 - 90, label, color)
        bx += tw + 10

    draw_centered(c, 60, "github.com/YOUR_USERNAME/sentinel-ai", size=11, color=GRAY)


def slide_problem(c):
    draw_bg(c)
    draw_centered(c, H - 80, "The Problem", size=32, font="Helvetica-Bold", color=RED)

    draw_card(c, 50, H - 380, W - 100, 260, RED)
    y = H - 150
    problems = [
        ("Kubernetes CVEs drop on the open web", "— no SIEM monitors them"),
        ("Credential leaks surface on paste sites", "— days before anyone notices"),
        ("Vendor breaches blindside companies", "— no continuous monitoring"),
        ("Regulatory changes slip through the cracks", "— manual tracking fails"),
        ("A human threat analyst takes DAYS per threat", "— most are never investigated"),
    ]
    for title, sub in problems:
        draw_bullet(c, 80, y, title, size=14, bullet_color=RED)
        draw_text(c, 96, y - 16, sub, size=11, color=GRAY)
        y -= 46

    draw_card(c, 50, 100, W - 100, 80, ORANGE)
    draw_centered(c, 150, "Two worlds that never connect:", size=16, font="Helvetica-Bold", color=ORANGE)
    draw_centered(c, 125, "The Open Web  ←→  Your Infrastructure", size=18, font="Helvetica-Bold", color=WHITE)


def slide_solution(c):
    draw_bg(c)
    draw_centered(c, H - 80, "The Solution", size=32, font="Helvetica-Bold", color=GREEN)

    draw_centered(c, H - 130, "SentinelAI bridges these worlds — autonomously.", size=17, color=WHITE)

    y = H - 180
    steps = [
        ("1. DISCOVER", "Scans the open web for CVEs, advisories, credential leaks, vendor breaches", BLUE),
        ("2. CORRELATE", "Matches threats against your actual K8s clusters, Terraform state, AWS resources", ORANGE),
        ("3. SCORE", "Calculates blast radius, exposure, and exploitability — not just CVSS", RED),
        ("4. REMEDIATE", "Generates exact kubectl, Terraform, and Helm commands to fix", GREEN),
        ("5. NOTIFY", "Sends Slack alerts and creates Jira tickets automatically", PURPLE),
    ]
    for title, desc, color in steps:
        draw_card(c, 50, y - 55, W - 100, 60, color)
        draw_text(c, 70, y - 15, title, size=15, font="Helvetica-Bold", color=color)
        draw_text(c, 70, y - 35, desc, size=11, color=GRAY)
        y -= 75

    draw_card(c, 50, 60, W - 100, 70, GREEN)
    draw_centered(c, 105, "\"Enter a company name. Watch AI agents investigate in real time.\"", size=14, font="Helvetica-Bold", color=GREEN)
    draw_centered(c, 80, "Zero config. One command. Full threat landscape.", size=12, color=GRAY)


def slide_architecture(c):
    draw_bg(c)
    draw_centered(c, H - 80, "Architecture", size=32, font="Helvetica-Bold", color=BLUE)

    # Bright Data layer
    draw_card(c, 50, H - 200, W - 100, 90, BLUE)
    draw_text(c, 70, H - 135, "Bright Data (Open Web)", size=14, font="Helvetica-Bold", color=BLUE)
    bd_tools = ["SERP API", "Web Unlocker", "Scraping Browser", "Web Scraper API"]
    bx = 80
    for tool in bd_tools:
        tw = draw_badge(c, bx, H - 165, tool, BLUE)
        bx += tw + 8

    # Agent layer
    draw_card(c, 50, H - 420, W - 100, 195, ORANGE)
    draw_text(c, 70, H - 235, "LangGraph Agent Pipeline", size=14, font="Helvetica-Bold", color=ORANGE)

    agents = [
        ("Orchestrator", GRAY, 70), ("Discovery", RED, 200), ("Credential Leak", ORANGE, 330), ("Vendor Risk", PURPLE, 460),
    ]
    for name, color, ax in agents:
        draw_badge(c, ax, H - 270, name, color)

    draw_centered(c, H - 310, "↓  merge results  ↓", size=11, color=GRAY)

    agents2 = [
        ("Correlation", YELLOW, 100), ("Risk Scoring", RED, 240), ("Remediation", GREEN, 370), ("Notify", PURPLE, 480),
    ]
    for name, color, ax in agents2:
        draw_badge(c, ax, H - 340, name, color)

    # Infrastructure layer
    draw_card(c, 50, H - 540, 240, 90, GREEN)
    draw_text(c, 70, H - 465, "Infrastructure", size=13, font="Helvetica-Bold", color=GREEN)
    draw_text(c, 70, H - 485, "Kafka  |  PostgreSQL  |  Docker", size=11, color=GRAY)
    draw_text(c, 70, H - 505, "Event Bus  Checkpoints  Containers", size=10, color=GRAY)

    # Output layer
    draw_card(c, 320, H - 540, 242, 90, PURPLE)
    draw_text(c, 340, H - 465, "Output", size=13, font="Helvetica-Bold", color=PURPLE)
    draw_text(c, 340, H - 485, "Dashboard  |  Slack  |  Jira", size=11, color=GRAY)
    draw_text(c, 340, H - 505, "Real-time SSE    Alerts    Tickets", size=10, color=GRAY)

    # LLM
    draw_card(c, 50, H - 630, W - 100, 60, ORANGE)
    draw_text(c, 70, H - 590, "Claude Opus 4.6 via LiteLLM", size=14, font="Helvetica-Bold", color=ORANGE)
    draw_text(c, 70, H - 610, "Autonomous reasoning with tool use — agents decide what to scrape and when", size=11, color=GRAY)


def slide_bright_data(c):
    draw_bg(c)
    draw_centered(c, H - 80, "Bright Data Integration", size=32, font="Helvetica-Bold", color=GREEN)
    draw_centered(c, H - 115, "All 5 tools used for distinct, critical purposes", size=14, color=GRAY)

    tools = [
        ("SERP API", "Searches Google for CVEs, breach news, vendor incidents, credential leaks, regulatory changes", BLUE),
        ("Web Unlocker", "Bypasses anti-bot on NVD, AWS bulletins, vendor portals, paste sites, regulatory websites", GREEN),
        ("Scraping Browser", "Navigates JS-heavy GitHub Security Advisories, AWS Health Dashboard, SaaS status pages", ORANGE),
        ("Web Scraper API", "Structured extraction from CVE databases, compliance registries — returns clean JSON", PURPLE),
        ("MCP Server", "Connects Claude directly to Bright Data — the agent autonomously decides what to scrape", RED),
    ]

    y = H - 170
    for name, desc, color in tools:
        draw_card(c, 50, y - 70, W - 100, 80, color)
        draw_text(c, 70, y - 15, name, size=16, font="Helvetica-Bold", color=color)
        draw_text(c, 70, y - 38, desc[:80], size=11, color=GRAY)
        if len(desc) > 80:
            draw_text(c, 70, y - 53, desc[80:], size=11, color=GRAY)
        y -= 95


def slide_demo(c):
    draw_bg(c)
    draw_centered(c, H - 80, "Demo Flow", size=32, font="Helvetica-Bold", color=PURPLE)
    draw_centered(c, H - 115, "3 minutes that win", size=14, color=GRAY)

    steps = [
        ("0:00", "Enter \"Acme Corp\"", "Agent starts, loads K8s + Terraform inventory", BLUE),
        ("0:30", "Discovery agents fan out", "3 parallel agents scan web via Bright Data", ORANGE),
        ("1:00", "First threats appear", "\"Found 5 CVEs affecting K8s 1.28.2\"", RED),
        ("1:30", "Correlation complete", "\"2 of 3 clusters run affected versions\"", YELLOW),
        ("2:00", "Risk scored", "\"85/100 — internet-facing, no network policies\"", RED),
        ("2:30", "Remediation generated", "\"kubectl upgrade + Terraform patch ready\"", GREEN),
        ("3:00", "Auto-notify", "Slack alert + Jira ticket created live", PURPLE),
    ]

    y = H - 170
    for time, title, desc, color in steps:
        draw_badge(c, 60, y, time, color)
        draw_text(c, 125, y, title, size=14, font="Helvetica-Bold", color=WHITE)
        draw_text(c, 125, y - 18, desc, size=11, color=GRAY)
        y -= 55

    draw_card(c, 50, 55, W - 100, 55, GREEN)
    draw_centered(c, 85, "The audience sees the full pipeline in 3 minutes.", size=14, font="Helvetica-Bold", color=GREEN)
    draw_centered(c, 65, "Pre-cached demo data ensures instant, reliable results.", size=11, color=GRAY)


def slide_tech_stack(c):
    draw_bg(c)
    draw_centered(c, H - 80, "Tech Stack", size=32, font="Helvetica-Bold", color=ORANGE)

    stack = [
        ("Docker + Docker Compose", "One command to launch the entire stack", BLUE),
        ("LangGraph", "Stateful graph-based multi-agent orchestration", ORANGE),
        ("Claude Opus 4.6 via LiteLLM", "Most capable reasoning model, unified API", ORANGE),
        ("FastAPI (Python)", "Async backend, SSE streaming", GREEN),
        ("Next.js 14 + Tailwind", "Real-time dashboard with live agent trace", BLUE),
        ("Kafka (Confluent 7.6)", "Event-driven pipeline, auditable event bus", PURPLE),
        ("PostgreSQL 16", "Threat history, LangGraph checkpoints", GREEN),
        ("Bright Data SDK (all 5 tools)", "Full open-web access with anti-bot bypass", GREEN),
        ("Slack SDK + Jira REST API", "Automated alerting and ticket creation", PURPLE),
    ]

    y = H - 140
    for name, desc, color in stack:
        draw_bullet(c, 60, y, "", bullet_color=color)
        draw_text(c, 80, y, name, size=13, font="Helvetica-Bold", color=WHITE)
        draw_text(c, 80, y - 17, desc, size=10, color=GRAY)
        y -= 45


def slide_why_we_win(c):
    draw_bg(c)
    draw_centered(c, H - 80, "Why SentinelAI Wins", size=32, font="Helvetica-Bold", color=YELLOW)

    reasons = [
        ("Novelty", "Not a generic LLM wrapper — infrastructure-aware AI that correlates web threats against YOUR environment", BLUE),
        ("Domain Expertise", "Built by someone who runs K8s, Terraform, and AWS in production — real SRE workflows", GREEN),
        ("Bright Data Integration", "All 5 tools used for distinct, critical web intelligence tasks", GREEN),
        ("Production Architecture", "Kafka event bus, Docker, environment parsers — this could ship today", ORANGE),
        ("Demo Impact", "CVE drops → agent finds it → checks clusters → generates fix → alerts Slack — in 3 minutes", RED),
        ("Real-World Value", "$15B+ threat intelligence market. Existing tools (Snyk, Wiz) cost $50K+/year", PURPLE),
    ]

    y = H - 150
    for title, desc, color in reasons:
        draw_card(c, 50, y - 60, W - 100, 70, color)
        draw_text(c, 70, y - 12, title, size=15, font="Helvetica-Bold", color=color)
        draw_text(c, 70, y - 32, desc[:85], size=10, color=GRAY)
        if len(desc) > 85:
            draw_text(c, 70, y - 45, desc[85:], size=10, color=GRAY)
        y -= 82


def slide_thank_you(c):
    draw_bg(c)

    c.setFillColor(BLUE)
    c.circle(W / 2 - 70, H / 2 + 80, 20, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(WHITE)
    c.drawCentredString(W / 2 - 70, H / 2 + 74, "S")
    draw_text(c, W / 2 - 42, H / 2 + 70, "SentinelAI", size=32, font="Helvetica-Bold", color=WHITE)

    draw_centered(c, H / 2 + 20, "Autonomous Infrastructure Threat Intelligence", size=16, color=GRAY)

    draw_centered(c, H / 2 - 40, "Try it: docker-compose up -d", size=18, font="Helvetica-Bold", color=GREEN)
    draw_centered(c, H / 2 - 65, "Open http://localhost:3000 and investigate.", size=13, color=GRAY)

    draw_centered(c, H / 2 - 130, "Built with", size=12, color=GRAY)
    badges = [("Bright Data", GREEN), ("LangGraph", ORANGE), ("Claude Opus 4.6", BLUE), ("Kafka", PURPLE), ("Docker", BLUE)]
    bx = 115
    for label, color in badges:
        tw = draw_badge(c, bx, H / 2 - 160, label, color)
        bx += tw + 8

    draw_centered(c, 80, "Thank you!", size=28, font="Helvetica-Bold", color=WHITE)


def main():
    output = "/Users/eslam.mohammed/eslam/eslam/ai-project/brightdata/SentinelAI/presentation/SentinelAI_Presentation.pdf"
    c = canvas.Canvas(output, pagesize=LETTER)
    c.setTitle("SentinelAI — Hackathon Presentation")

    slides = [
        slide_title,
        slide_problem,
        slide_solution,
        slide_architecture,
        slide_bright_data,
        slide_demo,
        slide_tech_stack,
        slide_why_we_win,
        slide_thank_you,
    ]

    for i, slide_fn in enumerate(slides):
        slide_fn(c)
        # Page number
        c.setFont("Helvetica", 8)
        c.setFillColor(GRAY)
        c.drawCentredString(W / 2, 25, f"{i + 1} / {len(slides)}")
        c.showPage()

    c.save()
    print(f"PDF saved: {output}")


if __name__ == "__main__":
    main()
