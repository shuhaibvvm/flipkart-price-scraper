import asyncio
from playwright.async_api import async_playwright
import pandas as pd
# step 1 scrape price and title

async def scrape_prices():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        await page.goto("https://www.flipkart.com/search?q=laptop", timeout=60000) 
        await page.wait_for_selector("div:has-text('Chromebook')") #Playwright pseudo-class extension
        
        #This XPath selector:
        titles = page.locator("//div[contains(text(),'Chromebook') or contains(text(),'Laptop') or contains(text(),'ASUS') or contains(text(),'Lenovo')]")
        prices = page.locator("//div[contains(text(),'₹')]")
        
        count = await titles.count()
        data = []
        
        for i in range(count):
            title = await titles.nth(i).text_content()
            price = await prices.nth(i).text_content()
            
            if title and price:
                data.append(
                    {
                        "title": title.strip(),
                        "price": price.strip().replace("₹","").replace(",","")
                    }
                )
        await browser.close()
        return pd.DataFrame(data)
    
    
# Step_2 Clean the Data

def clean_prices(df):
    df = df.copy()
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna()
    df = df[df['price'] > 1000] #Remove unwanted Noices
    return df


async def main():
    print("SCRAPING___STARTED_____")
    df_raw = await scrape_prices()
    
    print("CLEANING__DATA____")
    df_clean = clean_prices(df_raw)
    
    print("SAVING TO CSV")
    df_clean.to_csv("Flipkart_prices.csv", index= False)
    print(df_clean.head())
    
    

            
if __name__ == "__main__":
    asyncio.run(main())
