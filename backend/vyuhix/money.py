"""Indian-style money formatting. The copilot's grounding check relies on these exact strings."""


def group_indian(n: int) -> str:
    sign = "-" if n < 0 else ""
    s = str(abs(int(n)))
    if len(s) <= 3:
        return sign + s
    head, tail = s[:-3], s[-3:]
    parts = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return sign + ",".join(parts + [tail])


def inr(x: float) -> str:
    """₹3.42 Cr above one crore, ₹42.5 L above one lakh, else full Indian grouping."""
    x = float(x)
    if abs(x) >= 1e7:
        return f"₹{x / 1e7:.2f} Cr"
    if abs(x) >= 1e5:
        return f"₹{x / 1e5:.1f} L"
    return "₹" + group_indian(round(x))


def pct(x: float) -> str:
    return f"{x * 100:.0f}%"
