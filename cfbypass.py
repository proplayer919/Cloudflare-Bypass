import asyncio
import random
import time
from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


class CF_Solver:
    """
    Cloudflare Bypass Solver using Playwright for human-like browsing.
    Supports JS challenges (IUAM, BotFight) and manual CAPTCHA solving.
    Automatically polls for cf_clearance to handle heavy JS workloads.
    """

    def __init__(
        self,
        domain: str,
        user_agent: str = None,
        headless: bool = False,
        slow_mo: int = 50,
        poll_interval: float = 1.0,
        max_wait: float = 60.0,
    ):
        self.domain = domain.rstrip("/")
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/112.0.0.0 Safari/537.36"
        )
        self.headless = headless
        self.slow_mo = slow_mo
        self.poll_interval = poll_interval  # seconds
        self.max_wait = max_wait  # seconds
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        width = random.randint(1200, 1920)
        height = random.randint(700, 1080)
        self.context = await self.browser.new_context(
            user_agent=self.user_agent,
            viewport={"width": width, "height": height},
            locale="en-US",
            timezone_id="America/New_York",
        )
        self.page = await self.context.new_page()

    async def _prompt_manual_captcha(self):
        """
        When a CAPTCHA is detected, open a visible browser and prompt the user to solve it.
        """
        print(
            "CAPTCHA detected. Please solve it manually in the opened browser window."
        )
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, input, "After solving the CAPTCHA, press Enter here to continue...\n"
        )
        await asyncio.sleep(2)

    async def bypass(self, timeout: int = 0) -> str:
        """
        Perform the bypass and return cf_clearance cookie.
        If timeout > 0, overrides max_wait.
        Raises Exception on failure.
        """
        await self._init_browser()
        wait_deadline = time.time() + (timeout / 1000 if timeout else self.max_wait)

        try:
            # Start navigation (JS challenges may take longer than networkidle)
            await self.page.goto(
                self.domain,
                wait_until="domcontentloaded",
                timeout=timeout or int(self.max_wait * 1000),
            )
        except PlaywrightTimeoutError:
            # allow polling for clearance even if initial load timed out
            print(
                "Warning: initial navigation timed out, continuing to poll for clearance cookie."
            )

        # Poll for cf_clearance or CAPTCHA
        while time.time() < wait_deadline:
            # check cookies
            cookies = await self.context.cookies(self.domain)
            for ck in cookies:
                if ck.get("name") == "cf_clearance":
                    return ck.get("value")

            # detect CAPTCHA
            content = await self.page.content()
            if "captcha" in content.lower():
                if self.headless:
                    raise Exception(
                        "CAPTCHA encountered in headless mode. Use headless=False for manual solve."
                    )
                await self._prompt_manual_captcha()
                # after manual solving, continue polling

            await asyncio.sleep(self.poll_interval)

        raise Exception(
            "Timed out waiting for cf_clearance cookie. Challenge may be too heavy."
        )

    async def close(self):
        """
        Close browser and Playwright.
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Example usage
if __name__ == "__main__":
    import sys

    domain = sys.argv[1] if len(sys.argv) > 1 else "https://discord.com"
    solver = CF_Solver(
        domain, headless=True, slow_mo=100, poll_interval=1.0, max_wait=90.0
    )
    try:
        cf = asyncio.run(solver.bypass())
        print(f"{cf}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        asyncio.run(solver.close())
