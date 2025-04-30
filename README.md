# Cloudflare Bypass

**Bypass Cloudflare JS challenges and CAPTCHAs using Playwright in Python.**  
Retrieve `cf_clearance` cookies programmatically to automate access to protected web pages.

---

## 📦 Installation

Install dependencies:

```bash
pip install playwright
playwright install
```

---

## 🔧 Usage

You can use `Cloudflare Bypass` inside your own Python scripts or projects to automate the retrieval of the `cf_clearance` cookie from any Cloudflare-protected domain.

### ✅ Basic Example

```python
import asyncio
from cfbypass import CF_Solver

async def get_cookie():
    solver = CF_Solver(
        domain="https://example.com",
        headless=False,         # Set to True to run without UI
        slow_mo=100,            # Optional: adds delay between steps
        poll_interval=1.0,      # Check for cookies every second
        max_wait=90.0           # Wait up to 90 seconds
    )

    try:
        cf_cookie = await solver.bypass()
        print(f"cf_clearance: {cf_cookie}")
    finally:
        await solver.close()

# Run the async function
asyncio.run(get_cookie())
```

---

### 📚 Constructor Parameters

```python
CF_Solver(
    domain: str,               # Required. Target URL.
    user_agent: str = None,    # Optional. Custom user-agent string.
    headless: bool = False,    # Headless browser or visible.
    slow_mo: int = 50,         # Delay (ms) between actions (for realism).
    poll_interval: float = 1.0,# How often to check for cf_clearance.
    max_wait: float = 60.0     # Max total wait time for solving.
)
```

---

### 🔐 What It Returns

- Returns the `cf_clearance` cookie string if successful.
- Raises `Exception` if bypass fails, CAPTCHA appears in headless mode, or timeout occurs.

---

### 🤖 CAPTCHA Handling

- If a CAPTCHA is detected:
  - In **headless mode**: raises an error.
  - In **headful mode**: shows browser and prompts you to solve it manually.

---

## 🛠 Save and Use Cookies

Once you've obtained the `cf_clearance` value, attach it to future requests:

```python
import requests

cookies = {
    "cf_clearance": "your_cookie_here"
}

response = requests.get("https://example.com", cookies=cookies)
print(response.status_code)
```

---

## 📄 License

MIT License
