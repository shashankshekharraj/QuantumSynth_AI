import asyncio
from playwright.async_api import async_playwright
import sys
import os
from datetime import datetime

async def take_screenshot(label="event_capture"):
    """
    Simulates a human-like UI capture of the GCP JupyterLab interface.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"screenshot_{label}_{timestamp}.png"
    workspace_path = "/home/jupyter/quantum_agent"
    full_path = os.path.join(workspace_path, output_filename)
    
    async with async_playwright() as p:
        # Launch browser in headless mode but with human-like viewport
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()
        
        try:
            # We connect to the internal Jupyter proxy on port 8080
            # On Vertex AI, this usually serves the proxy content
            url = "http://localhost:8080"
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until="networkidle")
            
            # Wait for any dynamic elements to settle
            await asyncio.sleep(2)
            
            # Capture the entire UI as a human sees it
            await page.screenshot(path=full_path, full_page=True)
            print(f"SUCCESS: Screenshot saved to {full_path}")
            
        except Exception as e:
            print(f"ERROR: Playwright capture failed: {str(e)}")
        finally:
            await browser.close()
    
    return output_filename

if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "manual"
    asyncio.run(take_screenshot(label))
