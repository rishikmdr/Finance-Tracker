"""AI engine — portfolio analysis, suggestions, and chatbot using Claude API."""
import json
import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_memory import ChatConversation, ChatMessage, UserMemory, MemoryCategory
from app.models.expense import Expense, Income
from app.models.holdings import (
    FixedHolding, GoldHolding, Liability, MFHolding, PropertyHolding, SIP, StockHolding,
)
from app.models.user import User

logger = logging.getLogger(__name__)


def _get_anthropic_client(api_key: str | None = None):
    """Get Anthropic client with user-provided or env key."""
    key = api_key or settings.ANTHROPIC_API_KEY
    if not key:
        return None
    try:
        import anthropic
        return anthropic.Anthropic(api_key=key)
    except ImportError:
        logger.warning("anthropic package not installed. pip install anthropic")
        return None


def _build_portfolio_context(db: Session, user_id: int) -> str:
    """Build a text summary of the user's full portfolio for AI context."""
    stocks = db.query(StockHolding).filter(StockHolding.user_id == user_id).all()
    mfs = db.query(MFHolding).filter(MFHolding.user_id == user_id).all()
    sips = db.query(SIP).filter(SIP.user_id == user_id, SIP.is_active == True).all()  # noqa
    fixed = db.query(FixedHolding).filter(FixedHolding.user_id == user_id).all()
    props = db.query(PropertyHolding).filter(PropertyHolding.user_id == user_id).all()
    gold = db.query(GoldHolding).filter(GoldHolding.user_id == user_id).all()
    liabilities = db.query(Liability).filter(Liability.user_id == user_id).all()

    # Recent income/expenses (last 3 months)
    three_months_ago = date(date.today().year, max(1, date.today().month - 3), 1)
    recent_income = db.query(Income).filter(
        Income.user_id == user_id, Income.date >= three_months_ago
    ).all()
    recent_expenses = db.query(Expense).filter(
        Expense.user_id == user_id, Expense.date >= three_months_ago
    ).all()

    total_income_3m = sum(float(i.amount) for i in recent_income)
    total_expense_3m = sum(float(e.amount) for e in recent_expenses)

    lines = ["=== PORTFOLIO SNAPSHOT ===", f"Date: {date.today()}"]

    # Stocks
    if stocks:
        stock_total = sum(float(s.quantity * s.avg_buy_price) for s in stocks)
        lines.append(f"\n## Stocks ({len(stocks)} holdings, invested: ₹{stock_total:,.0f})")
        by_type = {}
        for s in stocks:
            by_type.setdefault(s.investment_type.value, []).append(s)
        for typ, holdings in by_type.items():
            lines.append(f"  {typ}: {', '.join(f'{s.symbol} ({s.quantity} @ ₹{s.avg_buy_price})' for s in holdings)}")

    # Mutual Funds
    if mfs:
        mf_total = sum(float(m.units * m.avg_nav) for m in mfs)
        lines.append(f"\n## Mutual Funds ({len(mfs)} holdings, invested: ₹{mf_total:,.0f})")
        for m in mfs:
            lines.append(f"  {m.scheme_name} ({m.category or 'N/A'}): {m.units} units @ ₹{m.avg_nav} [{m.investment_mode.value}]")

    # SIPs
    if sips:
        monthly_sip = sum(float(s.amount) for s in sips)
        lines.append(f"\n## Active SIPs ({len(sips)}, monthly outflow: ₹{monthly_sip:,.0f})")
        for s in sips:
            lines.append(f"  {s.scheme_name}: ₹{s.amount}/mo on {s.day_of_month}th{' (step-up ' + str(s.step_up_percent) + '%/yr)' if s.step_up_percent else ''}")

    # Fixed Income
    if fixed:
        fixed_total = sum(float(f.current_value) for f in fixed)
        lines.append(f"\n## Fixed Income ({len(fixed)} holdings, value: ₹{fixed_total:,.0f})")
        for f in fixed:
            lines.append(f"  {f.type.value} {f.name or ''}: ₹{f.current_value:,.0f} @ {f.interest_rate}%{' (matures ' + str(f.maturity_date) + ')' if f.maturity_date else ''}")

    # Property
    if props:
        prop_total = sum(float(p.estimated_current_value) for p in props)
        lines.append(f"\n## Property ({len(props)}, total value: ₹{prop_total:,.0f})")
        for p in props:
            lines.append(f"  {p.name} ({p.type.value}): bought ₹{p.purchase_price:,.0f}, now ₹{p.estimated_current_value:,.0f}{' [SHARED]' if p.is_shared else ''}")

    # Gold
    if gold:
        gold_total = sum(float(g.purchase_price) for g in gold)
        lines.append(f"\n## Gold ({len(gold)} holdings, invested: ₹{gold_total:,.0f})")
        for g in gold:
            lines.append(f"  {g.type.value}: {g.quantity_grams}g @ ₹{g.purchase_price:,.0f}")

    # Liabilities
    if liabilities:
        liab_total = sum(float(l.outstanding) for l in liabilities)
        lines.append(f"\n## Liabilities ({len(liabilities)}, total outstanding: ₹{liab_total:,.0f})")
        for l in liabilities:
            lines.append(f"  {l.name} ({l.type.value}): ₹{l.outstanding:,.0f} @ {l.interest_rate}%{' EMI ₹' + str(l.emi_amount) if l.emi_amount else ''}")

    # Income/Expense summary
    lines.append(f"\n## Last 3 Months")
    lines.append(f"  Total Income: ₹{total_income_3m:,.0f}")
    lines.append(f"  Total Expenses: ₹{total_expense_3m:,.0f}")
    lines.append(f"  Net Savings: ₹{total_income_3m - total_expense_3m:,.0f}")
    if total_income_3m > 0:
        lines.append(f"  Savings Rate: {(total_income_3m - total_expense_3m) / total_income_3m * 100:.1f}%")

    # Totals
    stock_total = sum(float(s.quantity * s.avg_buy_price) for s in stocks) if stocks else 0
    mf_total = sum(float(m.units * m.avg_nav) for m in mfs) if mfs else 0
    fixed_total = sum(float(f.current_value) for f in fixed) if fixed else 0
    prop_total = sum(float(p.estimated_current_value) for p in props) if props else 0
    gold_total = sum(float(g.purchase_price) for g in gold) if gold else 0
    liab_total = sum(float(l.outstanding) for l in liabilities) if liabilities else 0

    total_assets = stock_total + mf_total + fixed_total + prop_total + gold_total
    net_worth = total_assets - liab_total

    lines.append(f"\n## Net Worth: ₹{net_worth:,.0f}")
    lines.append(f"  Total Assets: ₹{total_assets:,.0f}")
    lines.append(f"  Total Liabilities: ₹{liab_total:,.0f}")

    if total_assets > 0:
        lines.append(f"\n## Asset Allocation")
        lines.append(f"  Equity: {(stock_total + mf_total) / total_assets * 100:.1f}%")
        lines.append(f"  Fixed Income: {fixed_total / total_assets * 100:.1f}%")
        lines.append(f"  Real Estate: {prop_total / total_assets * 100:.1f}%")
        lines.append(f"  Gold: {gold_total / total_assets * 100:.1f}%")

    return "\n".join(lines)


def _get_user_memories(db: Session, user_id: int) -> str:
    """Get structured user memories."""
    memories = db.query(UserMemory).filter(UserMemory.user_id == user_id).all()
    if not memories:
        return ""
    lines = ["\n=== USER PROFILE (from past conversations) ==="]
    for m in memories:
        lines.append(f"  [{m.category.value}] {m.key}: {m.value}")
    return "\n".join(lines)


def analyze_portfolio(db: Session, user_id: int, api_key: str | None = None) -> dict:
    """Generate AI portfolio analysis — health score, good/bad, alerts, suggestions."""
    client = _get_anthropic_client(api_key)
    if not client:
        return {
            "health_score": None,
            "good": [],
            "bad": [],
            "alerts": [],
            "suggestions": [],
            "error": "No API key configured. Add your Anthropic API key in Settings.",
        }

    context = _build_portfolio_context(db, user_id)
    memories = _get_user_memories(db, user_id)

    if "## Net Worth: ₹0" in context and "## Stocks" not in context:
        return {
            "health_score": None,
            "good": [],
            "bad": [],
            "alerts": ["Add your holdings to get AI analysis"],
            "suggestions": ["Start by adding your stock and mutual fund holdings"],
            "error": None,
        }

    prompt = f"""You are a SEBI-registered investment advisor AI for an Indian investor.
Analyze this portfolio and return a JSON response with exactly these keys:

- "health_score": integer 0-100 (overall portfolio health)
- "good": list of 2-4 strings (what's good about this portfolio)
- "bad": list of 2-4 strings (risks, problems, concentration issues)
- "alerts": list of 1-3 strings (urgent items needing attention — FD maturity, low emergency fund, tax deadlines)
- "suggestions": list of 3-5 strings (specific actionable next steps — what to invest in, rebalancing moves, tax planning)

Consider: diversification, asset allocation for Indian investor, concentration risk, emergency fund adequacy, tax efficiency (Indian tax laws — LTCG, STCG, 80C), SIP consistency, debt-to-equity ratio, insurance gaps.

Return ONLY valid JSON, no markdown fences, no explanation.

{context}
{memories}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        text = response.content[0].text.strip()
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        result = json.loads(text)
        result["error"] = None
        return result
    except json.JSONDecodeError:
        return {
            "health_score": None, "good": [], "bad": [], "alerts": [],
            "suggestions": [], "error": "AI returned invalid response. Please try again.",
        }
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        return {
            "health_score": None, "good": [], "bad": [], "alerts": [],
            "suggestions": [], "error": f"AI analysis failed: {str(e)[:100]}",
        }


def chat(
    db: Session, user_id: int, message: str,
    conversation_id: int | None = None, api_key: str | None = None,
) -> dict:
    """Chat with AI financial advisor. Maintains conversation history and memory."""
    client = _get_anthropic_client(api_key)
    if not client:
        return {
            "reply": "Please add your Anthropic API key in Settings to use the AI advisor.",
            "conversation_id": conversation_id,
        }

    # Get or create conversation
    if conversation_id:
        conversation = db.query(ChatConversation).filter(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == user_id,
        ).first()
    else:
        conversation = None

    if not conversation:
        conversation = ChatConversation(
            user_id=user_id,
            title=message[:80] if message else "New conversation",
        )
        db.add(conversation)
        db.flush()

    # Save user message
    user_msg = ChatMessage(
        conversation_id=conversation.id, role="user", content=message,
    )
    db.add(user_msg)
    db.flush()

    # Build messages history
    history = (
        db.query(ChatMessage)
        .filter(ChatMessage.conversation_id == conversation.id)
        .order_by(ChatMessage.created_at)
        .all()
    )

    context = _build_portfolio_context(db, user_id)
    memories = _get_user_memories(db, user_id)

    system_prompt = f"""You are a highly knowledgeable personal financial advisor for an Indian investor.
You have complete access to their portfolio, income, expenses, and financial history.
You remember their goals, preferences, and past conversations.

IMPORTANT RULES:
- Give specific, actionable advice based on their actual numbers
- Reference specific holdings by name when relevant
- Use Indian financial context (80C, LTCG, STCG, NPS, PPF, ELSS, etc.)
- Format amounts in Indian notation (L for lakhs, Cr for crores)
- Be conversational but professional
- If asked about projections, show calculations
- Never recommend specific stocks/funds for buying — suggest categories and strategies
- Always caveat that you're an AI advisor, not a replacement for a certified financial planner

{context}
{memories}"""

    messages = []
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            system=system_prompt,
            messages=messages,
        )
        reply_text = response.content[0].text

        # Save assistant reply
        assistant_msg = ChatMessage(
            conversation_id=conversation.id, role="assistant", content=reply_text,
        )
        db.add(assistant_msg)

        # Extract and save memories from the conversation
        _extract_memories(db, user_id, message, reply_text, client)

        conversation.updated_at = datetime.now(timezone.utc)
        db.commit()

        return {
            "reply": reply_text,
            "conversation_id": conversation.id,
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Chat failed: {e}")
        return {
            "reply": f"Sorry, I encountered an error: {str(e)[:100]}. Please try again.",
            "conversation_id": conversation.id if conversation else None,
        }


def _extract_memories(db: Session, user_id: int, user_msg: str, ai_reply: str, client) -> None:
    """Auto-extract key facts from conversation and save to memory."""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""Extract any key personal financial facts from this conversation that should be remembered for future conversations. Return JSON array of objects with "key", "value", "category" (one of: goal, preference, fact, plan). Only extract clear, specific facts. Return empty array [] if nothing notable.

User said: {user_msg}
Advisor replied: {ai_reply[:500]}

Return ONLY valid JSON array, no fences.""",
            }],
        )
        text = response.content[0].text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        facts = json.loads(text)
        if not isinstance(facts, list):
            return

        for fact in facts[:5]:  # Max 5 facts per message
            key = fact.get("key", "")
            value = fact.get("value", "")
            category = fact.get("category", "fact")
            if not key or not value:
                continue
            if category not in ("goal", "preference", "fact", "plan"):
                category = "fact"

            # Upsert memory
            existing = db.query(UserMemory).filter(
                UserMemory.user_id == user_id, UserMemory.key == key,
            ).first()
            if existing:
                existing.value = value
                existing.category = MemoryCategory(category)
                existing.updated_at = datetime.now(timezone.utc)
            else:
                mem = UserMemory(
                    user_id=user_id, key=key, value=value,
                    category=MemoryCategory(category),
                )
                db.add(mem)
    except Exception as e:
        logger.debug(f"Memory extraction failed (non-critical): {e}")


def get_conversations(db: Session, user_id: int) -> list[dict]:
    """Get all conversations for a user."""
    convos = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.updated_at.desc())
        .limit(50)
        .all()
    )
    return [
        {"id": c.id, "title": c.title, "updated_at": c.updated_at.isoformat()}
        for c in convos
    ]


def get_conversation_messages(db: Session, user_id: int, conversation_id: int) -> list[dict]:
    """Get messages for a conversation."""
    convo = db.query(ChatConversation).filter(
        ChatConversation.id == conversation_id,
        ChatConversation.user_id == user_id,
    ).first()
    if not convo:
        return []
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in convo.messages
    ]
